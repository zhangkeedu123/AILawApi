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
    contract_name: str | None = Query(None, description="合同名称(模糊)"),
    type_: str | None = Query(None, alias="type", description="合同类型"),
    hasrisk: str | None = Query(None, description="是否有风险"),
):
    items, total = await contract_service.list_contracts_service(
        contract_name=contract_name,
        type_=type_,
        hasrisk=hasrisk,
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
