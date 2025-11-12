from fastapi import APIRouter, Depends, Query
from ...schemas.content.content_template_schema import (
    ContentTemplateCreate, ContentTemplateUpdate, ContentTemplateRead,
)
from ...common.pagination import Paginated, PageMeta
from ...common.params import PageParams
from ...services.content import content_template_service
from ...schemas.response import ApiResponse
from ...security.auth import get_current_user


router = APIRouter(prefix="/content/templates", tags=["ContentTemplate"])


@router.get("/", response_model=ApiResponse[Paginated[ContentTemplateRead]])
async def list_items(
    page_params: PageParams = Depends(),
    name: str | None = Query(None, description="名称(模糊)"),
    user: dict = Depends(get_current_user),
):
    items, total = await content_template_service.list_service(
        name=name,
        page=page_params.page,
        page_size=page_params.page_size,
    )
    return ApiResponse(result={"meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size), "items": items})


@router.get("/{item_id}", response_model=ApiResponse[ContentTemplateRead])
async def get_item(item_id: int, user: dict = Depends(get_current_user)):
    obj = await content_template_service.get_by_id(item_id)
    if not obj:
        return ApiResponse(status=False, msg="数据不存在")
    return ApiResponse(result=obj)


@router.post("/", response_model=ApiResponse[ContentTemplateRead])
async def create_item(payload: ContentTemplateCreate, user: dict = Depends(get_current_user)):
    obj = await content_template_service.create(payload.model_dump(exclude_unset=True))
    return ApiResponse(result=obj)


@router.put("/{item_id}", response_model=ApiResponse[ContentTemplateRead])
async def update_item(item_id: int, payload: ContentTemplateUpdate, user: dict = Depends(get_current_user)):
    obj = await content_template_service.update(item_id, payload.model_dump(exclude_unset=True))
    if not obj:
        return ApiResponse(status=False, msg="操作失败")
    return ApiResponse(result=obj)


@router.delete("/{item_id}", response_model=ApiResponse[bool])
async def delete_item(item_id: int, user: dict = Depends(get_current_user)):
    ok = await content_template_service.delete(item_id)
    if not ok:
        return ApiResponse(status=False, msg="操作失败")
    return ApiResponse(result=True)
