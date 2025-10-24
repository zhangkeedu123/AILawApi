from pydantic import BaseModel
from typing import Optional

class DocumentBase(BaseModel):
    caseName: Optional[str] = None
    docName: str
    docType: Optional[str] = None
    createDate: Optional[str] = None
    status: Optional[str] = "草稿"

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    caseName: Optional[str] = None
    docName: Optional[str] = None
    docType: Optional[str] = None
    createDate: Optional[str] = None
    status: Optional[str] = None

class DocumentRead(DocumentBase):
    id: int
    class Config:
        from_attributes = True
