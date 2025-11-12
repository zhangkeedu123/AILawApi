from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ContentTemplateBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    base_prompt: Optional[str] = None


class ContentTemplateCreate(ContentTemplateBase):
    pass


class ContentTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    base_prompt: Optional[str] = None


class ContentTemplateRead(ContentTemplateBase):
    id: int
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True

