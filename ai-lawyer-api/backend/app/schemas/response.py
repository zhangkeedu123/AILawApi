from typing import Generic, Optional, TypeVar
from pydantic.generics import GenericModel

T = TypeVar("T")


class ApiResponse(GenericModel, Generic[T]):
    status: bool = True
    result: Optional[T] = None
    msg: str = "操作成功"

