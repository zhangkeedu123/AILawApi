from typing import Optional, Tuple, List, Dict, Any
from ..db.db import get_pg_pool
from ..db.repositories import employee_repo


async def list_employees_service(
    *,
    name: Optional[str] = None,
    title: Optional[str] = None,
    firm_name: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Dict[str, Any]], int]:
    pool = await get_pg_pool()
    skip = (page - 1) * page_size
    items = await employee_repo.get_all(
        pool,
        skip=skip,
        limit=page_size,
        name=name,
        title=title,
        firm_name=firm_name,
        status=status,
    )
    total = await employee_repo.count(
        pool, name=name, title=title, firm_name=firm_name, status=status
    )
    return items, total


async def get_employee_by_id(emp_id: int) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    return await employee_repo.get_by_id(pool, emp_id)


async def create_employee(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    new_id = await employee_repo.create(pool, data)
    return await employee_repo.get_by_id(pool, new_id)


async def update_employee(emp_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    ok = await employee_repo.update(pool, emp_id, data)
    if not ok:
        return None
    return await employee_repo.get_by_id(pool, emp_id)


async def delete_employee(emp_id: int) -> bool:
    pool = await get_pg_pool()
    return await employee_repo.delete(pool, emp_id)
