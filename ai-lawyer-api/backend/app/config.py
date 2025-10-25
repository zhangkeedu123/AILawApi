import os
from pydantic import BaseModel,Field

class Settings(BaseModel):
    #db
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "ailawyer")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "yingcai")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "123456zk")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")

    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    APP_RELOAD: bool = os.getenv("APP_RELOAD", "True").lower() == "true"

      # LLM
    das_scope_api_key: str =os.getenv("DASHSCOPE_API_KEY", "") 
    das_scope_base_url: str =os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    default_model: str = os.getenv("DEFAULT_MODEL", "qwen-plus")
    
    # Memory / context
    recent_rounds: int = 10               # 最近N轮注入上下文（不删历史）
    max_context_tokens: int = 8000        # 目标上下文上限（可按实际模型设置）
    summary_trigger_ratio: float = 0.7    # 70%
    summary_remind_after: int = 3         # T1：摘要>=3次提醒新建会话
    
settings = Settings()
