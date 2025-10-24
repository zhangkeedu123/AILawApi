from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.case_model import Case

def list_cases_service(
    db: Session,
    name: Optional[str] = None,
    status: Optional[str] = None,
    location: Optional[str] = None,
    plaintiff: Optional[str] = None,
    defendant: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Case], int]:
    q = db.query(Case)
    if name:
        q = q.filter(Case.name.ilike(f"%{name}%"))
    if status:
        q = q.filter(Case.status == status)
    if location:
        q = q.filter(Case.location.ilike(f"%{location}%"))
    if plaintiff:
        q = q.filter(Case.plaintiff.ilike(f"%{plaintiff}%"))
    if defendant:
        q = q.filter(Case.defendant.ilike(f"%{defendant}%"))

    total = db.query(func.count()).select_from(q.subquery()).scalar()
    items = q.order_by(Case.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return items, total
