from pydantic import BaseModel
from typing import Optional

class ContractBase(BaseModel):
    customer: str
    contractName: str
    uploadDate: Optional[str] = None
    amount: Optional[int] = None
    type: Optional[str] = None
    status: Optional[str] = None

class ContractCreate(ContractBase):
    pass

class ContractUpdate(BaseModel):
    customer: Optional[str] = None
    contractName: Optional[str] = None
    uploadDate: Optional[str] = None
    amount: Optional[int] = None
    type: Optional[str] = None
    status: Optional[str] = None

class ContractRead(ContractBase):
    id: int
    class Config:
        from_attributes = True
