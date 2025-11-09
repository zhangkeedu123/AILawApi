from fastapi import APIRouter, HTTPException, Depends, Query
from ..schemas.case_schema import CaseCreate, CaseUpdate, CaseRead
from ..common.pagination import Paginated, PageMeta
from ..common.params import PageParams
from ..services import case_service
from ..schemas.response import ApiResponse
from ..security.auth import get_current_user


router = APIRouter(prefix="/cases", tags=["Case"])


@router.get("/", response_model=ApiResponse[Paginated[CaseRead]])
async def list_cases(
    page_params: PageParams = Depends(),
    name: str | None = Query(None, description="案件名称(模糊)"),
    status: str | None = Query(None, description="案件状态"),
    location: str | None = Query(None, description="地点(模糊)"),
    plaintiff: str | None = Query(None, description="原告(模糊)"),
    defendant: str | None = Query(None, description="被告(模糊)"),
    user: dict = Depends(get_current_user),
):
    # 权限：0 员工、1 店长 仅看自己；2 管理员看全部
    created_user = None if int(user.get("role", 0)) == 2 else int(user["id"])
    items, total = await case_service.list_cases_service(
        name=name,
        status=status,
        location=location,
        plaintiff=plaintiff,
        defendant=defendant,
        created_user=created_user,
        page=page_params.page,
        page_size=page_params.page_size,
    )
    return ApiResponse(result={
        "meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size),
        "items": items,
    })


@router.get("/{case_id}", response_model=ApiResponse[CaseRead])
async def get_case(case_id: int, user: dict = Depends(get_current_user)):
    obj = await case_service.get_case_by_id(case_id)
    if not obj:
        raise HTTPException(404, "Case not found")
    # 非管理员仅能获取自己创建的数据
    if int(user.get("role", 0)) != 2 and int(obj.get("created_user") or 0) != int(user["id"]):
        raise HTTPException(404, "Case not found")
    return ApiResponse(result=obj)


@router.post("/", response_model=ApiResponse[CaseRead])
async def create_case(payload: CaseCreate, user: dict = Depends(get_current_user)):
    data = payload.model_dump()
    data["created_user"] = int(user["id"])  # 记录创建人
    obj = await case_service.create_case(data)
    return ApiResponse(result=obj)


@router.put("/{case_id}", response_model=ApiResponse[CaseRead])
async def update_case(case_id: int, payload: CaseUpdate, user: dict = Depends(get_current_user)):
    # 非管理员仅能更新自己创建的数据
    existing = await case_service.get_case_by_id(case_id)
    if not existing or (int(user.get("role", 0)) != 2 and int(existing.get("created_user") or 0) != int(user["id"])):
        raise HTTPException(404, "Case not found")
    obj = await case_service.update_case(case_id, payload.model_dump(exclude_unset=True))
    if not obj:
        raise HTTPException(404, "Case not found")
    return ApiResponse(result=obj)


@router.delete("/{case_id}", response_model=ApiResponse[bool])
async def delete_case(case_id: int, user: dict = Depends(get_current_user)):
    # 非管理员仅能删除自己创建的数据
    existing = await case_service.get_case_by_id(case_id)
    if not existing or (int(user.get("role", 0)) != 2 and int(existing.get("created_user") or 0) != int(user["id"])):
        raise HTTPException(404, "Case not found")
    ok = await case_service.delete_case(case_id)
    if not ok:
        raise HTTPException(404, "Case not found")
    return ApiResponse(result=True)

