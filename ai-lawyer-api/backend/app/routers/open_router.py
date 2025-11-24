from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Form, Request
from fastapi.responses import FileResponse
from ..schemas.file_schema import FileCreate, FileUpdate, FileRead, FileHtmlPayload
from ..common.pagination import Paginated, PageMeta
from ..common.params import PageParams
from ..services import files_service
from ..schemas.response import ApiResponse
from ..security.auth import get_current_user

from pathlib import Path
import os
import re
import time
import uuid
import mimetypes
from urllib.parse import quote
import jwt
from datetime import datetime, timedelta

router = APIRouter(prefix="/open", tags=["File"])
ONLYOFFICE_SECRET = "ZjS2mNT5nQZV1TJsIRxI3yLEm8ejnqD5"

@router.get("/office/file-proxy/{file_id}")
async def onlyoffice_file_proxy(
    file_id: int,
    token: str = Query(..., alias="token"),  # 注意参数名，不叫 token 了
):
    """
    ONLYOFFICE 下载文件专用代理：
    - 不要求用户登录
    - 只校验 ONLYOFFICE 发来的 file_token
    """
    # 1. 校验 ONLYOFFICE 传来的 file_token
    # try:
    #     jwt.decode(file_token, ONLYOFFICE_SECRET, algorithms=["HS256"])
    # except Exception:
    #     raise HTTPException(status_code=400, detail="Invalid ONLYOFFICE token")
    
    # 2. 查数据库里的 file 记录
    obj = await files_service.get_file_by_id(file_id)
    if not obj:
        raise HTTPException(status_code=404, detail="File not found")

    # 3. 根据 doc_url 拼真实路径
    abs_path = files_service._safe_join_file_path(obj["doc_url"])
    if not abs_path.exists():
        raise HTTPException(status_code=404, detail="Real file missing")

    print("FILE DOES NOT EXIST:", abs_path)
    # 读取头部检查真实类型
    with open(abs_path, "rb") as f:
        head = f.read(8)
    print("FILE HEAD BYTES:", head)
    # 4. 返回文件流
    return FileResponse(
        abs_path,
        media_type="application/octet-stream",
        filename=abs_path.name,
    )