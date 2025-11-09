from fastapi import APIRouter, Depends, Query
from ..schemas.employee_schema import EmployeeCreate, EmployeeUpdate, EmployeeRead
from ..common.pagination import Paginated, PageMeta
from ..common.params import PageParams
from ..services import employee_service
from ..schemas.response import ApiResponse
from ..security.auth import get_current_user


router = APIRouter(prefix="/employees", tags=["Employee"])


@router.get("/", response_model=ApiResponse[Paginated[EmployeeRead]])
async def list_employees(
    page_params: PageParams = Depends(),
    name: str | None = Query(None, description="姓名(模糊)"),
    firm_name: str | None = Query(None, description="所属律所(模糊)"),
    user: dict = Depends(get_current_user),
):
    # 0/1 仅查询同律所员工；2 管理员查全部
    only_firm_id = None if int(user.get("role", 0)) == 2 else str(user.get("firm_id") or "")
    items, total = await employee_service.list_employees_service(
        name=name,
        firm_name=firm_name,
        firm_id=only_firm_id,
        page=page_params.page,
        page_size=page_params.page_size,
    )
    return ApiResponse(result={
        "meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size),
        "items": items,
    })


@router.get("/{emp_id}", response_model=ApiResponse[EmployeeRead])
async def get_employee(emp_id: int, user: dict = Depends(get_current_user)):
    obj = await employee_service.get_employee_by_id(emp_id)
    if not obj:
        return ApiResponse(status=False, result=None, msg="员工不存在")
    # 非管理员仅能查看同律所员工
    if int(user.get("role", 0)) != 2 and str(obj.get("firm_id") or "") != str(user.get("firm_id") or ""):
        return ApiResponse(status=False, result=None, msg="无权限查看")
    return ApiResponse(result=obj)


@router.post("/", response_model=ApiResponse[EmployeeRead])
async def create_employee(payload: EmployeeCreate, user: dict = Depends(get_current_user)):
    # 仅允许 role=1/2；role=1 仅能在本律所创建，并强制归属其律所
    role = int(user.get("role", 0))
    if role not in (1, 2):
        return ApiResponse(status=False, result=None, msg="无权限创建")
    try:
        data = payload.model_dump()
        if role == 1:
            data["firm_id"] = str(user.get("firm_id") or "")
            data["firm_name"] = str(user.get("firm_name") or "")
        obj = await employee_service.create_employee(data)
        if not obj:
            return ApiResponse(status=False, result=None, msg="创建失败")
        return ApiResponse(result=obj)
    except Exception:
        return ApiResponse(status=False, result=None, msg="创建失败")


@router.put("/{emp_id}", response_model=ApiResponse[EmployeeRead])
async def update_employee(emp_id: int, payload: EmployeeUpdate, user: dict = Depends(get_current_user)):
    # 仅允许 role=1/2；role=1 仅能修改同律所员工，且不得跨律所
    role = int(user.get("role", 0))
    if role not in (1, 2):
        return ApiResponse(status=False, result=None, msg="无权限更新")
    existing = await employee_service.get_employee_by_id(emp_id)
    if not existing:
        return ApiResponse(status=False, result=None, msg="员工不存在")
    if role == 1 and str(existing.get("firm_id") or "") != str(user.get("firm_id") or ""):
        return ApiResponse(status=False, result=None, msg="无权限更新")
    try:
        data = payload.model_dump(exclude_unset=True)
        if role == 1:
            # 店长不可修改员工归属律所
            data.pop("firm_id", None)
            data.pop("firm_name", None)
        obj = await employee_service.update_employee(emp_id, data)
        if not obj:
            return ApiResponse(status=False, result=None, msg="员工不存在")
        return ApiResponse(result=obj)
    except Exception:
        return ApiResponse(status=False, result=None, msg="更新失败")


@router.delete("/{emp_id}", response_model=ApiResponse[bool])
async def delete_employee(emp_id: int, user: dict = Depends(get_current_user)):
    # 仅允许 role=1/2；role=1 仅能删除同律所员工
    role = int(user.get("role", 0))
    if role not in (1, 2):
        return ApiResponse(status=False, result=False, msg="无权限删除")
    existing = await employee_service.get_employee_by_id(emp_id)
    if not existing:
        return ApiResponse(status=False, result=False, msg="员工不存在")
    if role == 1 and str(existing.get("firm_id") or "") != str(user.get("firm_id") or ""):
        return ApiResponse(status=False, result=False, msg="无权限删除")
    try:
        ok = await employee_service.delete_employee(emp_id)
        if not ok:
            return ApiResponse(status=False, result=False, msg="员工不存在")
        return ApiResponse(result=True)
    except Exception:
        return ApiResponse(status=False, result=False, msg="删除失败")

