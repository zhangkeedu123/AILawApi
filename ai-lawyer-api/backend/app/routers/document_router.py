from fastapi import APIRouter, HTTPException, Depends, Query
from ..schemas.document_schema import DocumentCreate, DocumentUpdate, DocumentRead
from ..common.pagination import Paginated, PageMeta
from ..common.params import PageParams
from ..services import document_service

router = APIRouter(prefix="/documents", tags=["Document"])


@router.get("/", response_model=Paginated[DocumentRead])
async def list_documents(
    page_params: PageParams = Depends(),
    doc_name: str | None = Query(None, description="文书名称(模糊)"),
    case_name: str | None = Query(None, description="案件名称(模糊)"),
    doc_type: str | None = Query(None, description="文书类型"),
    status: str | None = Query(None, description="状态"),
):
    items, total = await document_service.list_documents_service(
        doc_name=doc_name, case_name=case_name, doc_type=doc_type, status=status,
        page=page_params.page, page_size=page_params.page_size,
    )
    return {"meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size), "items": items}


@router.get("/{doc_id}", response_model=DocumentRead)
async def get_document(doc_id: int):
    obj = await document_service.get_document_by_id(doc_id)
    if not obj:
        raise HTTPException(404, "Document not found")
    return obj


@router.post("/", response_model=DocumentRead)
async def create_document(payload: DocumentCreate):
    obj = await document_service.create_document(payload.model_dump())
    return obj


@router.put("/{doc_id}", response_model=DocumentRead)
async def update_document(doc_id: int, payload: DocumentUpdate):
    obj = await document_service.update_document(doc_id, payload.model_dump(exclude_unset=True))
    if not obj:
        raise HTTPException(404, "Document not found")
    return obj


@router.delete("/{doc_id}")
async def delete_document(doc_id: int):
    ok = await document_service.delete_document(doc_id)
    if not ok:
        raise HTTPException(404, "Document not found")
    return {"ok": True}

