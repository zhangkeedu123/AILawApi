import asyncio
from ..db.db import get_pg_pool
from ..db.repositories import conversations_repo, messages_repo
from ..core.memory_manager import memory_manager
from ..core.ai_client import qwen_client
from ..config import Settings

settings = Settings()

# 同一会话并发保护（避免同会话乱序）
_locks: dict[int, asyncio.Lock] = {}

def _lock_for(conversation_id: int) -> asyncio.Lock:
    if conversation_id not in _locks:
        _locks[conversation_id] = asyncio.Lock()
    return _locks[conversation_id]

async def ask(user_id: str, question: str) -> str:
    pool = await get_pg_pool()

    # 1) 找/建活跃会话
    conv = await conversations_repo.get_active_by_user(pool, user_id)
    if not conv:
        conv = await conversations_repo.create(pool, user_id, None)
    conv_id = int(conv["id"])

    lock = _lock_for(conv_id)
    async with lock:
        # 2) 记录用户消息（永久存库）
        await messages_repo.insert_message(pool, conv_id, "user", question)

        # 3) 取最近10轮（不删历史）
        recent = await messages_repo.get_last_n_rounds(pool, conv_id, settings.recent_rounds)
        recent_msgs = [{"role": r["role"], "content": r["content"]} for r in recent]

        # 4) 先拼上已有摘要
        context: list[dict] = [{"role": "system", "content": "You are a helpful assistant."}]
        cached_summary = memory_manager.get_summary(conv_id)
        if cached_summary:
            context.append({"role": "system", "content": f"[对话摘要]\n{cached_summary}"})
        context.extend(recent_msgs)

        # 5) 判断是否触发滚动摘要
        summary_text, compact_msgs, summarized = await memory_manager.summarize_if_needed(conv_id, context)

        # 6) 最终提示（system + [summary] + compact_msgs）
        final_msgs: list[dict] = [{"role": "system", "content": "You are a helpful assistant."}]
        if summary_text:
            final_msgs.append({"role": "system", "content": f"[对话摘要]\n{summary_text}"})
        final_msgs.extend([m for m in compact_msgs if m["role"] != "system"])

        # 7) 调用 Qwen
        reply = await qwen_client.chat(final_msgs)

        # 8) 写入助手消息
        await messages_repo.insert_message(pool, conv_id, "assistant", reply)

        # 9) 达到T1提醒
        if memory_manager.should_remind_new_conversation(conv_id):
            reply += "\n\n（提示：对话已很长并进行了多次压缩，建议新建会话以获得更清晰的上下文。）"

        return reply
