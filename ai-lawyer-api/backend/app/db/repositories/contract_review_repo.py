from typing import Dict, Any
import asyncpg

# Placeholder for potential future use (referenced by SQL files), not used by routers/services now.
TABLE = "contract_review"

async def delete_by_contract(pool: asyncpg.Pool, contract_id: int) -> int:
    sql = f"DELETE FROM {TABLE} WHERE contract_id=$1;"
    async with pool.acquire() as conn:
        res = await conn.execute(sql, contract_id)
        # returns 'DELETE <n>'
        return int(res.split(" ")[1]) if " " in res else 0

