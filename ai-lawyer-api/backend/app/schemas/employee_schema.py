from pydantic import BaseModel
from typing import Optional

class EmployeeBase(BaseModel):
    name: str
    title: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    firm_name: Optional[str] = None
    status: Optional[str] = "active"

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    firm_name: Optional[str] = None
    status: Optional[str] = None

class EmployeeRead(EmployeeBase):
    id: int
    class Config:
        from_attributes = True
