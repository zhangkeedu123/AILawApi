import asyncio
import json
from fastapi import APIRouter, Request, Query, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..schemas.conversation import ChatRequest, ChatResponse
from ..schemas.response import ApiResponse
from ..services import conversation_service, chat_service
from ..db.db import get_pg_pool
from ..db.repositories import package_user_repo
from ..services import contract_review_service
from ..services import document_service, case_service
from ..schemas.case_schema import CaseExtractResult
from ..schemas.legal_retrieval_schema import LegalRetrievalResult
from ..services.content import content_generate_service, content_prompt_service


router = APIRouter(prefix="/chat", tags=["chat"])





@router.post("", response_model=ApiResponse[ChatResponse])
async def chat_endpoint(payload: ChatRequest, request: Request) -> ApiResponse[ChatResponse]:
    user = getattr(request.state, "current_user", None)
    user_id = int(user["id"]) if user else None
    await _ensure_ai_quota_and_consume(request)
    reply, cid, title = await conversation_service.ask(user_id, payload.question, payload.conv_id or 0)
    return ApiResponse(result=ChatResponse(reply=reply, conv_id=cid, title=title))


@router.post("/stream")
async def chat_stream_endpoint(payload: ChatRequest, request: Request):
    """流式输出对话结果（SSE）。
    - 请求体与非流式接口相同（ChatRequest）
    - 响应为 `text/event-stream`，事件：meta/delta/done
    """
    user = getattr(request.state, "current_user", None) 
    user_id = int(user["id"]) if user else 0

    # 进入流式生成前做额度校验与消耗
    await _ensure_ai_quota_and_consume(request)

    async def event_gen():
        async for ev in conversation_service.ask_stream(user_id, payload.question, payload.conv_id or 0):
            typ = ev.get("type")
            if typ == "meta":
                yield f"event: meta\ndata: {json.dumps({'conv_id': ev.get('conv_id'), 'title': ev.get('title')})}\n\n"
            elif typ == "delta":
                # 文本增量
                yield f"event: delta\ndata: {json.dumps({'text': ev.get('text') or ''})}\n\n"
            elif typ == "done":
                yield "event: done\ndata: {}\n\n"

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(event_gen(), media_type="text/event-stream", headers=headers)


@router.post("/analyze")
async def analyze_case(payload: ChatRequest, request: Request):
    """法律分析改为 SSE：delta 流式返回，done 时异步落库案件"""
    user = getattr(request.state, "current_user", None)
    user_id = int(user["id"]) if user else 0

    # 进入流式生成前做额度校验与消耗
    await _ensure_ai_quota_and_consume(request)

    async def event_gen():
        chunks: list[str] = []
        try:
            # 流式向前端推送增量
            async for part in chat_service.analyze_case_stream(payload.question):
                chunks.append(part)
                yield f"event: delta\ndata: {json.dumps({'text': part})}\n\n"
        finally:
            full_text = "".join(chunks)
            # done 事件返回完整文本，前端可一次性拿到最终结果
            yield f"event: done\ndata: {json.dumps({'text': full_text})}\n\n"
            # done 后异步写入案件信息，避免阻塞 SSE
            asyncio.create_task(_persist_case_from_analysis(payload.question, full_text, user_id))

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(event_gen(), media_type="text/event-stream", headers=headers)


@router.post("/extract_case", response_model=ApiResponse[CaseExtractResult])
async def extract_case_info(payload: ChatRequest, request: Request) -> ApiResponse[CaseExtractResult]:
    """通过 service 使用 AI 提取案件信息，返回结构化字段。"""
    await _ensure_ai_quota_and_consume(request)
    result = await chat_service.extract_case_info_ai(payload.question)
    return ApiResponse(result=result)


@router.post("/contract_review", response_model=ApiResponse[ChatResponse])
async def contract_review(
    payload: ChatRequest,
    request: Request,
    contract_id: int = Query(..., description="合同ID"),
    tasks: BackgroundTasks = None,
) -> ApiResponse[ChatResponse]:
    """AI 合同审查：调用 AI 返回严格 JSON 格式审查结论字符串作为响应；
    同时在后台将 JSON 结果异步持久化：若已存在该合同ID记录则删除再插入（逻辑在 service 中处理）"""
    await _ensure_ai_quota_and_consume(request)
    reply = await chat_service.analyze_contract_ai(payload.question)
    if tasks is not None:
        tasks.add_task(contract_review_service.persist_reviews_from_json, contract_id, reply)
    else:
        await contract_review_service.persist_reviews_from_json(contract_id, reply)
    return ApiResponse(result=ChatResponse(reply=reply, conv_id=0, title=None))


class DocGenerateRequest(BaseModel):
    doc_type: str
    case_id: int = 0
    facts: str | None = None



