import os
from pydantic import BaseModel

class Settings(BaseModel):
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "yingcaiai")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "yingcai")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "123456zk")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    APP_RELOAD: bool = os.getenv("APP_RELOAD", "True").lower() == "true"

settings = Settings()
