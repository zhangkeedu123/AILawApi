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
from ..services import document_service, case_service, document_template_service
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
    facts: str
    template_id: int



@router.post("/generate_document", response_model=ApiResponse[dict])
async def generate_document(
    payload: DocGenerateRequest,
    request: Request,
):
    """文书生成：内部流式调用 AI 抽取结构化 JSON，渲染模板生成文档并入库，返回文书实体。"""
    user = getattr(request.state, "current_user", None)
    if not user:
        raise HTTPException(status_code=401, detail="未登录")

    await _ensure_ai_quota_and_consume(request)

    template = await document_template_service.get_document_template_by_id(int(payload.template_id))
    if not template:
        return ApiResponse(status=False,msg="文书模板不存在")
    template_url = (template.get("url") or "").strip()
    template_url="/files/office/借贷案例模板.docx"
    try:
        template_path = document_template_service.resolve_template_path(template_url)
    except FileNotFoundError as e:
        return ApiResponse(status=False,msg="AI 调用失败: {e}")

    chunks: list[str] = []
    try:
        async for part in chat_service.extract_document_elements_stream(payload.facts or ""):
            chunks.append(part)
    except Exception as e:
        return ApiResponse(status=False,msg="AI 调用失败: {e}")

    full_text = "".join(chunks).strip()
    json_text = document_template_service.extract_json_from_text(full_text)
    try:
        ai_result = json.loads(json_text)
    except Exception:
        return ApiResponse(status=False,msg="AI 返回不是有效的 JSON，请重试")

    try:
        doc_obj = await document_template_service.render_and_persist_document(
            template_path=template_path,
            template_info=template, 
            ai_result=ai_result,
            user=user,
        )
    except Exception as e:
        return ApiResponse(status=False,msg=str(e))

    return ApiResponse(result=doc_obj)

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
        raise HTTPException(status_code=400, detail="缺少律所信息")
    pool = await get_pg_pool()
    pkg = await package_user_repo.get_active_latest_by_firm(pool, int(firm_id))
    if not pkg:
        raise HTTPException(status_code=403, detail="套餐已到期，继续使用请充值")
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
