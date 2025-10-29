import asyncio
from typing import List, Dict, Optional, Tuple

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
    """粗略估算 token 数：约4字符≈1 token"""
    text = "\n".join(m["content"] for m in messages)
    return max(1, len(text) // 4)


async def _should_trigger_summary(pool, conversation_id: int) -> bool:
    """token 阈值触发：summary + recentN 估算超过阈值则触发异步摘要"""
    summary_row = await summaries_repo.get_by_conversation(pool, conversation_id)
    summary_text = summary_row['summary'] if summary_row and summary_row.get("summary") else ""

    recent = await messages_repo.get_last_n_rounds(pool, conversation_id, settings.recent_rounds)

    msgs: List[Dict] = []
    if summary_text:
        msgs.append({"role": "system", "content": summary_text})
    msgs.extend({"role": r["role"], "content": r["content"]} for r in recent)

    token_count = _estimate_tokens(msgs)
    return token_count > settings.max_context_tokens * settings.summary_trigger_ratio


# 组装系统提示词
def _system_text() -> str:
    return (
        "你是一位专注于法律领域的人工智能助手。你的任务是基于中国现行有效的法律法规、司法解释和权威案例，为用户提供准确、合法、专业的法律建议和信息。在回答时，请遵循以下原则：\n"
        "1. 法律依据：所有回答必须基于中国现行有效的法律、法规、规章及司法解释，如《中华人民共和国民法典》《中华人民共和国刑法》等；\n"
        "2. 严谨性：使用正式、专业的语言风格，确保逻辑清晰、表述准确，避免模糊或可能引起误解的表达；\n"
        "3. 合规性：严格遵守中国的法律法规，尊重个人隐私和其他合法权益；\n"
        "4. 中立性：保持客观中立，不偏袒任何一方，提供公正的分析；\n"
        "5. 延展性：在解答具体问题的同时，可适当补充相关法律条文、司法实践或可能的法律后果，帮助用户全面理解；\n"
        "如遇不确定问题或需具体操作指导时，请明确告知用户，并建议其咨询专业律师。"
    )


# 统一组装对话消息：系统 +（可选摘要+最近N轮）+ 当前问题
async def _compose_msgs(pool, conv_id: int, question: str) -> List[Dict]:
    msgs: List[Dict] = [{"role": "system", "content": _system_text()}]
    if conv_id:
        summary_row = await summaries_repo.get_by_conversation(pool, conv_id)
        if summary_row and summary_row.get("summary"):
            msgs.append({"role": "system", "content": f"[对话摘要]\n{summary_row['summary']}"})
        recent = await messages_repo.get_last_n_rounds(pool, conv_id, settings.recent_rounds)
        msgs.extend({"role": r["role"], "content": r["content"]} for r in recent)
    # 加入本次用户问题
    msgs.append({"role": "user", "content": question})
    return msgs


#
# 功能：对话问答主方法。
# 参数：
#   - user_id: 用户ID。
#   - question: 用户本次提问内容。
#   - conv_id: 会话ID，默认0。
#       = 0  时：不加载任何历史或摘要，先调用AI得到回复，随后新建会话（标题取问题前10个字符），
#                再依次写入用户消息与AI回复；
#       != 0 时：保持当前逻辑，基于该会话加载摘要与最近N轮消息，调用AI，然后记录消息并按阈值异步触发摘要。
# 说明：仅在已有会话场景下对该会话加锁，避免乱序回复。
async def ask(user_id: int, question: str, conv_id: int = 0) -> Tuple[str, int, Optional[str]]:
    pool = await get_pg_pool()

    # 分支一：conv_id == 0，新开对话（不加载历史/摘要）
    if not conv_id:
        msgs = await _compose_msgs(pool, 0, question)
        # 调用 AI 获取回复（仅系统提示 + 当前问题）
        reply = await qwen_client.chat(msgs)

        # 生成标题（截取前10个字符）并创建会话
        title = (question or "").strip()[:10] or "请创建标题"
        conv = await conversations_repo.create(pool, user_id, title)
        new_conv_id = int(conv["id"])

        # 依次创建用户消息与AI回复
        await messages_repo.insert_message(pool, new_conv_id, "user", question)
        await messages_repo.insert_message(pool, new_conv_id, "assistant", reply)

        # 按需触发摘要（通常单轮不会触发）
        try:
            if await _should_trigger_summary(pool, new_conv_id):
                asyncio.create_task(recompute_summary(new_conv_id))
        except Exception:
            pass

        return reply, new_conv_id, title

    # 分支二：conv_id != 0，保留现有逻辑（加载摘要与最近N轮），并加入当前问题
    lock = _lock_for(conv_id)
    async with lock:
        # Prompt = system + 摘要 + 最近N轮 + 当前问题
        msgs = await _compose_msgs(pool, conv_id, question)
        reply = await qwen_client.chat(msgs)

        # 记录用户消息与助手回复
        await messages_repo.insert_message(pool, conv_id, "user", question)
        await messages_repo.insert_message(pool, conv_id, "assistant", reply)

        # 按阈值异步触发摘要
        try:
            if await _should_trigger_summary(pool, conv_id):
                asyncio.create_task(recompute_summary(conv_id))
        except Exception:
            pass

        return reply, 0, None
