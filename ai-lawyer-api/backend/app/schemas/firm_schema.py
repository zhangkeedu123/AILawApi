from pydantic import BaseModel
from typing import Optional

class FirmBase(BaseModel):
    name: str
    contact: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    status: Optional[str] = "active"
    employees: int = 0
    package: Optional[str] = None

class FirmCreate(FirmBase):
    pass

class FirmUpdate(BaseModel):
    name: Optional[str] = None
    contact: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    status: Optional[str] = None
    employees: Optional[int] = None
    package: Optional[str] = None

class FirmRead(FirmBase):
    id: int
    class Config:
        from_attributes = True
