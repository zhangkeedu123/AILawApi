from typing import Optional, Tuple, List, Dict, Any
from ..db.db import get_pg_pool
from ..db.repositories import contract_repo


async def list_contracts_service(
    *,
    customer: Optional[str] = None,
    type_: Optional[str] = None,
    status: Optional[str] = None,
    upload_date_from: Optional[str] = None,  # 'YYYY-MM-DD'
    upload_date_to: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Dict[str, Any]], int]:
    pool = await get_pg_pool()
    skip = (page - 1) * page_size
    items = await contract_repo.get_all(
        pool,
        skip=skip,
        limit=page_size,
        customer=customer,
        type_=type_,
        status=status,
        upload_date_from=upload_date_from,
        upload_date_to=upload_date_to,
    )
    total = await contract_repo.count(
        pool,
        customer=customer,
        type_=type_,
        status=status,
        upload_date_from=upload_date_from,
        upload_date_to=upload_date_to,
    )
    return items, total


async def get_contract_by_id(contract_id: int) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    return await contract_repo.get_by_id(pool, contract_id)


async def create_contract(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    new_id = await contract_repo.create(pool, data)
    return await contract_repo.get_by_id(pool, new_id)


async def update_contract(contract_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    ok = await contract_repo.update(pool, contract_id, data)
    if not ok:
        return None
    return await contract_repo.get_by_id(pool, contract_id)


async def delete_contract(contract_id: int) -> bool:
    pool = await get_pg_pool()
    return await contract_repo.delete(pool, contract_id)
