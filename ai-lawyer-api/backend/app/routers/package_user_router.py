from fastapi import APIRouter, HTTPException, Depends, Query
from ..schemas.package_user_schema import (
    PackageUserCreate,
    PackageUserUpdate,
    PackageUserRead,
)
from ..common.pagination import Paginated, PageMeta
from ..common.params import PageParams
from ..services import package_user_service
from ..schemas.response import ApiResponse


router = APIRouter(prefix="/package-users", tags=["PackageUser"])


@router.get("/", response_model=ApiResponse[Paginated[PackageUserRead]])
async def list_package_users(
    page_params: PageParams = Depends(),
    status: str | None = Query(None, description="状态(数字)"),
    packages_id: int | None = Query(None, description="套餐ID"),
    firm_name: str | None = Query(None, description="律所名称(模糊)"),
):
    items, total = await package_user_service.list_package_users_service(
        status=status,
        packages_id=packages_id,
        firm_name=firm_name,
        page=page_params.page,
        page_size=page_params.page_size,
    )
    return ApiResponse(result={
        "meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size),
        "items": items,
    })


@router.get("/{row_id}", response_model=ApiResponse[PackageUserRead])
async def get_package_user(row_id: int):
    obj = await package_user_service.get_package_user_by_id(row_id)
    if not obj:
        raise HTTPException(404, "PackageUser not found")
    return ApiResponse(result=obj)


@router.post("/", response_model=ApiResponse[PackageUserRead])
async def create_package_user(payload: PackageUserCreate):
    obj = await package_user_service.create_package_user(payload.model_dump())
    return ApiResponse(result=obj)


@router.put("/{row_id}", response_model=ApiResponse[PackageUserRead])
async def update_package_user(row_id: int, payload: PackageUserUpdate):
    obj = await package_user_service.update_package_user(row_id, payload.model_dump(exclude_unset=True))
    if not obj:
        raise HTTPException(404, "PackageUser not found")
    return ApiResponse(result=obj)


@router.delete("/{row_id}", response_model=ApiResponse[bool])
async def delete_package_user(row_id: int):
    ok = await package_user_service.delete_package_user(row_id)
    if not ok:
        raise HTTPException(404, "PackageUser not found")
    return ApiResponse(result=True)


@router.post("/cron/run", response_model=ApiResponse[dict])
async def run_package_user_cron_once():
    """手动触发一次状态刷新（按到期时间计算已到期/未到期）。"""
    updated = await package_user_service.bulk_update_status_by_expiry()
    return ApiResponse(result={"updated": updated})
