from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChatRequest(BaseModel):
    # 用户当前问题
    question: str
    # 可选的会话ID；0 表示新建会话
    conv_id: Optional[int] = 0

class ChatResponse(BaseModel):
    # AI 回复内容
    reply: str
    # 会话ID（新建时返回新ID）
    conv_id: int
    # 会话标题（仅在新建时返回，其他场景可为空）
    title: Optional[str] = None


class ConversationRead(BaseModel):
    id: int
    user_id: int
    title: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ConversationRename(BaseModel):
    title: str


class MessageRead(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime
