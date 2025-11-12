from fastapi import APIRouter, Depends, Query
from ...schemas.content.content_idea_schema import (
    ContentIdeaCreate, ContentIdeaUpdate, ContentIdeaRead,
)
from ...common.pagination import Paginated, PageMeta
from ...common.params import PageParams
from ...services.content import content_idea_service
from ...schemas.response import ApiResponse
from ...security.auth import get_current_user


router = APIRouter(prefix="/content/ideas", tags=["ContentIdea"])


@router.get("/", response_model=ApiResponse[Paginated[ContentIdeaRead]])
async def list_items(
    page_params: PageParams = Depends(),
    title: str | None = Query(None, description="标题(模糊)"),
    persona: str | None = Query(None, description="读者画像(模糊)"),
    keywords: str | None = Query(None, description="关键词(模糊)"),
    user: dict = Depends(get_current_user),
):
    items, total = await content_idea_service.list_service(
        title=title,
        persona=persona,
        keywords=keywords,
        page=page_params.page,
        page_size=page_params.page_size,
    )
    return ApiResponse(result={"meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size), "items": items})


@router.get("/{item_id}", response_model=ApiResponse[ContentIdeaRead])
async def get_item(item_id: int, user: dict = Depends(get_current_user)):
    obj = await content_idea_service.get_by_id(item_id)
    if not obj:
        return ApiResponse(status=False, msg="数据不存在")
    return ApiResponse(result=obj)


@router.post("/", response_model=ApiResponse[ContentIdeaRead])
async def create_item(payload: ContentIdeaCreate, user: dict = Depends(get_current_user)):
    obj = await content_idea_service.create(payload.model_dump(exclude_unset=True))
    return ApiResponse(result=obj)


@router.put("/{item_id}", response_model=ApiResponse[ContentIdeaRead])
async def update_item(item_id: int, payload: ContentIdeaUpdate, user: dict = Depends(get_current_user)):
    obj = await content_idea_service.update(item_id, payload.model_dump(exclude_unset=True))
    if not obj:
        return ApiResponse(status=False, msg="Item not found")
    return ApiResponse(result=obj)


@router.delete("/{item_id}", response_model=ApiResponse[bool])
async def delete_item(item_id: int, user: dict = Depends(get_current_user)):
    ok = await content_idea_service.delete(item_id)
    if not ok:
        return ApiResponse(status=False, msg="Item not found")
    return ApiResponse(result=True)
