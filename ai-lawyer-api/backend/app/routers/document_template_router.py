from fastapi import APIRouter, Depends, HTTPException, Query

from ..common.pagination import Paginated, PageMeta
from ..common.params import PageParams
from ..schemas.document_template_schema import (
    DocumentTemplateCreate,
    DocumentTemplateRead,
    DocumentTemplateUpdate,
)
from ..schemas.response import ApiResponse
from ..security.auth import get_current_user
from ..services import document_template_service


router = APIRouter(prefix="/document-templates", tags=["DocumentTemplate"])


@router.get("/", response_model=ApiResponse[Paginated[DocumentTemplateRead]])
async def list_document_templates(
    page_params: PageParams = Depends(),
    name: str | None = Query(None, description="文书模板名称(模糊)"),
    p_id: int | None = Query(None, description="父级ID，默认为顶级"),
    user: dict = Depends(get_current_user),
):
    items, total = await document_template_service.list_document_templates_service(
        name=name,
        p_id=p_id,
        page=page_params.page,
        page_size=page_params.page_size,
    )
    return ApiResponse(
        result={
            "meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size),
            "items": items,
        }
    )


@router.get("/{template_id}", response_model=ApiResponse[DocumentTemplateRead])
async def get_document_template(template_id: int, user: dict = Depends(get_current_user)):
    obj = await document_template_service.get_document_template_by_id(template_id)
    if not obj:
        return ApiResponse(result=False,msg="数据不存在")
    return ApiResponse(result=obj)


@router.post("/", response_model=ApiResponse[DocumentTemplateRead])
async def create_document_template(payload: DocumentTemplateCreate, user: dict = Depends(get_current_user)):
    obj = await document_template_service.create_document_template(payload.model_dump())
    return ApiResponse(result=obj)


@router.put("/{template_id}", response_model=ApiResponse[DocumentTemplateRead])
async def update_document_template(
    template_id: int,
    payload: DocumentTemplateUpdate,
    user: dict = Depends(get_current_user),
):
    obj = await document_template_service.update_document_template(
        template_id, payload.model_dump(exclude_unset=True)
    )
    if not obj:
        return ApiResponse(result=False,msg="编辑失败")
    return ApiResponse(result=obj)


@router.delete("/{template_id}", response_model=ApiResponse[bool])
async def delete_document_template(template_id: int, user: dict = Depends(get_current_user)):
    ok = await document_template_service.delete_document_template(template_id)
    if not ok:
        return ApiResponse(result=False,msg="删除失败")
    return ApiResponse(status=True)
