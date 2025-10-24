from pydantic import BaseModel, EmailStr
from typing import Optional

class ClientBase(BaseModel):
    name: str
    type: Optional[str] = "个人"
    phone: Optional[str] = None
    email: Optional[str] = None
    cases: int = 0
    contracts: int = 0
    status: Optional[str] = "active"

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    cases: Optional[int] = None
    contracts: Optional[int] = None
    status: Optional[str] = None

class ClientRead(ClientBase):
    id: int
    class Config:
        from_attributes = True
