from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DocumentBase(BaseModel):
    user_id: int
    doc_name: str
    doc_type: Optional[str] = None
    doc_content: Optional[int | str] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    user_id: Optional[int] = None
    doc_name: Optional[str] = None
    doc_type: Optional[str] = None
    doc_content: Optional[int | str] = None


class DocumentRead(DocumentBase):
    id: int
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True
