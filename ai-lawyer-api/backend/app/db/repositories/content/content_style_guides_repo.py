from typing import Optional, Dict, Any, List
import asyncpg


TABLE = "content_style_guides"
SELECT_COLUMNS = [
    "id",
    "tone",
    "reading_level",
    "do_list",
    "dont_list",
    "legal_scope",
    "created_at",
]


def _build_filters(
    tone: Optional[str] = None,
    reading_level: Optional[str] = None,
):
    clauses: List[str] = []
    values: List[Any] = []
    if tone:
        values.append(f"%{tone}%")
        clauses.append(f"tone ILIKE ${len(values)}")
    if reading_level:
        values.append(f"%{reading_level}%")
        clauses.append(f"reading_level ILIKE ${len(values)}")
    return clauses, values


async def count(
    pool: asyncpg.Pool,
    *,
    tone: Optional[str] = None,
    reading_level: Optional[str] = None,
) -> int:
    clauses, values = _build_filters(tone, reading_level)
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"SELECT COUNT(*) FROM {TABLE} {where_sql};"
    async with pool.acquire() as conn:
        return int(await conn.fetchval(sql, *values))


async def get_all(
    pool: asyncpg.Pool,
    *,
    skip: int = 0,
    limit: int = 20,
    tone: Optional[str] = None,
    reading_level: Optional[str] = None,
) -> List[Dict[str, Any]]:
    clauses, values = _build_filters(tone, reading_level)
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


async def get_by_id(pool: asyncpg.Pool, id: int) -> Optional[Dict[str, Any]]:
    cols = ", ".join(SELECT_COLUMNS)
    sql = f"SELECT {cols} FROM {TABLE} WHERE id=$1;"
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
    allowed = [c for c in SELECT_COLUMNS if c not in ("id",)]
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

