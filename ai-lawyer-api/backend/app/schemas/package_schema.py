from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel


class PackageBase(BaseModel):
    name: str
    content: Optional[str] = None
    status: int = 0
    status_name: Optional[str] = "未启用"
    money: Decimal | float = Decimal("0.00")
    day_use_num: int = 0


class PackageCreate(PackageBase):
    pass


class PackageUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    status: Optional[int] = None
    status_name: Optional[str] = None
    money: Optional[Decimal | float] = None
    day_use_num: Optional[int] = None


class PackageRead(PackageBase):
    id: int
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True

