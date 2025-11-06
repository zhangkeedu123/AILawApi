from typing import Optional, Tuple, List, Dict, Any
from ..db.db import get_pg_pool
from ..db.repositories import client_repo


async def list_clients_service(
    *,
    name: Optional[str] = None,
    type_: Optional[str] = None,
    status: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Dict[str, Any]], int]:
    pool = await get_pg_pool()
    skip = (page - 1) * page_size
    items = await client_repo.get_all(
        pool,
        skip=skip,
        limit=page_size,
        name=name,
        phone=phone,
    )
    total = await client_repo.count(
        pool, name=name,  phone=phone,
    )
    return items, total


async def get_client_by_id(client_id: int) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    return await client_repo.get_by_id(pool, client_id)


async def create_client(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    new_id = await client_repo.create(pool, data)
    return await client_repo.get_by_id(pool, new_id)


async def update_client(client_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    ok = await client_repo.update(pool, client_id, data)
    if not ok:
        return None
    return await client_repo.get_by_id(pool, client_id)


async def delete_client(client_id: int) -> bool:
    pool = await get_pg_pool()
    return await client_repo.delete(pool, client_id)
