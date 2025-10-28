from fastapi import APIRouter, Request
from ..schemas.conversation import ChatRequest, ChatResponse
from ..schemas.response import ApiResponse
from ..services import conversation_service

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("", response_model=ApiResponse[ChatResponse])
async def chat_endpoint(payload: ChatRequest, request: Request) -> ApiResponse[ChatResponse]:
    user = getattr(request.state, "current_user", None)
    user_id = int(user["id"]) if user else None
    reply = await conversation_service.ask(user_id, payload.question)
    return ApiResponse(result=ChatResponse(reply=reply))
