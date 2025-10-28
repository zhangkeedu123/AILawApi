from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .db.db import init_pg_pool, close_pg_pool
from .routers.chat_router import router as chat_router
from .routers.conversations_router import router as conversations_router
from .routers.client_router import router as client_router
from .routers.case_router import router as case_router
from .routers.contract_router import router as contract_router
from .routers.document_router import router as document_router
from .routers.spider_router import router as spider_router
from .routers.firm_router import router as firm_router
from .routers.employee_router import router as employee_router
from .routers.auth_router import router as auth_router
from .schemas.response import ApiResponse
from .security.auth import get_current_user, set_current_user

app = FastAPI(title="AI Lawyer Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

@app.get("/", response_model=ApiResponse[dict])
def root():
    return ApiResponse(result={"service": "AI Lawyer Backend"})
# ✅ 启动时初始化 asyncpg 连接池
@app.on_event("startup")
async def on_startup():
    await init_pg_pool()

# ✅ 关闭时释放连接池
@app.on_event("shutdown")
async def on_shutdown():
    await close_pg_pool()

# ✅ 挂载新路由
app.include_router(chat_router, dependencies=[Depends(set_current_user)])
app.include_router(conversations_router, dependencies=[Depends(set_current_user)])
# 注册路由（统一鉴权）
app.include_router(client_router, dependencies=[Depends(get_current_user)])
app.include_router(case_router, dependencies=[Depends(get_current_user)])
app.include_router(contract_router, dependencies=[Depends(get_current_user)])
app.include_router(document_router, dependencies=[Depends(get_current_user)])
app.include_router(spider_router, dependencies=[Depends(get_current_user)])
app.include_router(firm_router, dependencies=[Depends(get_current_user)])
app.include_router(employee_router, dependencies=[Depends(get_current_user)])

# 认证路由（公开）
app.include_router(auth_router)
