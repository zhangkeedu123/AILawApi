from fastapi import APIRouter, Depends
from ...schemas.content.content_prompt_schema import (
    ContentPromptCreate, ContentPromptUpdate, ContentPromptRead,
)
from ...common.pagination import Paginated, PageMeta
from ...common.params import PageParams
from ...services.content import content_prompt_service
from ...schemas.response import ApiResponse
from ...security.auth import get_current_user


router = APIRouter(prefix="/content/prompts", tags=["ContentPrompt"])


@router.get("/", response_model=ApiResponse[Paginated[ContentPromptRead]])
async def list_items(
    page_params: PageParams = Depends(),
    user: dict = Depends(get_current_user),
):
    employees_id = None if int(user.get("role", 0)) == 2 else int(user["id"])
    items, total = await content_prompt_service.list_service(
        employees_id=employees_id,
        page=page_params.page,
        page_size=page_params.page_size,
    )
    return ApiResponse(result={"meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size), "items": items})


@router.get("/{item_id}", response_model=ApiResponse[ContentPromptRead])
async def get_item(item_id: int, user: dict = Depends(get_current_user)):
    obj = await content_prompt_service.get_by_id(item_id)
    if not obj:
        return ApiResponse(status=False, msg="数据不存在")
    # 非管理员只能看自己的
    if int(user.get("role", 0)) != 2 and int(obj.get("employees_id") or 0) != int(user["id"]):
        return ApiResponse(status=False, msg="数据不存在")
    return ApiResponse(result=obj)


@router.post("/", response_model=ApiResponse[ContentPromptRead])
async def create_item(payload: ContentPromptCreate, user: dict = Depends(get_current_user)):
    data = payload.model_dump(exclude_unset=True)
    data["employees_id"] = int(user["id"]) if data.get("employees_id") is None else data["employees_id"]
    obj = await content_prompt_service.create(data)
    return ApiResponse(result=obj)


@router.put("/{item_id}", response_model=ApiResponse[ContentPromptRead])
async def update_item(item_id: int, payload: ContentPromptUpdate, user: dict = Depends(get_current_user)):
    existing = await content_prompt_service.get_by_id(item_id)
    if not existing or (int(user.get("role", 0)) != 2 and int(existing.get("employees_id") or 0) != int(user["id"])):
        return ApiResponse(status=False, msg="Item not found")
    obj = await content_prompt_service.update(item_id, payload.model_dump(exclude_unset=True))
    if not obj:
        return ApiResponse(status=False, msg="Item not found")
    return ApiResponse(result=obj)


@router.delete("/{item_id}", response_model=ApiResponse[bool])
async def delete_item(item_id: int, user: dict = Depends(get_current_user)):
    existing = await content_prompt_service.get_by_id(item_id)
    if not existing or (int(user.get("role", 0)) != 2 and int(existing.get("employees_id") or 0) != int(user["id"])):
        return ApiResponse(status=False, msg="Item not found")
    ok = await content_prompt_service.delete(item_id)
    if not ok:
        return ApiResponse(status=False, msg="Item not found")
    return ApiResponse(result=True)
