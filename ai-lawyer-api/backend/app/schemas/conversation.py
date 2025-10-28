from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    reply: str


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
