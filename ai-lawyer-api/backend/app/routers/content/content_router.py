from fastapi import APIRouter, Depends, Query
from ...schemas.content.content_schema import (
    ContentCreate, ContentUpdate, ContentRead,
)
from ...common.pagination import Paginated, PageMeta
from ...common.params import PageParams
from ...services.content import content_service
from ...schemas.response import ApiResponse
from ...security.auth import get_current_user


router = APIRouter(prefix="/content/contents", tags=["Content"])


@router.get("/", response_model=ApiResponse[Paginated[ContentRead]])
async def list_items(
    page_params: PageParams = Depends(),
    title: str | None = Query(None, description="标题(模糊)"),
    user: dict = Depends(get_current_user),
):
    employees_id = None if int(user.get("role", 0)) == 2 else int(user["id"])
    items, total = await content_service.list_service(
        title=title,
        employees_id=employees_id,
        page=page_params.page,
        page_size=page_params.page_size,
    )
    return ApiResponse(result={"meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size), "items": items})


@router.get("/{item_id}", response_model=ApiResponse[ContentRead])
async def get_item(item_id: int, user: dict = Depends(get_current_user)):
    obj = await content_service.get_by_id(item_id)
    if not obj:
        return ApiResponse(status=False, msg="数据不存在")
    if int(user.get("role", 0)) != 2 and int(obj.get("employees_id") or 0) != int(user["id"]):
        return ApiResponse(status=False, msg="数据不存在")
    return ApiResponse(result=obj)


@router.post("/", response_model=ApiResponse[ContentRead])
async def create_item(payload: ContentCreate, user: dict = Depends(get_current_user)):
    data = payload.model_dump(exclude_unset=True)
    data["employees_id"] = int(user["id"]) if data.get("employees_id") is None else data["employees_id"]
    obj = await content_service.create(data)
    return ApiResponse(result=obj)


@router.put("/{item_id}", response_model=ApiResponse[ContentRead])
async def update_item(item_id: int, payload: ContentUpdate, user: dict = Depends(get_current_user)):
    existing = await content_service.get_by_id(item_id)
    if not existing or (int(user.get("role", 0)) != 2 and int(existing.get("employees_id") or 0) != int(user["id"])):
        return ApiResponse(status=False, msg="没有权限")
    obj = await content_service.update(item_id, payload.model_dump(exclude_unset=True))
    if not obj:
        return ApiResponse(status=False, msg="操作失败")
    return ApiResponse(result=obj)


@router.delete("/{item_id}", response_model=ApiResponse[bool])
async def delete_item(item_id: int, user: dict = Depends(get_current_user)):
    existing = await content_service.get_by_id(item_id)
    if not existing or (int(user.get("role", 0)) != 2 and int(existing.get("employees_id") or 0) != int(user["id"])):
        return ApiResponse(status=False, msg="没有权限")
    ok = await content_service.delete(item_id)
    if not ok:
        return ApiResponse(status=False, msg="操作失败")
    return ApiResponse(result=True)
