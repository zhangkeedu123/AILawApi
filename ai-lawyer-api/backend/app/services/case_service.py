from typing import Optional, Tuple, List, Dict, Any
from ..db.db import get_pg_pool
from ..db.repositories import case_repo


async def list_cases_service(
    *,
    name: Optional[str] = None,
    status: Optional[str] = None,
    location: Optional[str] = None,
    plaintiff: Optional[str] = None,
    defendant: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Dict[str, Any]], int]:
    pool = await get_pg_pool()
    skip = (page - 1) * page_size
    items = await case_repo.get_all(
        pool,
        skip=skip,
        limit=page_size,
        name=name,
        status=status,
        location=location,
        plaintiff=plaintiff,
        defendant=defendant,
    )
    total = await case_repo.count(
        pool, name=name, status=status, location=location, plaintiff=plaintiff, defendant=defendant
    )
    return items, total


async def get_case_by_id(case_id: int) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    return await case_repo.get_by_id(pool, case_id)


async def create_case(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    new_id = await case_repo.create(pool, data)
    return await case_repo.get_by_id(pool, new_id)


async def update_case(case_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    ok = await case_repo.update(pool, case_id, data)
    if not ok:
        return None
    return await case_repo.get_by_id(pool, case_id)


async def delete_case(case_id: int) -> bool:
    pool = await get_pg_pool()
    return await case_repo.delete(pool, case_id)
