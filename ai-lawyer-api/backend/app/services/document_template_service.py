from typing import Any, Dict, List, Optional, Tuple

from ..db.db import get_pg_pool
from ..db.repositories import document_template_repo


async def list_document_templates_service(
    *,
    name: Optional[str] = None,
    p_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Dict[str, Any]], int]:
    pool = await get_pg_pool()
    skip = (page - 1) * page_size
    items = await document_template_repo.get_all(
        pool,
        skip=skip,
        limit=page_size,
        name=name,
        p_id=p_id,
    )
    total = await document_template_repo.count(
        pool,
        name=name,
        p_id=p_id,
    )
    return items, total


async def get_document_template_by_id(id_: int) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    return await document_template_repo.get_by_id(pool, id_)


async def create_document_template(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    new_id = await document_template_repo.create(pool, data)
    return await document_template_repo.get_by_id(pool, new_id)


async def update_document_template(id_: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    ok = await document_template_repo.update(pool, id_, data)
    if not ok:
        return None
    return await document_template_repo.get_by_id(pool, id_)


async def delete_document_template(id_: int) -> bool:
    pool = await get_pg_pool()
    return await document_template_repo.delete(pool, id_)
