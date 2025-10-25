from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ContractBase(BaseModel):
    contract_name: str
    type: Optional[str] = None
    hasRisk: bool = False
    high_risk: int = 0
    medium_risk: int = 0
    low_risk: int = 0


class ContractCreate(ContractBase):
    pass


class ContractUpdate(BaseModel):
    contract_name: Optional[str] = None
    type: Optional[str] = None
    hasRisk: Optional[bool] = None
    high_risk: Optional[int] = None
    medium_risk: Optional[int] = None
    low_risk: Optional[int] = None


class ContractRead(ContractBase):
    id: int
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True
