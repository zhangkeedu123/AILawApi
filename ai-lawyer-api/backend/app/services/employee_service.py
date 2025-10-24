from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.employee_model import Employee

def list_employees_service(
    db: Session,
    name: Optional[str] = None,
    title: Optional[str] = None,
    firm_name: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Employee], int]:
    q = db.query(Employee)
    if name:
        q = q.filter(Employee.name.ilike(f"%{name}%"))
    if title:
        q = q.filter(Employee.title.ilike(f"%{title}%"))
    if firm_name:
        q = q.filter(Employee.firm_name.ilike(f"%{firm_name}%"))
    if status:
        q = q.filter(Employee.status == status)

    total = db.query(func.count()).select_from(q.subquery()).scalar()
    items = q.order_by(Employee.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return items, total
