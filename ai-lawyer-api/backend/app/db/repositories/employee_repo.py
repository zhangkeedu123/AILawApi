from typing import Optional, Dict, Any, List
import asyncpg


TABLE = "employees"
SELECT_COLUMNS = [
    "id",
    "name",
    "phone",
    "password",
    "token",
    "firm_id",
    "firm_name",
    "client_num",
    "case_num",
    "status",
    "status_name",
    "created_at",
    "update_at",
    "role",
]


def _build_filters(
    name: Optional[str],
    firm_name: Optional[str],
    firm_id: Optional[str] = None,
):
    clauses: List[str] = []
    values: List[Any] = []
    if name:
        values.append(f"%{name}%")
        clauses.append(f"name ILIKE ${len(values)}")
    
    if firm_name:
        values.append(f"%{firm_name}%")
        clauses.append(f"firm_name ILIKE ${len(values)}")
    if firm_id:
        values.append(str(firm_id))
        clauses.append(f"firm_id = ${len(values)}")
   
    return clauses, values


async def count(
    pool: asyncpg.Pool,
    *,
    name: Optional[str] = None,
    firm_name: Optional[str] = None,
    firm_id: Optional[str] = None,
) -> int:
    clauses, values = _build_filters(name, firm_name, firm_id)
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
    firm_name: Optional[str] = None,
    firm_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    clauses, values = _build_filters(name, firm_name, firm_id)
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


# Auth-related helpers
async def get_by_phone(pool: asyncpg.Pool, phone: str) -> Optional[Dict[str, Any]]:
    cols = ", ".join(SELECT_COLUMNS)
    sql = f"SELECT {cols} FROM {TABLE} WHERE phone=$1;"
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, phone)
        return dict(row) if row else None


async def update_token(pool: asyncpg.Pool, emp_id: int, token_hash: str) -> bool:
    sql = f"UPDATE {TABLE} SET token=$1 WHERE id=$2;"
    async with pool.acquire() as conn:
        res = await conn.execute(sql, token_hash, emp_id)
        return res.upper().startswith("UPDATE")
