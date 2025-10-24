from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.spider_model import SpiderCustomer

def list_spider_customers_service(
    db: Session,
    name: Optional[str] = None,
    city: Optional[str] = None,
    platform: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[SpiderCustomer], int]:
    q = db.query(SpiderCustomer)
    if name:
        q = q.filter(SpiderCustomer.name.ilike(f"%{name}%"))
    if city:
        q = q.filter(SpiderCustomer.city.ilike(f"%{city}%"))
    if platform:
        q = q.filter(SpiderCustomer.platform == platform)
    if status:
        q = q.filter(SpiderCustomer.status == status)

    total = db.query(func.count()).select_from(q.subquery()).scalar()
    items = q.order_by(SpiderCustomer.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return items, total
