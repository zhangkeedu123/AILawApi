from fastapi import APIRouter, HTTPException, Depends, Query
from ..schemas.client_schema import ClientCreate, ClientUpdate, ClientRead
from ..common.pagination import Paginated, PageMeta
from ..common.params import PageParams
from ..services import client_service
from ..schemas.response import ApiResponse

router = APIRouter(prefix="/clients", tags=["Client"])


@router.get("/", response_model=ApiResponse[Paginated[ClientRead]])
async def list_clients(
    page_params: PageParams = Depends(),
    name: str | None = Query(None, description="客户名称(模糊)"),
    phone: str | None = Query(None, description="电话(模糊)"),
):
    items, total = await client_service.list_clients_service(
        name=name,  phone=phone, 
        page=page_params.page, page_size=page_params.page_size,
    )
    return ApiResponse(result={"meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size), "items": items})


@router.get("/{client_id}", response_model=ApiResponse[ClientRead])
async def get_client(client_id: int):
    obj = await client_service.get_client_by_id(client_id)
    if not obj:
        raise HTTPException(404, "Client not found")
    return ApiResponse(result=obj)


@router.post("/", response_model=ApiResponse[ClientRead])
async def create_client(payload: ClientCreate):
    obj = await client_service.create_client(payload.model_dump())
    return ApiResponse(result=obj)


@router.put("/{client_id}", response_model=ApiResponse[ClientRead])
async def update_client(client_id: int, payload: ClientUpdate):
    obj = await client_service.update_client(client_id, payload.model_dump(exclude_unset=True))
    if not obj:
        raise HTTPException(404, "Client not found")
    return ApiResponse(result=obj)


@router.delete("/{client_id}", response_model=ApiResponse[bool])
async def delete_client(client_id: int):
    ok = await client_service.delete_client(client_id)
    if not ok:
        raise HTTPException(404, "Client not found")
    return ApiResponse(result=True)
