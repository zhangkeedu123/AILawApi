from fastapi import Query
from pydantic import BaseModel

class PageParams(BaseModel):
    page: int = Query(1, ge=1, description="页码(从1开始)")
    page_size: int = Query(20, ge=1, le=200, description="每页条数")
