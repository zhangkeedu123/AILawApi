import asyncio
from typing import List, Dict

from ..db.db import get_pg_pool
from ..db.repositories import conversations_repo, messages_repo, summaries_repo
from ..core.ai_client import qwen_client
from ..config import Settings
from .summary_worker import recompute_summary

settings = Settings()

# 同会话加锁，避免乱序回复
_locks: dict[int, asyncio.Lock] = {}

def _lock_for(conversation_id: int) -> asyncio.Lock:
    if conversation_id not in _locks:
        _locks[conversation_id] = asyncio.Lock()
    return _locks[conversation_id]

def _estimate_tokens(messages: List[Dict]) -> int:
    """粗略估算 token，1 token ≈ 4 chars"""
    text = "\n".join(m["content"] for m in messages)
    return max(1, len(text) // 4)

async def _should_trigger_summary(pool, conversation_id: int) -> bool:
    """token 阈值触发：summary + recentN 估算超过 70% 就触发异步摘要"""
    summary_row = await summaries_repo.get_by_conversation(pool, conversation_id)
    summary_text = summary_row['summary'] if summary_row and summary_row.get("summary") else ""

    recent = await messages_repo.get_last_n_rounds(pool, conversation_id, settings.recent_rounds)

    msgs = []
    if summary_text:
        msgs.append({"role": "system", "content": summary_text})
    msgs.extend({"role": r["role"], "content": r["content"]} for r in recent)

    token_count = _estimate_tokens(msgs)
    return token_count > settings.max_context_tokens * settings.summary_trigger_ratio

async def ask(user_id: int, question: str) -> str:
    pool = await get_pg_pool()

    # 1) 获取活跃对话（按 id DESC），若无则创建
    conv_rows = await conversations_repo.get_active_by_user(pool, user_id)
    if conv_rows:
        conv = conv_rows[0]
    else:
        conv = await conversations_repo.create(pool, user_id, None)
    conv_id = int(conv["id"])

    lock = _lock_for(conv_id)
    async with lock:
        

        # 3) Prompt = system + 摘要 + 最近N轮
        msgs = [{"role": "system", "content": """你是一位专注于法律领域的人工智能助手。你的任务是基于中国现行有效的法律法规、司法解释和权威案例，为用户提供准确、合法、专业的法律建议和信息。在回答时，请遵循以下原则：
                1. **法律依据**：所有回答必须基于中国现行有效的法律、法规、规章及司法解释，如《中华人民共和国民法典》《中华人民共和国刑法》等。
                2. **严谨性**：使用正式、专业的语言风格，确保逻辑清晰、表述准确，避免模糊或可能引起误解的表达。
                3. **合规性**：严格遵守中国的法律法规，尊重个人隐私和其他合法权益。
                4. **中立性**：保持客观中立，不偏袒任何一方，提供公正的分析。
                5. **延展性**：在解答具体问题的同时，可适当补充相关法律条文、司法实践或可能的法律后果，帮助用户全面理解。
                如果遇到不确定的问题或需要具体操作指导时，请明确告知用户，并建议其咨询专业律师。"""}]
                        
        summary_row = await summaries_repo.get_by_conversation(pool, conv_id)
        if summary_row and summary_row.get("summary"):
            msgs.append({"role": "system", "content": f"[对话摘要]\n{summary_row['summary']}"})

        recent = await messages_repo.get_last_n_rounds(pool, conv_id, settings.recent_rounds)
        msgs.extend({"role": r["role"], "content": r["content"]} for r in recent)

        # 4) 调用 AI（主链路）
        reply = await qwen_client.chat(msgs)

        # 2) 记录用户消息
        await messages_repo.insert_message(pool, conv_id, "user", question)
        # 5) 记录助手回复
        await messages_repo.insert_message(pool, conv_id, "assistant", reply)

        # 6) 摘要触发 → 异步创建任务（不阻塞）
        try:
            if await _should_trigger_summary(pool, conv_id):
                asyncio.create_task(recompute_summary(conv_id))
        except Exception:
            pass

        return reply
