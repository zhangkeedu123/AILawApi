from pydantic import BaseModel, Field
from typing import List


class LawItem(BaseModel):
    law_name: str = ""
    article: str = ""
    content: str = ""


class CaseItem(BaseModel):
    case_name: str = ""
    date: str = ""
    docket_no: str = ""
    summary: str = ""
    judgment: str = ""


class OpinionItem(BaseModel):
    title: str = ""
    advice: str = ""


class LegalRetrievalResult(BaseModel):
    laws: List[LawItem] = Field(default_factory=list)
    cases: List[CaseItem] = Field(default_factory=list)
    opinions: List[OpinionItem] = Field(default_factory=list)
