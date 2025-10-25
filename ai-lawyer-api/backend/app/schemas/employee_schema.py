from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EmployeeBase(BaseModel):
    name: str
    phone: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    firm_id: Optional[str] = None
    firm_name: Optional[str] = None
    client_num: int = 0
    case_num: int = 0
    status: int = 0
    status_name: Optional[str] = "未启用"


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    firm_id: Optional[str] = None
    firm_name: Optional[str] = None
    client_num: Optional[int] = None
    case_num: Optional[int] = None
    status: Optional[int] = None
    status_name: Optional[str] = None


class EmployeeRead(EmployeeBase):
    id: int
    created_at: Optional[datetime] = None
    update_at: Optional[datetime] = None
    class Config:
        from_attributes = True
