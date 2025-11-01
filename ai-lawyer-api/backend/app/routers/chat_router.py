from fastapi import APIRouter, Request
from ..schemas.conversation import ChatRequest, ChatResponse
from ..schemas.response import ApiResponse
from ..services import conversation_service, chat_service
from ..schemas.case_schema import CaseExtractResult

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ApiResponse[ChatResponse])
async def chat_endpoint(payload: ChatRequest, request: Request) -> ApiResponse[ChatResponse]:
    user = getattr(request.state, "current_user", None)
    user_id = int(user["id"]) if user else None
    reply, cid, title = await conversation_service.ask(user_id, payload.question, payload.conv_id or 0)
    return ApiResponse(result=ChatResponse(reply=reply, conv_id=cid, title=title))


@router.post("/analyze", response_model=ApiResponse[ChatResponse])
async def analyze_case(payload: ChatRequest) -> ApiResponse[ChatResponse]:
    """直接调用 AI 进行案件分析。"""
    reply = await chat_service.analyze_case_ai(payload.question)
    return ApiResponse(result=ChatResponse(reply=reply, conv_id=0, title=None))


@router.post("/extract_case", response_model=ApiResponse[CaseExtractResult])
async def extract_case_info(payload: ChatRequest) -> ApiResponse[CaseExtractResult]:
    """调用 service 使用 AI 提取案件信息，仅返回严格的五个字段。"""
    result = await chat_service.extract_case_info_ai(payload.question)
    return ApiResponse(result=result)


@router.post("/contract_review", response_model=ApiResponse[ChatResponse])
async def contract_review(payload: ChatRequest) -> ApiResponse[ChatResponse]:
    """AI 合同审查：将合同文本交给 service，返回严格 JSON（字符串载荷）。"""
    reply = await chat_service.analyze_contract_ai(payload.question)
    return ApiResponse(result=ChatResponse(reply=reply, conv_id=0, title=None))
