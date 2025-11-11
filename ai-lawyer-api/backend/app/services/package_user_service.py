from typing import Optional, Tuple, List, Dict, Any
from ..db.db import get_pg_pool
from ..db.repositories import package_user_repo


async def list_package_users_service(
    *,
    status: Optional[str] = None,
    packages_id: Optional[int] = None,
    firm_name: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Dict[str, Any]], int]:
    pool = await get_pg_pool()
    skip = (page - 1) * page_size
    items = await package_user_repo.get_all(
        pool,
        skip=skip,
        limit=page_size,
        status=status,
        packages_id=packages_id,
        firm_name=firm_name,
    )
    total = await package_user_repo.count(
        pool,
        status=status,
        packages_id=packages_id,
        firm_name=firm_name,
    )
    return items, total


async def get_package_user_by_id(row_id: int) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    return await package_user_repo.get_by_id(pool, row_id)


async def create_package_user(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    new_id = await package_user_repo.create(pool, data)
    return await package_user_repo.get_by_id(pool, new_id)


async def update_package_user(row_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    ok = await package_user_repo.update(pool, row_id, data)
    if not ok:
        return None
    return await package_user_repo.get_by_id(pool, row_id)


async def delete_package_user(row_id: int) -> bool:
    pool = await get_pg_pool()
    return await package_user_repo.delete(pool, row_id)


async def bulk_update_status_by_expiry() -> int:
    """根据到期时间批量更新所有套餐订阅的状态与名称。"""
    pool = await get_pg_pool()
    return await package_user_repo.update_all_status_by_expiry(pool)


async def reset_all_day_used() -> int:
    """每日重置所有套餐的当日已用次数。"""
    pool = await get_pg_pool()
    return await package_user_repo.reset_all_day_used(pool)
