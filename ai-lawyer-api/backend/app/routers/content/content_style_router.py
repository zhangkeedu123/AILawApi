from fastapi import APIRouter, Depends, Query
from ...schemas.content.content_style_schema import (
    ContentStyleCreate, ContentStyleUpdate, ContentStyleRead,
)
from ...common.pagination import Paginated, PageMeta
from ...common.params import PageParams
from ...services.content import content_style_service
from ...schemas.response import ApiResponse
from ...security.auth import get_current_user


router = APIRouter(prefix="/content/style-guides", tags=["ContentStyle"])


@router.get("/", response_model=ApiResponse[Paginated[ContentStyleRead]])
async def list_items(
    page_params: PageParams = Depends(),
    tone: str | None = Query(None, description="语气(模糊)"),
    reading_level: str | None = Query(None, description="阅读层级(模糊)"),
    user: dict = Depends(get_current_user),
):
    items, total = await content_style_service.list_service(
        tone=tone,
        reading_level=reading_level,
        page=page_params.page,
        page_size=page_params.page_size,
    )
    return ApiResponse(result={"meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size), "items": items})


@router.get("/{item_id}", response_model=ApiResponse[ContentStyleRead])
async def get_item(item_id: int, user: dict = Depends(get_current_user)):
    obj = await content_style_service.get_by_id(item_id)
    if not obj:
        return ApiResponse(status=False, msg="数据不存在")
    return ApiResponse(result=obj)


@router.post("/", response_model=ApiResponse[ContentStyleRead])
async def create_item(payload: ContentStyleCreate, user: dict = Depends(get_current_user)):
    obj = await content_style_service.create(payload.model_dump(exclude_unset=True))
    return ApiResponse(result=obj)


@router.put("/{item_id}", response_model=ApiResponse[ContentStyleRead])
async def update_item(item_id: int, payload: ContentStyleUpdate, user: dict = Depends(get_current_user)):
    obj = await content_style_service.update(item_id, payload.model_dump(exclude_unset=True))
    if not obj:
        return ApiResponse(status=False, msg="操作失败")
    return ApiResponse(result=obj)


@router.delete("/{item_id}", response_model=ApiResponse[bool])
async def delete_item(item_id: int, user: dict = Depends(get_current_user)):
    ok = await content_style_service.delete(item_id)
    if not ok:
        return ApiResponse(status=False, msg="操作失败")
    return ApiResponse(result=True)
