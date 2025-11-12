from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ContentBase(BaseModel):
    employees_id: Optional[int] = None
    title: Optional[str] = None
    body_md: Optional[str] = None
    keywords: Optional[str] = None
    reading_level: Optional[str] = None
    tone: Optional[str] = None


class ContentCreate(ContentBase):
    pass


class ContentUpdate(BaseModel):
    employees_id: Optional[int] = None
    title: Optional[str] = None
    body_md: Optional[str] = None
    keywords: Optional[str] = None
    reading_level: Optional[str] = None
    tone: Optional[str] = None


class ContentRead(ContentBase):
    id: int
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True