@router.post("/generate_document", response_model=ApiResponse[ChatResponse])
async def generate_document(
    payload: DocGenerateRequest,
    request: Request,
    tasks: BackgroundTasks = None,
) -> ApiResponse[ChatResponse]:
    """生成法律文书：
    - 参数：文书类型、案件ID、事实案件描述
    - 逻辑：case_id=0 用 facts；否则查询案件信息并拼接（如有 facts 作为补充）
    - 输出：第一行文书名称；第二行起为文书内容；不要多余内容
    - 持久化：返回后异步写入 documents 表
    """
    user = getattr(request.state, "current_user", None)
    user_id = int(user["id"]) if user else None

    case_obj = None
    if payload.case_id and payload.case_id != 0:
        try:
            case_obj = await case_service.get_case_by_id(int(payload.case_id))
        except Exception:
            case_obj = None
    material = chat_service.compose_case_material(case_obj, payload.facts)

    # 调用 AI 生成文书（先额度校验）
    await _ensure_ai_quota_and_consume(request)
    raw_reply = await chat_service.generate_legal_document_ai(payload.doc_type, material)

    # 解析：第一行为文书名称，其余为正文
    text = (raw_reply or "").strip()
    # 简单去除可能的代码块包裹
    if text.startswith("```") and text.endswith("```"):
        text = text.strip("`\n")
    lines = [ln.strip() for ln in text.splitlines()]
    while lines and not lines[0]:
        lines.pop(0)
    doc_name = lines[0] if lines else (payload.doc_type or "文书")
    doc_content = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

    # 组合返回文本（严格：第一行名称，第二行起正文）
    final_reply = doc_name + ("\n" + doc_content if doc_content else "")

    # 异步入库
    data = {
        "user_id": user_id or 0,
        "doc_name": doc_name,
        "doc_type": payload.doc_type,
        "doc_content": doc_content,
    }
    if tasks is not None:
        tasks.add_task(document_service.create_document, data)
    else:
        try:
            await document_service.create_document(data)
        except Exception:
            # 忽略持久化错误，保证主流程返回
            pass 

    return ApiResponse(result=ChatResponse(reply=final_reply, conv_id=0, title=None)) 


@router.post("/legal_retrieval", response_model=ApiResponse[LegalRetrievalResult])
async def legal_retrieval(
    payload: ChatRequest,
    request: Request,
) -> ApiResponse[LegalRetrievalResult]:
    """法律案件检索：返回严格 JSON 格式，包含三类集合：
    - 法律集合：法律名称、第几条、法律内容
    - 案件集合：案件名称、时间、案号、案情摘要、判决结果
    - 律师务实观点集合：标题、观点建议

    注意：严格只返回 JSON 本体字符串（中文），业务逻辑置于 service。
    """
    await _ensure_ai_quota_and_consume(request)
    result = await chat_service.legal_retrieval_structured_v2(payload.question)
    return ApiResponse(result=result)


@router.post("/generate_content_by_prompt", response_model=ApiResponse[dict])
async def generate_content_by_prompt(
    request: Request,
    prompt_id: int = Query(..., description="content_prompts 表ID"),
    tasks: BackgroundTasks = None,
):
    """基于 content_prompts 的 filled_prompt 生成营销成稿（异步生成并入库 contents）。
    - 进入前做额度校验与消耗
    - 立即返回成功，后台流式生成并入库
    - 非管理员仅可使用自己创建的 prompt
    """
    # 额度校验与消耗（与其他接口一致）
    await _ensure_ai_quota_and_consume(request)
    
    user = getattr(request.state, "current_user", None)
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    user_id = int(user.get("id") or 0)
    role = int(user.get("role") or 0)

    

    # 权限校验：非管理员只能操作自己的 prompt
    prompt = await content_prompt_service.get_by_id(int(prompt_id))
    if not prompt:
        return ApiResponse(status=False, msg="Item not found")
    if role != 2 and int(prompt.get("employees_id") or 0) != user_id:
        return ApiResponse(status=False, msg="Item not found")

    # 异步生成并入库
    if tasks is not None:
        tasks.add_task(content_generate_service.generate_and_persist_by_prompt_id, int(prompt_id), user_id)
    else:
        import asyncio
        asyncio.create_task(content_generate_service.generate_and_persist_by_prompt_id(int(prompt_id), user_id))

    return ApiResponse(result={"accepted": True})


async def _ensure_ai_quota_and_consume(request: Request) -> None:
    """检查套餐是否有效、当日次数是否用尽；若可用则原子+1计数。"""
    user = getattr(request.state, "current_user", None)
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    firm_id = user.get("firm_id")
    if not firm_id:
        raise HTTPException(status_code=403, detail="缺少律所信息")
    pool = await get_pg_pool()
    pkg = await package_user_repo.get_active_latest_by_firm(pool, int(firm_id))
    if not pkg:
        raise HTTPException(status_code=403, detail="套餐已到期，继续使用请联系管理员")
    # 双重保险：本地校验一次额度
    day_use = int(pkg.get("day_use_num") or 0)
    day_used = int(pkg.get("day_used_num") or 0)
    if day_use != 0 and day_used >= day_use:
        raise HTTPException(status_code=403, detail="当日次数已用完")
    # 原子消耗 1 次
    ok = await package_user_repo.try_consume_one(pool, int(pkg["id"]))
    if not ok:
        raise HTTPException(status_code=403, detail="当日次数已用完")



async def _persist_case_from_analysis(question: str, analysis_text: str, user_id: int) -> None:
    """done 后异步写入 cases 核心字段，失败不影响 SSE"""
    try:
        extract = await chat_service.extract_case_info_ai(analysis_text)
        name = (extract.name).strip()[:30] or "未命名案件"
        claims = (question).strip()[:2000]
        facts = (analysis_text or "").strip()
        data = {
            "name": name,
            "claims": claims,
            "facts": facts,
            "created_user": user_id or 0,
        }
        await case_service.create_case(data)
    except Exception:
        # 写入失败不阻塞主流程
        pass
