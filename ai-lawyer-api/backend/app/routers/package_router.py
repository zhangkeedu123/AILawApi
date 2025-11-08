from fastapi import APIRouter, HTTPException, Query, Depends
from ..schemas.package_schema import PackageCreate, PackageUpdate, PackageRead
from ..common.pagination import Paginated, PageMeta
from ..common.params import PageParams
from ..services import package_service
from ..schemas.response import ApiResponse


router = APIRouter(prefix="/packages", tags=["Package"])


@router.get("/", response_model=ApiResponse[Paginated[PackageRead]])
async def list_packages(
    page_params: PageParams = Depends(),
    name: str | None = Query(None, description="套餐名称(模糊)")
):
    items, total = await package_service.list_packages_service(
        name=name,
        page=page_params.page,
        page_size=page_params.page_size,
    )
    return ApiResponse(result={
        "meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size),
        "items": items,
    })


@router.get("/{package_id}", response_model=ApiResponse[PackageRead])
async def get_package(package_id: int):
    obj = await package_service.get_package_by_id(package_id)
    if not obj:
        raise HTTPException(404, "Package not found")
    return ApiResponse(result=obj)


@router.post("/", response_model=ApiResponse[PackageRead])
async def create_package(payload: PackageCreate):
    obj = await package_service.create_package(payload.model_dump())
    return ApiResponse(result=obj)


@router.put("/{package_id}", response_model=ApiResponse[PackageRead])
async def update_package(package_id: int, payload: PackageUpdate):
    obj = await package_service.update_package(package_id, payload.model_dump(exclude_unset=True))
    if not obj:
        raise HTTPException(404, "Package not found")
    return ApiResponse(result=obj)


@router.delete("/{package_id}", response_model=ApiResponse[bool])
async def delete_package(package_id: int):
    ok = await package_service.delete_package(package_id)
    if not ok:
        raise HTTPException(404, "Package not found")
    return ApiResponse(result=True)

