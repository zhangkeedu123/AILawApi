from typing import Optional, Dict, Any, List
import asyncpg


TABLE = "clients"
SELECT_COLUMNS = [
    "id",
    "name",
    "type",
    "phone",
    "address",
    "cases",
    "sstatus",
    "status_name",
    "created_at",
]


def _build_filters(
    name: Optional[str],
    type_: Optional[str],
    status: Optional[str],
    phone: Optional[str],
    email: Optional[str],
):
    clauses: List[str] = []
    values: List[Any] = []
    if name:
        values.append(f"%{name}%")
        clauses.append(f"name ILIKE ${len(values)}")
    if type_:
        values.append(type_)
        clauses.append(f"type = ${len(values)}")
    if status:
        # 若传入可转为整数，则按 sstatus 过滤；否则按 status_name 模糊匹配
        try:
            ival = int(status)
            values.append(ival)
            clauses.append(f"sstatus = ${len(values)}")
        except Exception:
            values.append(f"%{status}%")
            clauses.append(f"status_name ILIKE ${len(values)}")
    if phone:
        values.append(f"%{phone}%")
        clauses.append(f"phone ILIKE ${len(values)}")
    # email 字段在 SQL 中不存在，此处忽略 email 过滤
    return clauses, values


async def count(
    pool: asyncpg.Pool,
    *,
    name: Optional[str] = None,
    type_: Optional[str] = None,
    status: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
) -> int:
    clauses, values = _build_filters(name, type_, status, phone, email)
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
    type_: Optional[str] = None,
    status: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
) -> List[Dict[str, Any]]:
    clauses, values = _build_filters(name, type_, status, phone, email)
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
