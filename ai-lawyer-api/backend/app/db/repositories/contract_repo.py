from typing import Optional, Dict, Any, List, Tuple

import asyncpg


TABLE = "contracts"
SELECT_COLUMNS = [
    "id",
    "contract_name",
    "type",
    "hasrisk",
    "high_risk",
    "medium_risk",
    "low_risk",
    "files",
    "created_user",
    "created_at",
]


def _build_filters(
    contract_name: Optional[str],
    type_: Optional[str],
    hasrisk: Optional[str],
    created_user: Optional[int],
) -> Tuple[List[str], List[Any]]:
    clauses: List[str] = []
    values: List[Any] = []

    if contract_name:
        values.append(f"%{contract_name}%")
        clauses.append(f"contract_name ILIKE ${len(values)}")

    if type_:
        values.append(type_)
        clauses.append(f"type = ${len(values)}")

    if hasrisk:
        values.append(hasrisk)
        clauses.append(f"hasrisk = ${len(values)}")

    if created_user is not None:
        values.append(int(created_user))
        clauses.append(f"created_user = ${len(values)}")

    return clauses, values


async def count(
    pool: asyncpg.Pool,
    *,
    contract_name: Optional[str] = None,
    type_: Optional[str] = None,
    hasrisk: Optional[str] = None,
    created_user: Optional[int] = None,
) -> int:
    clauses, values = _build_filters(contract_name, type_, hasrisk, created_user)
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"SELECT COUNT(*) FROM {TABLE} {where_sql};"
    async with pool.acquire() as conn:
        return int(await conn.fetchval(sql, *values))


async def get_all(
    pool: asyncpg.Pool,
    *,
    skip: int = 0,
    limit: int = 20,
    contract_name: Optional[str] = None,
    type_: Optional[str] = None,
    hasrisk: Optional[str] = None,
    created_user: Optional[int] = None,
) -> List[Dict[str, Any]]:
    clauses, values = _build_filters(contract_name, type_, hasrisk, created_user)
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    offset_idx = len(values) + 1
    limit_idx = len(values) + 2
    values.extend([skip, limit])
    cols = ", ".join(SELECT_COLUMNS)
    sql = (
        f"SELECT {cols} FROM {TABLE} {where_sql} "
        f"ORDER BY id DESC OFFSET ${offset_idx} LIMIT ${limit_idx};"
    )
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, *values)
        return [dict(r) for r in rows]


async def get_by_id(pool: asyncpg.Pool, id: int) -> Optional[Dict[str, Any]]:
    sql = f"SELECT {', '.join(SELECT_COLUMNS)} FROM {TABLE} WHERE id=$1;"
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, id)
        return dict(row) if row else None


async def create(pool: asyncpg.Pool, data: Dict[str, Any]) -> int:
    allowed = [c for c in SELECT_COLUMNS if c != "id"]
    fields = [k for k in allowed if k in data]
    if not fields:
        raise ValueError("No valid fields for insert")
    placeholders = ", ".join(f"${i+1}" for i in range(len(fields)))
    cols = ", ".join(fields)
    sql = f"INSERT INTO {TABLE} ({cols}) VALUES ({placeholders}) RETURNING id;"
    values = [data[f] for f in fields]
    async with pool.acquire() as conn:
        new_id = await conn.fetchval(sql, *values)
        return int(new_id)


async def update(pool: asyncpg.Pool, id: int, data: Dict[str, Any]) -> bool:
    allowed = [c for c in SELECT_COLUMNS if c != "id"]
    fields = [k for k in allowed if k in data]
    if not fields:
        return False
    set_parts = []
    values: List[Any] = []
    for i, f in enumerate(fields, start=1):
        set_parts.append(f"{f} = ${i}")
        values.append(data[f])
    values.append(id)
    sql = f"UPDATE {TABLE} SET {', '.join(set_parts)} WHERE id=${len(values)};"
    async with pool.acquire() as conn:
        res = await conn.execute(sql, *values)
        return res.upper().startswith("UPDATE")


async def delete(pool: asyncpg.Pool, id: int) -> bool:
    sql = f"DELETE FROM {TABLE} WHERE id=$1;"
    async with pool.acquire() as conn:
        res = await conn.execute(sql, id)
        return res.upper().startswith("DELETE")
