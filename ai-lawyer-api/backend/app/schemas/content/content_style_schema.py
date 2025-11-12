from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ContentStyleBase(BaseModel):
    tone: Optional[str] = None
    reading_level: Optional[str] = None
    do_list: Optional[str] = None
    dont_list: Optional[str] = None
    legal_scope: Optional[str] = None


class ContentStyleCreate(ContentStyleBase):
    pass


class ContentStyleUpdate(BaseModel):
    tone: Optional[str] = None
    reading_level: Optional[str] = None
    do_list: Optional[str] = None
    dont_list: Optional[str] = None
    legal_scope: Optional[str] = None


class ContentStyleRead(ContentStyleBase):
    id: int
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True

