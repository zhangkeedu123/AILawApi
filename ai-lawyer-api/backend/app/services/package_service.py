from typing import Optional, Tuple, List, Dict, Any
from ..db.db import get_pg_pool
from ..db.repositories import package_repo


async def list_packages_service(
    *,
    name: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Dict[str, Any]], int]:
    pool = await get_pg_pool()
    skip = (page - 1) * page_size
    items = await package_repo.get_all(
        pool,
        skip=skip,
        limit=page_size,
        name=name,
    )
    total = await package_repo.count(
        pool,
        name=name,
    )
    return items, total


async def get_package_by_id(pkg_id: int) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    return await package_repo.get_by_id(pool, pkg_id)


async def create_package(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    new_id = await package_repo.create(pool, data)
    return await package_repo.get_by_id(pool, new_id)


async def update_package(pkg_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    ok = await package_repo.update(pool, pkg_id, data)
    if not ok:
        return None
    return await package_repo.get_by_id(pool, pkg_id)


async def delete_package(pkg_id: int) -> bool:
    pool = await get_pg_pool()
    return await package_repo.delete(pool, pkg_id)

