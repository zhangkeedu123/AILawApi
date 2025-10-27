from fastapi import APIRouter, HTTPException, Depends, Query
from ..schemas.firm_schema import FirmCreate, FirmUpdate, FirmRead
from ..common.pagination import Paginated, PageMeta
from ..common.params import PageParams
from ..services import firm_service
from ..schemas.response import ApiResponse

router = APIRouter(prefix="/firms", tags=["Firm"])


@router.get("/", response_model=ApiResponse[Paginated[FirmRead]])
async def list_firms(
    page_params: PageParams = Depends(),
    name: str | None = Query(None, description="律所名称(模糊)"),
    city: str | None = Query(None, description="城市(模糊)"),
    status: str | None = Query(None, description="状态"),
    package: str | None = Query(None, description="套餐"),
):
    items, total = await firm_service.list_firms_service(
        name=name, city=city, status=status, package=package,
        page=page_params.page, page_size=page_params.page_size,
    )
    return ApiResponse(result={"meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size), "items": items})


@router.get("/{firm_id}", response_model=ApiResponse[FirmRead])
async def get_firm(firm_id: int):
    obj = await firm_service.get_firm_by_id(firm_id)
    if not obj:
        raise HTTPException(404, "Firm not found")
    return ApiResponse(result=obj)


@router.post("/", response_model=ApiResponse[FirmRead])
async def create_firm(payload: FirmCreate):
    obj = await firm_service.create_firm(payload.model_dump())
    return ApiResponse(result=obj)


@router.put("/{firm_id}", response_model=ApiResponse[FirmRead])
async def update_firm(firm_id: int, payload: FirmUpdate):
    obj = await firm_service.update_firm(firm_id, payload.model_dump(exclude_unset=True))
    if not obj:
        raise HTTPException(404, "Firm not found")
    return ApiResponse(result=obj)


@router.delete("/{firm_id}", response_model=ApiResponse[bool])
async def delete_firm(firm_id: int):
    ok = await firm_service.delete_firm(firm_id)
    if not ok:
        raise HTTPException(404, "Firm not found")
    return ApiResponse(result=True)
