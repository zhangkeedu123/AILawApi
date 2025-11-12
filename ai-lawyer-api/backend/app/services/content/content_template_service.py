from typing import Optional, Tuple, List, Dict, Any
from ...db.db import get_pg_pool
from ...db.repositories.content import content_templates_repo


async def list_service(
    *,
    name: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Dict[str, Any]], int]:
    pool = await get_pg_pool()
    skip = (page - 1) * page_size
    items = await content_templates_repo.get_all(
        pool,
        skip=skip,
        limit=page_size,
        name=name,
    )
    total = await content_templates_repo.count(pool, name=name)
    return items, total


async def get_by_id(id_: int) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    return await content_templates_repo.get_by_id(pool, id_)


async def create(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    new_id = await content_templates_repo.create(pool, data)
    return await content_templates_repo.get_by_id(pool, new_id)


async def update(id_: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    ok = await content_templates_repo.update(pool, id_, data)
    if not ok:
        return None
    return await content_templates_repo.get_by_id(pool, id_)


async def delete(id_: int) -> bool:
    pool = await get_pg_pool()
    return await content_templates_repo.delete(pool, id_)

