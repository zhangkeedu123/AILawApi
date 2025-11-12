from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ContentPromptBase(BaseModel):
    filled_prompt: Optional[str] = None
    employees_id: Optional[int] = None


class ContentPromptCreate(ContentPromptBase):
    pass


class ContentPromptUpdate(BaseModel):
    filled_prompt: Optional[str] = None
    employees_id: Optional[int] = None


class ContentPromptRead(ContentPromptBase):
    id: int
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True

