from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    user_id: str
    question: str

class ChatResponse(BaseModel):
    reply: str
