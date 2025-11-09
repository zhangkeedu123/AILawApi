from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class PackageUserBase(BaseModel):
    packages_id: int
    firms_id: int
    status: int = 0
    status_name: Optional[str] = "未到期"
    day_use_num: int = 0
    expiry_date: datetime
    money: Decimal | float = Decimal("0.00")


class PackageUserCreate(PackageUserBase):
    pass


class PackageUserUpdate(BaseModel):
    packages_id: Optional[int] = None
    firms_id: Optional[int] = None
    status: Optional[int] = None
    status_name: Optional[str] = None
    day_use_num: Optional[int] = None
    expiry_date: Optional[datetime] = None
    money: Optional[Decimal | float] = None


class PackageUserRead(PackageUserBase):
    id: int
    # 关联展示字段
    package_name: Optional[str] = None
    firm_name: Optional[str] = None
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True

