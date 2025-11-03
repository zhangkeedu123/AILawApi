from fastapi import APIRouter, Request, Query, BackgroundTasks
from ..schemas.conversation import ChatRequest, ChatResponse
from ..schemas.response import ApiResponse
from ..services import conversation_service, chat_service
from ..services import contract_review_service
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
    """直接调用 AI 做案件分析。"""
    reply = await chat_service.analyze_case_ai(payload.question)
    return ApiResponse(result=ChatResponse(reply=reply, conv_id=0, title=None))


@router.post("/extract_case", response_model=ApiResponse[CaseExtractResult])
async def extract_case_info(payload: ChatRequest) -> ApiResponse[CaseExtractResult]:
    """通过 service 使用 AI 提取案件信息，返回结构化字段。"""
    result = await chat_service.extract_case_info_ai(payload.question)
    return ApiResponse(result=result)


@router.post("/contract_review", response_model=ApiResponse[ChatResponse])
async def contract_review(
    payload: ChatRequest,
    contract_id: int = Query(..., description="合同ID"),
    tasks: BackgroundTasks = None,
) -> ApiResponse[ChatResponse]:
    """AI 合同审查：调用 AI 生成严格 JSON 的审查结果字符串并立即返回；
    同时在后台根据 JSON 结果异步持久化（若已存在该合同ID记录则先删除后批量新增）。"""
    reply = await chat_service.analyze_contract_ai(payload.question)
    if tasks is not None:
        tasks.add_task(contract_review_service.persist_reviews_from_json, contract_id, reply)
    else:
        await contract_review_service.persist_reviews_from_json(contract_id, reply)
    return ApiResponse(result=ChatResponse(reply=reply, conv_id=0, title=None))
