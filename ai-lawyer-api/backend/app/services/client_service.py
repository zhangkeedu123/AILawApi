from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.client_model import Client

def list_clients_service(
    db: Session,
    name: Optional[str] = None,
    type_: Optional[str] = None,
    status: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Client], int]:
    q = db.query(Client)
    if name:
        q = q.filter(Client.name.ilike(f"%{name}%"))
    if type_:
        q = q.filter(Client.type == type_)
    if status:
        q = q.filter(Client.status == status)
    if phone:
        q = q.filter(Client.phone.ilike(f"%{phone}%"))
    if email:
        q = q.filter(Client.email.ilike(f"%{email}%"))

    total = db.query(func.count(Client.id)).scalar() if q._distinct is None else q.count()
    # 更稳妥：用一个不带limit/offset的副本做count
    total = db.query(func.count()).select_from(q.subquery()).scalar() if q._limit is not None or q._offset is not None else db.query(func.count()).select_from(Client).filter(*q._criterion) if getattr(q, "_criterion", None) else db.query(func.count(Client.id)).scalar()

    # 简洁且正确的方式：构造count子查询
    total = db.query(func.count()).select_from(q.subquery()).scalar()

    items = q.order_by(Client.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return items, total
