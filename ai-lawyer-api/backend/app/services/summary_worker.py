# backend/app/services/summary_worker.py
from typing import List, Dict
from ..db.db import get_pg_pool
from ..db.repositories import messages_repo, summaries_repo
from ..core.ai_client import qwen_client
from ..config import Settings

settings = Settings()

def _estimate_tokens(messages: List[Dict]) -> int:
    """粗略估算 token：约 1 token ≈ 4 字符。用于必要的截断保护。"""
    text = "\n".join(m["content"] for m in messages)
    return max(1, len(text) // 4)

def _join(messages: List[Dict]) -> str:
    return "\n".join(f"{m['role']}: {m['content']}" for m in messages)

async def recompute_summary(conversation_id: int):
    """
    异步重算摘要（不阻塞主链路）：
    1) 取“除最近 N 轮”之外的旧消息
    2) 用 LLM 压缩成简洁摘要
    3) 覆盖写入 conversation_summaries（只保留一条）
    """
    pool = await get_pg_pool()

    # 最近 N 轮保留原文：每轮2条（user + assistant）
    keep_last_msgs = max(2, settings.recent_rounds * 2)

    older_msgs_db = await messages_repo.get_all_except_last(pool, conversation_id, keep_last_msgs)
    # 没有可摘要的历史：清空摘要（保持单条记录的正确性）
    if not older_msgs_db:
        await summaries_repo.upsert(pool, conversation_id, "")
        return

    older_msgs = [{"role": m["role"], "content": m["content"]} for m in older_msgs_db]

    # 简单截断保护：避免一次性丢给模型超大上下文（根据 max_context_tokens 动态裁剪）
    # 仅裁剪“旧历史”摘要输入，不动最近N轮（最近N轮不在这里参与）
    # 粗略估算：保留至不超过 0.9 * max_context_tokens，给系统提示留余量
    budget_tokens = int(settings.max_context_tokens * 0.9)
    if _estimate_tokens(older_msgs) > budget_tokens:
        # 从头开始合并直到达标
        trimmed: List[Dict] = []
        running = 0
        for m in older_msgs:
            t = max(1, len(m["content"]) // 4)
            if running + t > budget_tokens:
                break
            trimmed.append(m)
            running += t
        older_msgs = trimmed if trimmed else older_msgs[:1]  # 至少保留一点上下文

    prompt = [
        {
            "role": "system",
            "content": (
                "请将以下较早的对话历史压缩为**简洁的中文摘要**，用于后续上下文衔接：\n"
                "1) 保留关键事实、用户目标、限制条件与已达成结论\n"
                "2) 不要重复问候语\n"
                "3) 尽量短小（优先信息密度）"
            ),
        },
        {"role": "user", "content": _join(older_msgs)},
    ]

    summary_text = await qwen_client.chat(prompt)
    await summaries_repo.upsert(pool, conversation_id, summary_text.strip())
