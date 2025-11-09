from fastapi import APIRouter, HTTPException, Depends, Query
from ..schemas.contract_schema import ContractCreate, ContractUpdate, ContractRead
from ..common.pagination import Paginated, PageMeta
from ..common.params import PageParams
from ..services import contract_service, contract_review_service
from ..schemas.response import ApiResponse
from ..security.auth import get_current_user


router = APIRouter(prefix="/contracts", tags=["Contract"])


@router.get("/", response_model=ApiResponse[Paginated[ContractRead]])
async def list_contracts(
    page_params: PageParams = Depends(),
    contract_name: str | None = Query(None, description="合同名称(模糊)"),
    type_: str | None = Query(None, alias="type", description="合同类型"),
    hasrisk: str | None = Query(None, description="是否有风险"),
    user: dict = Depends(get_current_user),
):
    created_user = None if int(user.get("role", 0)) == 2 else int(user["id"])
    items, total = await contract_service.list_contracts_service(
        contract_name=contract_name,
        type_=type_,
        hasrisk=hasrisk,
        created_user=created_user,
        page=page_params.page,
        page_size=page_params.page_size,
    )
    return ApiResponse(result={
        "meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size),
        "items": items,
    })


@router.get("/{contract_id}", response_model=ApiResponse[ContractRead])
async def get_contract(contract_id: int, user: dict = Depends(get_current_user)):
    obj = await contract_service.get_contract_by_id(contract_id)
    if not obj:
        raise HTTPException(404, "Contract not found")
    if int(user.get("role", 0)) != 2 and int(obj.get("created_user") or 0) != int(user["id"]):
        raise HTTPException(404, "Contract not found")
    return ApiResponse(result=obj)


@router.get("/{contract_id}/reviews", response_model=ApiResponse[list[dict]])
async def list_contract_reviews(contract_id: int, user: dict = Depends(get_current_user)):
    """根据合同ID获取合同审查记录，不分页，全部返回"""
    obj = await contract_service.get_contract_by_id(contract_id)
    if not obj:
        raise HTTPException(404, "Contract not found")
    if int(user.get("role", 0)) != 2 and int(obj.get("created_user") or 0) != int(user["id"]):
        raise HTTPException(404, "Contract not found")
    items = await contract_review_service.list_reviews_by_contract(contract_id)
    return ApiResponse(result=items)


@router.post("/", response_model=ApiResponse[ContractRead])
async def create_contract(payload: ContractCreate, user: dict = Depends(get_current_user)):
    data = payload.model_dump()
    data["created_user"] = int(user["id"])  # 记录创建人
    obj = await contract_service.create_contract(data)
    return ApiResponse(result=obj)


@router.put("/{contract_id}", response_model=ApiResponse[ContractRead])
async def update_contract(contract_id: int, payload: ContractUpdate, user: dict = Depends(get_current_user)):
    existing = await contract_service.get_contract_by_id(contract_id)
    if not existing or (int(user.get("role", 0)) != 2 and int(existing.get("created_user") or 0) != int(user["id"])):
        raise HTTPException(404, "Contract not found")
    obj = await contract_service.update_contract(contract_id, payload.model_dump(exclude_unset=True))
    if not obj:
        raise HTTPException(404, "Contract not found")
    return ApiResponse(result=obj)


@router.delete("/{contract_id}", response_model=ApiResponse[bool])
async def delete_contract(contract_id: int, user: dict = Depends(get_current_user)):
    existing = await contract_service.get_contract_by_id(contract_id)
    if not existing or (int(user.get("role", 0)) != 2 and int(existing.get("created_user") or 0) != int(user["id"])):
        raise HTTPException(404, "Contract not found")
    ok = await contract_service.delete_contract(contract_id)
    if not ok:
        raise HTTPException(404, "Contract not found")
    return ApiResponse(result=True)

