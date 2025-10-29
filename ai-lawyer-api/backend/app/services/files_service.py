from typing import Optional, Tuple, List, Dict, Any
from ..db.db import get_pg_pool
from ..db.repositories import files_repo


async def list_files_service(
    *,
    name: Optional[str] = None,
    user_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Dict[str, Any]], int]:
    """分页查询文件列表，可按名称和用户过滤"""
    pool = await get_pg_pool()
    skip = (page - 1) * page_size
    items = await files_repo.get_all(
        pool,
        skip=skip,
        limit=page_size,
        name=name,
        user_id=user_id,
    )
    total = await files_repo.count(pool, name=name, user_id=user_id)
    return items, total


async def get_file_by_id(file_id: int) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    return await files_repo.get_by_id(pool, file_id)


async def create_file(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    new_id = await files_repo.create(pool, data)
    return await files_repo.get_by_id(pool, new_id)


async def update_file(file_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    ok = await files_repo.update(pool, file_id, data)
    if not ok:
        return None
    return await files_repo.get_by_id(pool, file_id)


async def delete_file(file_id: int) -> bool:
    pool = await get_pg_pool()
    return await files_repo.delete(pool, file_id)

