from typing import Optional, Dict, Any, List
import asyncpg

async def insert_message(pool: asyncpg.Pool, conversation_id: int, role: str, content: str) -> int:
    sql = """
    INSERT INTO messages (conversation_id, role, content)
    VALUES ($1, $2, $3)
    RETURNING id;
    """
    async with pool.acquire() as conn:
        msg_id = await conn.fetchval(sql, conversation_id, role, content)
        return int(msg_id)

async def get_last_n_rounds(pool: asyncpg.Pool, conversation_id: int, rounds: int) -> List[Dict[str, Any]]:
    # 1 轮 = 用户 + 助手 = 2 条，因此 recent rounds = 2 * rounds
    limit_rows = max(2, rounds * 2)
    sql = """
    SELECT id, conversation_id, role, content, created_at
    FROM messages
    WHERE conversation_id=$1
    ORDER BY id DESC
    LIMIT $2;
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, conversation_id, limit_rows)
        return [dict(r) for r in reversed(rows)]  # 升序返回
        
async def count_by_conversation(pool: asyncpg.Pool, conversation_id: int) -> int:
    sql = "SELECT COUNT(*) FROM messages WHERE conversation_id=$1;"
    async with pool.acquire() as conn:
        return int(await conn.fetchval(sql, conversation_id))


async def get_all_except_last(pool: asyncpg.Pool, conversation_id: int, last_n: int) -> List[Dict[str, Any]]:
    """
    取除去最后 last_n 条之外的历史（用于摘要）。注意：last_n=最近N条消息（不是N轮）。
    """
    # 先查总数
    total = await count_by_conversation(pool, conversation_id)
    cut = max(0, total - last_n)
    if cut <= 0:
        return []

    sql = """
    SELECT id, conversation_id, role, content, created_at
    FROM messages
    WHERE conversation_id=$1
    ORDER BY id ASC
    LIMIT $2;
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, conversation_id, cut)
        return [dict(r) for r in rows]


async def get_by_conversation(
    pool: asyncpg.Pool,
    conversation_id: int,
    *,
    skip: int = 0,
    limit: int = 20,
    asc: bool = True,
) -> List[Dict[str, Any]]:
    order = "ASC" if asc else "DESC"
    sql = f"""
    SELECT id, conversation_id, role, content, created_at
    FROM messages
    WHERE conversation_id=$1
    ORDER BY id {order}
    OFFSET $2 LIMIT $3;
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, conversation_id, skip, limit)
        return [dict(r) for r in rows]


async def get_all_by_conversation(
    pool: asyncpg.Pool,
    conversation_id: int,
    *,
    asc: bool = True,
) -> List[Dict[str, Any]]:
    order = "ASC" if asc else "DESC"
    sql = f"""
    SELECT id, conversation_id, role, content, created_at
    FROM messages
    WHERE conversation_id=$1
    ORDER BY id {order};
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, conversation_id)
        return [dict(r) for r in rows]
