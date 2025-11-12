from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ContentIdeaBase(BaseModel):
    title: Optional[str] = None
    brief: Optional[str] = None
    persona: Optional[str] = None
    pain_point: Optional[str] = None
    keywords: Optional[str] = None


class ContentIdeaCreate(ContentIdeaBase):
    pass


class ContentIdeaUpdate(BaseModel):
    title: Optional[str] = None
    brief: Optional[str] = None
    persona: Optional[str] = None
    pain_point: Optional[str] = None
    keywords: Optional[str] = None


class ContentIdeaRead(ContentIdeaBase):
    id: int
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True

