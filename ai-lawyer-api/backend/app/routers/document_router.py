from fastapi import APIRouter, HTTPException, Depends, Query
from ..schemas.document_schema import DocumentCreate, DocumentUpdate, DocumentRead
from ..common.pagination import Paginated, PageMeta
from ..common.params import PageParams
from ..services import document_service
from ..schemas.response import ApiResponse
from ..security.auth import get_current_user

router = APIRouter(prefix="/documents", tags=["Document"])


@router.get("/", response_model=ApiResponse[Paginated[DocumentRead]])
async def list_documents(
    page_params: PageParams = Depends(),
    doc_name: str | None = Query(None, description="文书名称(模糊)"),
    doc_type: str | None = Query(None, description="文书类型"),
    user: dict = Depends(get_current_user),
):
    # 权限：0/1 仅看自己（根据 user_id）；2 管理员看全部
    uid = None if int(user.get("role", 0)) == 2 else int(user["id"])
    items, total = await document_service.list_documents_service(
        doc_name=doc_name,
        doc_type=doc_type,
        user_id=uid,
        page=page_params.page,
        page_size=page_params.page_size,
    )
    return ApiResponse(result={"meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size), "items": items})


@router.get("/{doc_id}", response_model=ApiResponse[DocumentRead])
async def get_document(doc_id: int, user: dict = Depends(get_current_user)):
    obj = await document_service.get_document_by_id(doc_id)
    if not obj:
        raise HTTPException(404, "Document not found")
    if int(user.get("role", 0)) != 2 and int(obj.get("user_id") or 0) != int(user["id"]):
        raise HTTPException(404, "Document not found")
    return ApiResponse(result=obj)


@router.post("/", response_model=ApiResponse[DocumentRead])
async def create_document(payload: DocumentCreate, user: dict = Depends(get_current_user)):
    data = payload.model_dump()
    # 强制归属当前用户（忽略外部传入 user_id）
    data["user_id"] = int(user["id"]) 
    obj = await document_service.create_document(data)
    return ApiResponse(result=obj)


@router.put("/{doc_id}", response_model=ApiResponse[DocumentRead])
async def update_document(doc_id: int, payload: DocumentUpdate, user: dict = Depends(get_current_user)):
    existing = await document_service.get_document_by_id(doc_id)
    if not existing or (int(user.get("role", 0)) != 2 and int(existing.get("user_id") or 0) != int(user["id"])):
        raise HTTPException(404, "Document not found")
    data = payload.model_dump(exclude_unset=True)
    if int(user.get("role", 0)) != 2 and "user_id" in data:
        # 非管理员不得变更归属
        data.pop("user_id", None)
    obj = await document_service.update_document(doc_id, data)
    if not obj:
        raise HTTPException(404, "Document not found")
    return ApiResponse(result=obj)


@router.delete("/{doc_id}", response_model=ApiResponse[bool])
async def delete_document(doc_id: int, user: dict = Depends(get_current_user)):
    existing = await document_service.get_document_by_id(doc_id)
    if not existing or (int(user.get("role", 0)) != 2 and int(existing.get("user_id") or 0) != int(user["id"])):
        raise HTTPException(404, "Document not found")
    ok = await document_service.delete_document(doc_id)
    if not ok:
        raise HTTPException(404, "Document not found")
    return ApiResponse(result=True)
