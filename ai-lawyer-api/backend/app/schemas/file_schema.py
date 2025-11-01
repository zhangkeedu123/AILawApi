from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FileBase(BaseModel):
    # 文件展示名（可与原文件名不同）
    name: str
    # 纯文本内容（可选，用于文本类文件或抽取后存储）
    content: Optional[str] = None


class FileCreate(FileBase):
    # 上传接口会自动生成 doc_url，这里仅保留 name/content 字段
    pass


class FileUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None


class FileRead(FileBase):
    id: int
    user_id: Optional[int] = None
    doc_url: str
    preview_url: Optional[str] = None
    download_url: Optional[str] = None
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True
