from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ClientBase(BaseModel):
    name: str
    type: Optional[str] = "个人"
    phone: Optional[str] = None
    address: Optional[str] = None
    cases: int = 0
    status: int = 0
    status_name: Optional[str] = "已联系"
    created_user: Optional[int] = None

class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    cases: Optional[int] = None
    status: Optional[int] = None
    status_name: Optional[str] = None
    created_user: Optional[int] = None

class ClientRead(ClientBase):
    id: int
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True
