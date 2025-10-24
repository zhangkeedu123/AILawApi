from typing import Generic, List, TypeVar
from pydantic.generics import GenericModel
from pydantic import BaseModel, Field

T = TypeVar("T")

class PageMeta(BaseModel):
    total: int = Field(0, description="总条数")
    page:  int = Field(1, ge=1, description="页码(从1开始)")
    page_size: int = Field(20, ge=1, le=200, description="每页数量")

class Paginated(GenericModel, Generic[T]):
    meta: PageMeta
    items: List[T]
