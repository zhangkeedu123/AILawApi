from typing import Optional, Dict, Any, List, Tuple
import asyncpg


TABLE = "packages_user"

# 以联查名称为主，选择需要的列
BASE_COLUMNS = [
    "pu.id",
    "pu.packages_id",
    "pu.firms_id",
    "pu.status",
    "pu.status_name",
    "pu.day_use_num",
    "pu.expiry_date",
    "pu.money",
    "pu.created_at",
    "p.name AS package_name",
    "f.name AS firm_name",
]


def _build_filters(
    *,
    status: Optional[str] = None,
    firms_id: Optional[int] = None,
    packages_id: Optional[int] = None,
    firm_name: Optional[str] = None,
    package_name: Optional[str] = None,
) -> Tuple[List[str], List[Any]]:
    clauses: List[str] = []
    values: List[Any] = []
    if status is not None and status != "":
        try:
            ival = int(status)
            values.append(ival)
            clauses.append(f"pu.status = ${len(values)}")
        except Exception:
            values.append(f"%{status}%")
            clauses.append(f"pu.status_name ILIKE ${len(values)}")
    if firms_id:
        values.append(int(firms_id))
        clauses.append(f"pu.firms_id = ${len(values)}")
    if packages_id:
        values.append(int(packages_id))
        clauses.append(f"pu.packages_id = ${len(values)}")
    if firm_name:
        values.append(f"%{firm_name}%")
        clauses.append(f"f.name ILIKE ${len(values)}")
    if package_name:
        values.append(f"%{package_name}%")
        clauses.append(f"p.name ILIKE ${len(values)}")
    return clauses, values


async def count(
    pool: asyncpg.Pool,
    *,
    status: Optional[str] = None,
    firms_id: Optional[int] = None,
    packages_id: Optional[int] = None,
    firm_name: Optional[str] = None,
    package_name: Optional[str] = None,
) -> int:
    clauses, values = _build_filters(
        status=status,
        firms_id=firms_id,
        packages_id=packages_id,
        firm_name=firm_name,
        package_name=package_name,
    )
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = (
        "SELECT COUNT(*) FROM packages_user pu "
        "JOIN packages p ON p.id = pu.packages_id "
        "JOIN firms f ON f.id = pu.firms_id "
        f"{where_sql};"
    )
    async with pool.acquire() as conn:
        return int(await conn.fetchval(sql, *values))


async def get_all(
    pool: asyncpg.Pool,
    *,
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    firms_id: Optional[int] = None,
    packages_id: Optional[int] = None,
    firm_name: Optional[str] = None,
    package_name: Optional[str] = None,
) -> List[Dict[str, Any]]:
    clauses, values = _build_filters(
        status=status,
        firms_id=firms_id,
        packages_id=packages_id,
        firm_name=firm_name,
        package_name=package_name,
    )
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    offset_idx = len(values) + 1
    limit_idx = len(values) + 2
    values.extend([skip, limit])
    cols = ", ".join(BASE_COLUMNS)
    sql = (
        f"SELECT {cols} FROM {TABLE} pu "
        "JOIN packages p ON p.id = pu.packages_id "
        "JOIN firms f ON f.id = pu.firms_id "
        f"{where_sql} ORDER BY pu.id DESC OFFSET ${offset_idx} LIMIT ${limit_idx};"
    )
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, *values)
        return [dict(r) for r in rows]


async def get_by_id(pool: asyncpg.Pool, id: int) -> Optional[Dict[str, Any]]:
    cols = ", ".join(BASE_COLUMNS)
    sql = (
        f"SELECT {cols} FROM {TABLE} pu "
        "JOIN packages p ON p.id = pu.packages_id "
        "JOIN firms f ON f.id = pu.firms_id "
        "WHERE pu.id=$1;"
    )
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, id)
        return dict(row) if row else None


async def create(pool: asyncpg.Pool, data: Dict[str, Any]) -> int:
    allowed = [
        "packages_id",
        "firms_id",
        "status",
        "status_name",
        "day_use_num",
        "expiry_date",
        "money",
    ]
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
    allowed = [
        "packages_id",
        "firms_id",
        "status",
        "status_name",
        "day_use_num",
        "expiry_date",
        "money",
    ]
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


async def update_all_status_by_expiry(pool: asyncpg.Pool) -> int:
    """
    根据到期时间批量更新所有记录的状态与状态名称。
    到期(<= NOW()) -> status=1, status_name='已到期'
    未到期(> NOW()) -> status=0, status_name='未到期'
    返回受影响行数。
    """
    sql = (
        "UPDATE packages_user "
        "SET status = CASE WHEN expiry_date <= NOW() THEN 1 ELSE 0 END, "
        "    status_name = CASE WHEN expiry_date <= NOW() THEN '已到期' ELSE '未到期' END;"
    )
    async with pool.acquire() as conn:
        res = await conn.execute(sql)
        # asyncpg 返回类似 'UPDATE 123'
        try:
            return int(str(res).split()[-1])
        except Exception:
            return 0
