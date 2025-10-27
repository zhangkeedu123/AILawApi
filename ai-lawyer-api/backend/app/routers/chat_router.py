from fastapi import APIRouter
from ..schemas.conversation import ChatRequest, ChatResponse
from ..schemas.response import ApiResponse
from ..services import conversation_service

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("", response_model=ApiResponse[ChatResponse])
async def chat_endpoint(payload: ChatRequest) -> ApiResponse[ChatResponse]:
    reply = await conversation_service.ask(payload.user_id, payload.question)
    return ApiResponse(result=ChatResponse(reply=reply))
