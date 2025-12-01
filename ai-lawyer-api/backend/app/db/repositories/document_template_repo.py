from typing import Any, Dict, List, Optional

import asyncpg


TABLE = "document_template"
SELECT_COLUMNS = [
    "id",
    "name",
    "p_id",
    "url",
    "is_template",
    "created_at",
]


def _build_filters(
    name: Optional[str],
    p_id: Optional[int],
    is_template: Optional[bool],
) -> tuple[list[str], list[Any]]:
    clauses: List[str] = []
    values: List[Any] = []
    if name:
        values.append(f"%{name}%")
        clauses.append(f"name ILIKE ${len(values)}")
    if p_id is not None:
        values.append(int(p_id))
        clauses.append(f"p_id = ${len(values)}")
    if is_template is not None:
        values.append(bool(is_template))
        clauses.append(f"is_template = ${len(values)}")
    return clauses, values


async def count(
    pool: asyncpg.Pool,
    *,
    name: Optional[str] = None,
    p_id: Optional[int] = None,
    is_template: Optional[bool] = None,
) -> int:
    clauses, values = _build_filters(name, p_id, is_template)
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"SELECT COUNT(*) FROM {TABLE} {where_sql};"
    async with pool.acquire() as conn:
        return int(await conn.fetchval(sql, *values))


async def get_all(
    pool: asyncpg.Pool,
    *,
    skip: int = 0,
    limit: int = 20,
    name: Optional[str] = None,
    p_id: Optional[int] = None,
    is_template: Optional[bool] = None,
) -> List[Dict[str, Any]]:
    clauses, values = _build_filters(name, p_id, is_template)
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    values.extend([skip, limit])
    cols = ", ".join(SELECT_COLUMNS)
    sql = (
        f"SELECT {cols} FROM {TABLE} {where_sql} "
        f"ORDER BY id DESC OFFSET ${len(values)-1} LIMIT ${len(values)};"
    )
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, *values)
        return [dict(r) for r in rows]


async def get_by_id(pool: asyncpg.Pool, id_: int) -> Optional[Dict[str, Any]]:
    cols = ", ".join(SELECT_COLUMNS)
    sql = f"SELECT {cols} FROM {TABLE} WHERE id=$1;"
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, id_)
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


async def update(pool: asyncpg.Pool, id_: int, data: Dict[str, Any]) -> bool:
    allowed = [c for c in SELECT_COLUMNS if c != "id"]
    fields = [k for k in allowed if k in data]
    if not fields:
        return False
    set_parts = []
    values: List[Any] = []
    for i, f in enumerate(fields, start=1):
        set_parts.append(f"{f} = ${i}")
        values.append(data[f])
    values.append(id_)
    sql = f"UPDATE {TABLE} SET {', '.join(set_parts)} WHERE id=${len(values)};"
    async with pool.acquire() as conn:
        res = await conn.execute(sql, *values)
        return res.upper().startswith("UPDATE")


async def delete(pool: asyncpg.Pool, id_: int) -> bool:
    sql = f"DELETE FROM {TABLE} WHERE id=$1;"
    async with pool.acquire() as conn:
        res = await conn.execute(sql, id_)
        return res.upper().startswith("DELETE")
