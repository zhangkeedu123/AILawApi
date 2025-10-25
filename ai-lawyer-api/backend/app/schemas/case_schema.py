from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CaseBase(BaseModel):
    name: str
    plaintiff: Optional[str] = None
    defendant: Optional[str] = None
    location: Optional[str] = None
    status: int = 0
    status_name: Optional[str] = "未受理"
    claims: Optional[str] = None
    facts: Optional[str] = None


class CaseCreate(CaseBase):
    pass


class CaseUpdate(BaseModel):
    name: Optional[str] = None
    plaintiff: Optional[str] = None
    defendant: Optional[str] = None
    location: Optional[str] = None
    status: Optional[int] = None
    status_name: Optional[str] = None
    claims: Optional[str] = None
    facts: Optional[str] = None


class CaseRead(CaseBase):
    id: int
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True
