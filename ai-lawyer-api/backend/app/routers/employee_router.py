from fastapi import APIRouter, HTTPException, Depends, Query
from ..schemas.employee_schema import EmployeeCreate, EmployeeUpdate, EmployeeRead
from ..common.pagination import Paginated, PageMeta
from ..common.params import PageParams
from ..services import employee_service
from ..schemas.response import ApiResponse

router = APIRouter(prefix="/employees", tags=["Employee"])


@router.get("/", response_model=ApiResponse[Paginated[EmployeeRead]])
async def list_employees(
    page_params: PageParams = Depends(),
    name: str | None = Query(None, description="姓名(模糊)"),
    firm_name: str | None = Query(None, description="所属律所(模糊)"),
):
    items, total = await employee_service.list_employees_service(
        name=name,  firm_name=firm_name, 
        page=page_params.page, page_size=page_params.page_size,
    )
    return ApiResponse(result={"meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size), "items": items})


@router.get("/{emp_id}", response_model=ApiResponse[EmployeeRead])
async def get_employee(emp_id: int):
    obj = await employee_service.get_employee_by_id(emp_id)
    if not obj:
        return ApiResponse(status=False, result=None, msg="员工不存在")
    return ApiResponse(result=obj)


@router.post("/", response_model=ApiResponse[EmployeeRead])
async def create_employee(payload: EmployeeCreate):
    try:
        obj = await employee_service.create_employee(payload.model_dump())
        if not obj:
            return ApiResponse(status=False, result=None, msg="创建失败")
        return ApiResponse(result=obj)
    except HTTPException as e:
        detail = getattr(e, "detail", None) or str(e)
        return ApiResponse(status=False, result=None, msg=str(detail))
    except Exception:
        return ApiResponse(status=False, result=None, msg="创建失败")


@router.put("/{emp_id}", response_model=ApiResponse[EmployeeRead])
async def update_employee(emp_id: int, payload: EmployeeUpdate):
    try:
        obj = await employee_service.update_employee(emp_id, payload.model_dump(exclude_unset=True))
        if not obj:
            return ApiResponse(status=False, result=None, msg="员工不存在")
        return ApiResponse(result=obj)
    except HTTPException as e:
        detail = getattr(e, "detail", None) or str(e)
        return ApiResponse(status=False, result=None, msg=str(detail))
    except Exception:
        return ApiResponse(status=False, result=None, msg="更新失败")


@router.delete("/{emp_id}", response_model=ApiResponse[bool])
async def delete_employee(emp_id: int):
    try:
        ok = await employee_service.delete_employee(emp_id)
        if not ok:
            return ApiResponse(status=False, result=False, msg="员工不存在")
        return ApiResponse(result=True)
    except Exception:
        return ApiResponse(status=False, result=False, msg="删除失败")
