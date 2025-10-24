from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.document_model import Document

def list_documents_service(
    db: Session,
    doc_name: Optional[str] = None,
    case_name: Optional[str] = None,
    doc_type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Document], int]:
    q = db.query(Document)
    if doc_name:
        q = q.filter(Document.docName.ilike(f"%{doc_name}%"))
    if case_name:
        q = q.filter(Document.caseName.ilike(f"%{case_name}%"))
    if doc_type:
        q = q.filter(Document.docType == doc_type)
    if status:
        q = q.filter(Document.status == status)

    total = db.query(func.count()).select_from(q.subquery()).scalar()
    items = q.order_by(Document.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return items, total
