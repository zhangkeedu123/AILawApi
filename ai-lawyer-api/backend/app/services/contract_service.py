from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.contract_model import Contract

def list_contracts_service(
    db: Session,
    customer: Optional[str] = None,
    type_: Optional[str] = None,
    status: Optional[str] = None,
    upload_date_from: Optional[str] = None,  # 'YYYY-MM-DD'
    upload_date_to: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Contract], int]:
    q = db.query(Contract)
    if customer:
        q = q.filter(Contract.customer.ilike(f"%{customer}%"))
    if type_:
        q = q.filter(Contract.type == type_)
    if status:
        q = q.filter(Contract.status == status)
    if upload_date_from:
        q = q.filter(Contract.uploadDate >= upload_date_from)
    if upload_date_to:
        q = q.filter(Contract.uploadDate <= upload_date_to)

    total = db.query(func.count()).select_from(q.subquery()).scalar()
    items = q.order_by(Contract.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return items, total
