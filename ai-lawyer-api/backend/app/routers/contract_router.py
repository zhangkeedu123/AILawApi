from fastapi import APIRouter, HTTPException, Depends, Query
from ..schemas.contract_schema import ContractCreate, ContractUpdate, ContractRead
from ..common.pagination import Paginated, PageMeta
from ..common.params import PageParams
from ..services import contract_service
from ..schemas.response import ApiResponse

router = APIRouter(prefix="/contracts", tags=["Contract"])


@router.get("/", response_model=ApiResponse[Paginated[ContractRead]])
async def list_contracts(
    page_params: PageParams = Depends(),
    customer: str | None = Query(None, description="客户名称(模糊)"),
    type_: str | None = Query(None, alias="type", description="合同类型"),
    status: str | None = Query(None, description="状态"),
    upload_date_from: str | None = Query(None, description="上传日期(如 YYYY-MM-DD)"),
    upload_date_to: str | None = Query(None, description="上传日期(如 YYYY-MM-DD)"),
):
    items, total = await contract_service.list_contracts_service(
        customer=customer, type_=type_, status=status,
        upload_date_from=upload_date_from, upload_date_to=upload_date_to,
        page=page_params.page, page_size=page_params.page_size,
    )
    return ApiResponse(result={"meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size), "items": items})


@router.get("/{contract_id}", response_model=ApiResponse[ContractRead])
async def get_contract(contract_id: int):
    obj = await contract_service.get_contract_by_id(contract_id)
    if not obj:
        raise HTTPException(404, "Contract not found")
    return ApiResponse(result=obj)


@router.post("/", response_model=ApiResponse[ContractRead])
async def create_contract(payload: ContractCreate):
    obj = await contract_service.create_contract(payload.model_dump())
    return ApiResponse(result=obj)


@router.put("/{contract_id}", response_model=ApiResponse[ContractRead])
async def update_contract(contract_id: int, payload: ContractUpdate):
    obj = await contract_service.update_contract(contract_id, payload.model_dump(exclude_unset=True))
    if not obj:
        raise HTTPException(404, "Contract not found")
    return ApiResponse(result=obj)


@router.delete("/{contract_id}", response_model=ApiResponse[bool])
async def delete_contract(contract_id: int):
    ok = await contract_service.delete_contract(contract_id)
    if not ok:
        raise HTTPException(404, "Contract not found")
    return ApiResponse(result=True)
