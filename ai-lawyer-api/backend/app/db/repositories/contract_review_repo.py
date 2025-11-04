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

async def insert_many(pool: asyncpg.Pool, rows: list[dict]) -> int:
    if not rows:
        return 0
    cols = [
        "contract_id","title","risk_level","position","method","risk_clause",
        "result_type","original_content","suggestion","result_content","legal_basis"
    ]
    placeholders = ", ".join(f"${i+1}" for i in range(len(cols)))
    sql = f"INSERT INTO {TABLE} ({', '.join(cols)}) VALUES ({placeholders});"
    values_list = []
    for r in rows:
        values_list.append([r.get(c) for c in cols])
    async with pool.acquire() as conn:
        await conn.executemany(sql, values_list)
    return len(rows)


async def select_by_contract(pool: asyncpg.Pool, contract_id: int) -> list[dict]:
    sql = (
        f"SELECT id, contract_id, title, risk_level, position, method, risk_clause, "
        f"result_type, original_content, suggestion, result_content, legal_basis "
        f"FROM {TABLE} WHERE contract_id=$1 ORDER BY id ASC;"
    )
    async with pool.acquire() as conn:
        records = await conn.fetch(sql, contract_id)
        return [dict(r) for r in records]
