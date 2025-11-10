from pydantic import BaseModel, Field
from typing import Optional


class RegisterRequest(BaseModel):
    phone: str = Field(..., description="手机号")
    password: str = Field(..., description="密码(明文，后端加密)")
    name: Optional[str] = Field(None, description="姓名")
    role:int

class LoginRequest(BaseModel):
    phone: str
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role :int


class MeResponse(BaseModel):
    id: int
    name: Optional[str] = None
    phone: str
    role :int

