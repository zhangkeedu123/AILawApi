from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.firm_model import Firm

def list_firms_service(
    db: Session,
    name: Optional[str] = None,
    city: Optional[str] = None,
    status: Optional[str] = None,
    package: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Firm], int]:
    q = db.query(Firm)
    if name:
        q = q.filter(Firm.name.ilike(f"%{name}%"))
    if city:
        q = q.filter(Firm.city.ilike(f"%{city}%"))
    if status:
        q = q.filter(Firm.status == status)
    if package:
        q = q.filter(Firm.package == package)

    total = db.query(func.count()).select_from(q.subquery()).scalar()
    items = q.order_by(Firm.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return items, total
