from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from ..models.document_model import Document
from ..schemas.document_schema import DocumentCreate, DocumentUpdate, DocumentRead
from ..deps import db_dep
from ..common.pagination import Paginated, PageMeta
from ..common.params import PageParams
from ..services.document_service import list_documents_service

router = APIRouter(prefix="/documents", tags=["Document"])

@router.get("/", response_model=Paginated[DocumentRead])
def list_documents(
    page_params: PageParams = Depends(),
    doc_name: str | None = Query(None, description="文书名称(模糊)"),
    case_name: str | None = Query(None, description="案件名称(模糊)"),
    doc_type: str | None = Query(None, description="文书类型"),
    status: str | None = Query(None, description="状态"),
    db: Session = Depends(db_dep),
):
    items, total = list_documents_service(
        db, doc_name=doc_name, case_name=case_name, doc_type=doc_type, status=status,
        page=page_params.page, page_size=page_params.page_size
    )
    return {"meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size), "items": items}

@router.get("/{doc_id}", response_model=DocumentRead)
def get_document(doc_id: int, db: Session = Depends(db_dep)):
    obj = db.get(Document, doc_id)
    if not obj:
        raise HTTPException(404, "Document not found")
    return obj

@router.post("/", response_model=DocumentRead)
def create_document(payload: DocumentCreate, db: Session = Depends(db_dep)):
    obj = Document(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.put("/{doc_id}", response_model=DocumentRead)
def update_document(doc_id: int, payload: DocumentUpdate, db: Session = Depends(db_dep)):
    obj = db.get(Document, doc_id)
    if not obj:
        raise HTTPException(404, "Document not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(db_dep)):
    obj = db.get(Document, doc_id)
    if not obj:
        raise HTTPException(404, "Document not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}
