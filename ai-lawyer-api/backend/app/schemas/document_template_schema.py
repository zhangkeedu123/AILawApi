from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DocumentTemplateBase(BaseModel):
    name: str
    p_id: Optional[int] = None
    url: Optional[str] = None
    is_template: bool = True


class DocumentTemplateCreate(DocumentTemplateBase):
    pass


class DocumentTemplateUpdate(BaseModel):
    name: Optional[str] = None
    p_id: Optional[int] = None
    url: Optional[str] = None
    is_template: Optional[bool] = None


class DocumentTemplateRead(DocumentTemplateBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
