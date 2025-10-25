from typing import Optional, Tuple, List, Dict, Any
from ..db.db import get_pg_pool
from ..db.repositories import spider_repo


async def list_spider_customers_service(
    *,
    name: Optional[str] = None,
    city: Optional[str] = None,
    platform: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Dict[str, Any]], int]:
    pool = await get_pg_pool()
    skip = (page - 1) * page_size
    items = await spider_repo.get_all(
        pool,
        skip=skip,
        limit=page_size,
        name=name,
        city=city,
        platform=platform,
        status=status,
    )
    total = await spider_repo.count(
        pool, name=name, city=city, platform=platform, status=status
    )
    return items, total


async def get_spider_customer_by_id(item_id: int) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    return await spider_repo.get_by_id(pool, item_id)


async def create_spider_customer(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    new_id = await spider_repo.create(pool, data)
    return await spider_repo.get_by_id(pool, new_id)


async def update_spider_customer(item_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    ok = await spider_repo.update(pool, item_id, data)
    if not ok:
        return None
    return await spider_repo.get_by_id(pool, item_id)


async def delete_spider_customer(item_id: int) -> bool:
    pool = await get_pg_pool()
    return await spider_repo.delete(pool, item_id)
