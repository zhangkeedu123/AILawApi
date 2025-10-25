from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DocumentBase(BaseModel):
    case_id: int
    case_name: Optional[str] = None
    doc_name: str
    doc_type: Optional[str] = None
    doc_content: Optional[str] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    case_id: Optional[int] = None
    case_name: Optional[str] = None
    doc_name: Optional[str] = None
    doc_type: Optional[str] = None
    doc_content: Optional[str] = None


class DocumentRead(DocumentBase):
    id: int
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True
