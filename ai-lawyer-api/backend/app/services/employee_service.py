from typing import Optional, Tuple, List, Dict, Any
from fastapi import HTTPException
from ..db.db import get_pg_pool
from ..db.repositories import employee_repo
from ..security.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    device_fingerprint,
    get_current_user,
)

async def list_employees_service(
    *,
    name: Optional[str] = None,
    firm_name: Optional[str] = None,
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
        firm_name=firm_name,
    )
    total = await employee_repo.count(
        pool, name=name,  firm_name=firm_name, 
    )
    return items, total


async def get_employee_by_id(emp_id: int) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    return await employee_repo.get_by_id(pool, emp_id)


async def create_employee(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    phone = data.get("phone")
    if phone:
        existed = await employee_repo.get_by_phone(pool, phone)
        if existed:
            # 手机号唯一性约束
            raise HTTPException(status_code=400, detail="手机号已存在")
    # 哈希密码（若提供）
    if "password" in data and data["password"]:
        data["password"] = hash_password(str(data["password"]))
    new_id = await employee_repo.create(pool, data)
    return await employee_repo.get_by_id(pool, new_id)


async def update_employee(emp_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    # 若更新手机号，需校验唯一性（排除自身）
    phone = data.get("phone")
    if phone:
        existed = await employee_repo.get_by_phone(pool, phone)
        if existed and int(existed.get("id")) != int(emp_id):
            raise HTTPException(status_code=400, detail="手机号已存在")

    # 若允许修改密码，需进行哈希
    if "password" in data:
        if data["password"]:
            data["password"] = hash_password(str(data["password"]))
        else:
            # 空密码不更新
            data.pop("password", None)
    ok = await employee_repo.update(pool, emp_id, data)
    if not ok:
        return None
    return await employee_repo.get_by_id(pool, emp_id)


async def delete_employee(emp_id: int) -> bool:
    pool = await get_pg_pool()
    return await employee_repo.delete(pool, emp_id)
