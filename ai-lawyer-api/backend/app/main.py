from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.client_router import router as client_router
from .routers.case_router import router as case_router
from .routers.contract_router import router as contract_router
from .routers.document_router import router as document_router
from .routers.spider_router import router as spider_router
from .routers.firm_router import router as firm_router
from .routers.employee_router import router as employee_router

app = FastAPI(title="AI Lawyer Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

@app.get("/")
def root():
    return {"ok": True, "service": "AI Lawyer Backend"}

# 注册路由
app.include_router(client_router)
app.include_router(case_router)
app.include_router(contract_router)
app.include_router(document_router)
app.include_router(spider_router)
app.include_router(firm_router)
app.include_router(employee_router)
