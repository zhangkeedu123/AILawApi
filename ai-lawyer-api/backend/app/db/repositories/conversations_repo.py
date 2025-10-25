from typing import Optional, Dict, Any, List
import asyncpg

async def get_active_by_user(pool: asyncpg.Pool, user_id: str) -> Optional[Dict[str, Any]]:
    sql = """
    SELECT id, user_id, title, is_active, created_at, updated_at
    FROM conversations
    WHERE user_id=$1 AND is_active=TRUE
    ORDER BY id DESC
    LIMIT 1;
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, user_id)
        return dict(row) if row else None

async def create(pool: asyncpg.Pool, user_id: str, title: Optional[str] = None) -> Dict[str, Any]:
    sql = """
    INSERT INTO conversations (user_id, title, is_active)
    VALUES ($1, $2, TRUE)
    RETURNING id, user_id, title, is_active, created_at, updated_at;
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, user_id, title)
        return dict(row)

async def deactivate(pool: asyncpg.Pool, conversation_id: int) -> None:
    sql = "UPDATE conversations SET is_active=FALSE WHERE id=$1;"
    async with pool.acquire() as conn:
        await conn.execute(sql, conversation_id)
