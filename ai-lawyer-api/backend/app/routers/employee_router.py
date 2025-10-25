from fastapi import APIRouter, HTTPException, Depends, Query
from ..schemas.employee_schema import EmployeeCreate, EmployeeUpdate, EmployeeRead
from ..common.pagination import Paginated, PageMeta
from ..common.params import PageParams
from ..services import employee_service

router = APIRouter(prefix="/employees", tags=["Employee"])


@router.get("/", response_model=Paginated[EmployeeRead])
async def list_employees(
    page_params: PageParams = Depends(),
    name: str | None = Query(None, description="姓名(模糊)"),
    title: str | None = Query(None, description="职称/职位(模糊)"),
    firm_name: str | None = Query(None, description="所属律所(模糊)"),
    status: str | None = Query(None, description="状态"),
):
    items, total = await employee_service.list_employees_service(
        name=name, title=title, firm_name=firm_name, status=status,
        page=page_params.page, page_size=page_params.page_size,
    )
    return {"meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size), "items": items}


@router.get("/{emp_id}", response_model=EmployeeRead)
async def get_employee(emp_id: int):
    obj = await employee_service.get_employee_by_id(emp_id)
    if not obj:
        raise HTTPException(404, "Employee not found")
    return obj


@router.post("/", response_model=EmployeeRead)
async def create_employee(payload: EmployeeCreate):
    obj = await employee_service.create_employee(payload.model_dump())
    return obj


@router.put("/{emp_id}", response_model=EmployeeRead)
async def update_employee(emp_id: int, payload: EmployeeUpdate):
    obj = await employee_service.update_employee(emp_id, payload.model_dump(exclude_unset=True))
    if not obj:
        raise HTTPException(404, "Employee not found")
    return obj


@router.delete("/{emp_id}")
async def delete_employee(emp_id: int):
    ok = await employee_service.delete_employee(emp_id)
    if not ok:
        raise HTTPException(404, "Employee not found")
    return {"ok": True}

