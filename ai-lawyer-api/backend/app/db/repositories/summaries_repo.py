import asyncpg
from typing import Optional, Dict, Any

async def get_by_conversation(pool: asyncpg.Pool, conversation_id: int) -> Optional[Dict[str, Any]]:
    sql = """
    SELECT conversation_id, summary, updated_at
    FROM conversation_summaries
    WHERE conversation_id=$1;
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, conversation_id)
        return dict(row) if row else None

async def upsert(pool: asyncpg.Pool, conversation_id: int, summary: str) -> None:
    sql = """
    INSERT INTO conversation_summaries (conversation_id, summary)
    VALUES ($1, $2)
    ON CONFLICT (conversation_id)
    DO UPDATE SET summary=EXCLUDED.summary, updated_at=NOW();
    """
    async with pool.acquire() as conn:
        await conn.execute(sql, conversation_id, summary)
