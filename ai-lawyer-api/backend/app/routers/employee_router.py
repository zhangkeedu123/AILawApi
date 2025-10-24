from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from ..models.employee_model import Employee
from ..schemas.employee_schema import EmployeeCreate, EmployeeUpdate, EmployeeRead
from ..deps import db_dep
from ..common.pagination import Paginated, PageMeta
from ..common.params import PageParams
from ..services.employee_service import list_employees_service

router = APIRouter(prefix="/employees", tags=["Employee"])

@router.get("/", response_model=Paginated[EmployeeRead])
def list_employees(
    page_params: PageParams = Depends(),
    name: str | None = Query(None, description="姓名(模糊)"),
    title: str | None = Query(None, description="职称/职位(模糊)"),
    firm_name: str | None = Query(None, description="所属律所(模糊)"),
    status: str | None = Query(None, description="状态"),
    db: Session = Depends(db_dep),
):
    items, total = list_employees_service(
        db, name=name, title=title, firm_name=firm_name, status=status,
        page=page_params.page, page_size=page_params.page_size
    )
    return {"meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size), "items": items}

@router.get("/{emp_id}", response_model=EmployeeRead)
def get_employee(emp_id: int, db: Session = Depends(db_dep)):
    obj = db.get(Employee, emp_id)
    if not obj:
        raise HTTPException(404, "Employee not found")
    return obj

@router.post("/", response_model=EmployeeRead)
def create_employee(payload: EmployeeCreate, db: Session = Depends(db_dep)):
    obj = Employee(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.put("/{emp_id}", response_model=EmployeeRead)
def update_employee(emp_id: int, payload: EmployeeUpdate, db: Session = Depends(db_dep)):
    obj = db.get(Employee, emp_id)
    if not obj:
        raise HTTPException(404, "Employee not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{emp_id}")
def delete_employee(emp_id: int, db: Session = Depends(db_dep)):
    obj = db.get(Employee, emp_id)
    if not obj:
        raise HTTPException(404, "Employee not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}
