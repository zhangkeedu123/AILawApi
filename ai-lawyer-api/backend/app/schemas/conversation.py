from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChatRequest(BaseModel):
    user_id: str
    question: str

class ChatResponse(BaseModel):
    reply: str


class ConversationRead(BaseModel):
    id: int
    user_id: str
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
