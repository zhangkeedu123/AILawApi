from pydantic import BaseModel
from typing import Optional

class CaseBase(BaseModel):
    name: str
    plaintiff: Optional[str] = None
    defendant: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    claims: Optional[str] = None
    facts: Optional[str] = None

class CaseCreate(CaseBase):
    pass

class CaseUpdate(BaseModel):
    name: Optional[str] = None
    plaintiff: Optional[str] = None
    defendant: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    claims: Optional[str] = None
    facts: Optional[str] = None

class CaseRead(CaseBase):
    id: int
    class Config:
        from_attributes = True
