from fastapi import APIRouter
from ..schemas.conversation import ChatRequest, ChatResponse
from ..services import conversation_service

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest) -> ChatResponse:
    reply = await conversation_service.ask(payload.user_id, payload.question)
    return ChatResponse(reply=reply)
