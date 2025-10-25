import asyncpg
from typing import Optional
from ..config import Settings

settings = Settings()

_pg_pool: Optional[asyncpg.Pool] = None

async def init_pg_pool() -> asyncpg.Pool:
    global _pg_pool
    if _pg_pool is None:
        _pg_pool = await asyncpg.create_pool(
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB,
            host=settings.POSTGRES_HOST,
            port=int(settings.POSTGRES_PORT),
            min_size=2,
            max_size=20,
            command_timeout=60,
        )
    return _pg_pool

async def get_pg_pool() -> asyncpg.Pool:
    if _pg_pool is None:
        return await init_pg_pool()
    return _pg_pool

async def close_pg_pool():
    global _pg_pool
    if _pg_pool is not None:
        await _pg_pool.close()
        _pg_pool = None
