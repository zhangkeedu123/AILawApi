from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FirmBase(BaseModel):
    name: str
    contact: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    status: int = 0
    status_name: Optional[str] = "未启用"
    employees: int = 0


class FirmCreate(FirmBase):
    pass


class FirmUpdate(BaseModel):
    name: Optional[str] = None
    contact: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    status: Optional[int] = None
    status_name: Optional[str] = None
    employees: Optional[int] = None


class FirmRead(FirmBase):
    id: int
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True
