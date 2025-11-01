from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, AliasChoices, ConfigDict


class ContractBase(BaseModel):
    contract_name: str
    type: Optional[str] = None
    hasrisk: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("hasrisk", "hasRisk"),
        serialization_alias="hasrisk",
    )
    high_risk: int = 0
    medium_risk: int = 0
    low_risk: int = 0
    files: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class ContractCreate(ContractBase):
    pass


class ContractUpdate(BaseModel):
    contract_name: Optional[str] = None
    type: Optional[str] = None
    hasrisk: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("hasrisk", "hasRisk"),
        serialization_alias="hasrisk",
    )
    high_risk: Optional[int] = None
    medium_risk: Optional[int] = None
    low_risk: Optional[int] = None
    files: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class ContractRead(ContractBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
