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
from urllib.parse import quote, urlparse, urlunparse
import jwt
from datetime import datetime, timedelta
import httpx

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
    # 1. 校验 ONLYOFFICE 传来的 token，避免越权下载
    try:
        jwt.decode(token, ONLYOFFICE_SECRET, algorithms=["HS256"])
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ONLYOFFICE token")
    
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


@router.post("/office/save/{file_id}")
async def onlyoffice_save_callback(
    file_id: int,
    request: Request,
    token: str = Query(..., alias="token"),
):
    """
    ONLYOFFICE 保存回调：下载新版本并覆盖原文件
    """
    try:
        jwt.decode(token, ONLYOFFICE_SECRET, algorithms=["HS256"])
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ONLYOFFICE token")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid callback payload")

    status = payload.get("status")
    download_url = payload.get("url") or payload.get("changesurl")

    # 回调里的下载地址可能是 localhost:8080（容器内不可达），改写为同网段的 onlyoffice:80
    def _rewrite_to_onlyoffice(url: str) -> str:
        if not url:
            return url
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return url
            new_netloc = "onlyoffice"
            # DocumentServer 内部监听 80，强制改成容器名+80
            if parsed.scheme in {"http", "https"}:
                new_netloc = f"{new_netloc}:80"
            return urlunparse(parsed._replace(netloc=new_netloc))
        except Exception:
            return url

    download_url = _rewrite_to_onlyoffice(download_url)
    print("download_url:", download_url)
    print("status:", status)
    # 状态 2：必须保存；6：强制保存。其他状态直接返回成功让文档服务器继续流程
    if status not in {2, 6}:
        return {"error": 0}

    if not download_url:
        return {"error": 1}

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(download_url, timeout=30)
            resp.raise_for_status()
            data = resp.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载新版本失败: {e}")

    ok = await files_service.overwrite_file_content(file_id, data)
    if not ok:
        raise HTTPException(status_code=500, detail="写入文件失败")

    return {"error": 0}
