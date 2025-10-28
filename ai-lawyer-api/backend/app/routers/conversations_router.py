from fastapi import APIRouter, Query, HTTPException, Request, Depends

from ..db.db import get_pg_pool
from ..db.repositories import conversations_repo, messages_repo
from ..schemas.conversation import ConversationRead, ConversationRename, MessageRead
from ..schemas.response import ApiResponse
from ..common.pagination import Paginated, PageMeta
from ..common.params import PageParams


router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.get("/active", response_model=ApiResponse[Paginated[ConversationRead]])
async def list_active_conversations(
    request: Request,
    page_params: PageParams = Depends(),
) -> ApiResponse[Paginated[ConversationRead]]:
    pool = await get_pg_pool()
    user = getattr(request.state, "current_user", None)
    rows = await conversations_repo.get_active_by_user(pool, int(user["id"]))

    total = len(rows)
    start = (page_params.page - 1) * page_params.page_size
    end = start + page_params.page_size
    items = rows[start:end]

    return ApiResponse(result={
        "meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size),
        "items": items,
    })


@router.get("/{conversation_id}/messages", response_model=ApiResponse[list[MessageRead]])
async def list_messages(conversation_id: int, request: Request) -> ApiResponse[list[MessageRead]]:
    pool = await get_pg_pool()
    rows = await messages_repo.get_all_by_conversation(pool, conversation_id, asc=True)
    return ApiResponse(result=rows)


@router.delete("/{conversation_id}", response_model=ApiResponse[bool])
async def delete_conversation(conversation_id: int, request: Request) -> ApiResponse[bool]:
    pool = await get_pg_pool()
    ok = await conversations_repo.delete_with_messages(pool, conversation_id)
    if not ok:
        raise HTTPException(404, "Conversation not found")
    return ApiResponse(result=True)


@router.put("/{conversation_id}/title", response_model=ApiResponse[ConversationRead])
async def rename_conversation(conversation_id: int, payload: ConversationRename, request: Request) -> ApiResponse[ConversationRead]:
    pool = await get_pg_pool()
    updated = await conversations_repo.rename(pool, conversation_id, payload.title)
    if not updated:
        raise HTTPException(404, "Conversation not found")
    return ApiResponse(result=updated)  # type: ignore[return-value]
