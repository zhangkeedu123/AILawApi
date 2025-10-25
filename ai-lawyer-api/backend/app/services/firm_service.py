from typing import Optional, Tuple, List, Dict, Any
from ..db.db import get_pg_pool
from ..db.repositories import firm_repo


async def list_firms_service(
    *,
    name: Optional[str] = None,
    city: Optional[str] = None,
    status: Optional[str] = None,
    package: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Dict[str, Any]], int]:
    pool = await get_pg_pool()
    skip = (page - 1) * page_size
    items = await firm_repo.get_all(
        pool,
        skip=skip,
        limit=page_size,
        name=name,
        city=city,
        status=status,
        package=package,
    )
    total = await firm_repo.count(
        pool, name=name, city=city, status=status, package=package
    )
    return items, total


async def get_firm_by_id(firm_id: int) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    return await firm_repo.get_by_id(pool, firm_id)


async def create_firm(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    new_id = await firm_repo.create(pool, data)
    return await firm_repo.get_by_id(pool, new_id)


async def update_firm(firm_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    ok = await firm_repo.update(pool, firm_id, data)
    if not ok:
        return None
    return await firm_repo.get_by_id(pool, firm_id)


async def delete_firm(firm_id: int) -> bool:
    pool = await get_pg_pool()
    return await firm_repo.delete(pool, firm_id)
