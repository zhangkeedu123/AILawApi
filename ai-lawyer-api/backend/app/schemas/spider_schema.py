from pydantic import BaseModel
from typing import Optional

class SpiderBase(BaseModel):
    name: str
    job: Optional[str] = None
    city: Optional[str] = None
    platform: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = "未联系"

class SpiderCreate(SpiderBase):
    pass

class SpiderUpdate(BaseModel):
    name: Optional[str] = None
    job: Optional[str] = None
    city: Optional[str] = None
    platform: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None

class SpiderRead(SpiderBase):
    id: int
    class Config:
        from_attributes = True
