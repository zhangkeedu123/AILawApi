from typing import Optional, Tuple, List, Dict, Any
from ..db.db import get_pg_pool
from ..db.repositories import document_repo


async def list_documents_service(
    *,
    doc_name: Optional[str] = None,
    doc_type: Optional[str] = None,
    user_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Dict[str, Any]], int]:
    pool = await get_pg_pool()
    skip = (page - 1) * page_size
    items = await document_repo.get_all(
        pool,
        skip=skip,
        limit=page_size,
        doc_name=doc_name,
        doc_type=doc_type,
        user_id=user_id,
    )
    total = await document_repo.count(pool, doc_name=doc_name, doc_type=doc_type, user_id=user_id)
    return items, total


async def get_document_by_id(doc_id: int) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    return await document_repo.get_by_id(pool, doc_id)


async def create_document(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    new_id = await document_repo.create(pool, data)
    return await document_repo.get_by_id(pool, new_id)


async def update_document(doc_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    ok = await document_repo.update(pool, doc_id, data)
    if not ok:
        return None
    return await document_repo.get_by_id(pool, doc_id)


async def delete_document(doc_id: int) -> bool:
    pool = await get_pg_pool()
    return await document_repo.delete(pool, doc_id)
