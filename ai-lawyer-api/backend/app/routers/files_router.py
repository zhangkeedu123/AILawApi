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

router = APIRouter(prefix="/files", tags=["File"])


def _repo_root() -> Path:
    # 运行在容器中时，代码目录通常挂载在 /app，当前文件位于 /app/app/routers/...
    # 使用 parents[3] 指向代码根（本仓库的 backend 目录或容器内的 /app）
    # 这样保存到 "files/" 会落在挂载卷内（宿主机的 backend/files）
    return Path(__file__).resolve().parents[3]


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _files_root() -> Path:
    # 使用环境变量 FILES_ROOT 指定物理存储根目录，默认 /app/files
    return Path(os.environ.get("FILES_ROOT", "/app/files")).resolve()


def _safe_name(name: str) -> str:
    return re.sub(r"[^\w\-.]+", "_", name)


def _attach_urls(obj: dict) -> dict:
    try:
        fid = int(obj.get("id"))
    except Exception:
        return obj
    obj = dict(obj)
    obj["preview_url"] = f"/files/raw/{fid}"
    obj["download_url"] = f"/files/raw/{fid}?download=true"
    return obj


def _should_extract_text(upload: UploadFile) -> bool:
    ct = (upload.content_type or "").lower()
    if ct.startswith("text/"):
        return True
    if ct in {"application/json", "application/xml"}:
        return True
    # 根据扩展名再兜底判断
    suffix = Path(upload.filename or "").suffix.lower()
    if suffix in {".txt", ".md", ".json", ".csv", ".log"}:
        return True
    return False


@router.get("/", response_model=ApiResponse[Paginated[FileRead]])
async def list_files(
    page_params: PageParams = Depends(),
    name: str | None = Query(None, description="文件名称(模糊)"),
    request: Request = None,
    user: dict = Depends(get_current_user),
):
    """分页查询文件列表（当前用户）"""
    items, total = await files_service.list_files_service(
        name=name, user_id=int(user["id"]),
        page=page_params.page, page_size=page_params.page_size,
    )
    items = [_attach_urls(i) for i in items]
    return ApiResponse(result={
        "meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size),
        "items": items,
    })


@router.get("/{file_id}", response_model=ApiResponse[FileRead])
async def get_file(file_id: int, user: dict = Depends(get_current_user)):
    obj = await files_service.get_file_by_id(file_id)
    if not obj or (obj.get("user_id") and int(obj["user_id"]) != int(user["id"])):
        raise HTTPException(404, "File not found")
    return ApiResponse(result=_attach_urls(obj))


@router.post("/upload", response_model=ApiResponse[FileRead])
async def upload_file(
    upload: UploadFile = File(..., description="要上传的文件"),
    name: str | None = Form(None, description="文件展示名（可选）"),
    extract_text: bool = Form(False, description="是否抽取文本内容（仅文本类）"),
    user: dict = Depends(get_current_user),
):
    """上传文件到相对目录 `files/` 下，并在数据库中创建记录。
    - 存储路径：`files/{user_id}/{uuid_time}_{safe_name}`（相对项目根）
    - 数据库字段：user_id, name, doc_url（相对路径）, content（可选文本）
    """
    files_root = _files_root()
    store_dir = files_root / str(int(user["id"]))
    _ensure_dir(store_dir)

    original = upload.filename or "upload.bin"
    display_name = name or original
    fname = f"{int(time.time())}_{uuid.uuid4().hex[:8]}_{_safe_name(original)}"
    rel_path = Path("files") / str(int(user["id"])) / fname
    abs_path = files_root / str(int(user["id"])) / fname

    # 保存文件
    data = await upload.read()
    with open(abs_path, "wb") as f:
        f.write(data)

    # 可选抽取文本
    text_content = None
    if extract_text and _should_extract_text(upload):
        try:
            text_content = data.decode("utf-8", errors="ignore")
        except Exception:
            text_content = None

    obj = await files_service.create_file({
        "user_id": int(user["id"]),
        "name": display_name,
        "doc_url": str(rel_path).replace("\\", "/"),
        "content": text_content,
    })
    return ApiResponse(result=_attach_urls(obj))


@router.post("/extract", response_model=ApiResponse[str])
async def extract_file_content(
    upload: UploadFile = File(..., description="上传待识别内容的文件（docx/pdf/txt 等）"),
    user: dict = Depends(get_current_user),
):
    """识别上传文件内容（不落盘不入库），直接返回文本。
    - 支持：docx、pdf、文本类（txt/csv/md/json 等）
    - 不支持：图片、加密 PDF，复杂版式效果有限
    """
    if not upload.filename:
        raise HTTPException(400, "缺少文件名")

    data = await upload.read()
    if not data:
        raise HTTPException(400, "空文件")

    try:
        text = files_service.extract_file_text(
            data=data,
            filename=upload.filename,
            content_type=upload.content_type,
        )
    except files_service.UnsupportedFileType:
        return ApiResponse(msg="暂不支持的文件类型", status=False)
    except files_service.DependencyMissing:
        return ApiResponse(msg="缺少依赖", status=False)
    except files_service.FileExtractError:
        return ApiResponse(msg="解析失败", status=False)

    return ApiResponse(result=text)


@router.put("/{file_id}", response_model=ApiResponse[FileRead])
async def update_file(file_id: int, payload: FileUpdate, user: dict = Depends(get_current_user)):
    obj = await files_service.get_file_by_id(file_id)
    if not obj or (obj.get("user_id") and int(obj["user_id"]) != int(user["id"])):
        raise HTTPException(404, "File not found")
    updated = await files_service.update_file(file_id, payload.model_dump(exclude_unset=True))
    return ApiResponse(result=_attach_urls(updated) if updated else updated)


@router.get("/raw/{file_id}")
async def download_file(
    file_id: int,
    download: bool = Query(False, description="是否以附件下载；默认内联预览"),
    user: dict = Depends(get_current_user),
):
    """根据 `file_id` 返回原始文件内容。
    - `download=false`（默认）：内联预览（pdf、图片、文本等）
    - `download=true`：作为附件下载
    """
    obj = await files_service.get_file_by_id(file_id)
    if not obj or (obj.get("user_id") and int(obj["user_id"]) != int(user["id"])):
        raise HTTPException(404, "File not found")

    rel = (obj.get("doc_url") or "").lstrip("/\\")
    if rel.startswith("files/"):
        rel = rel[len("files/"):]
    files_root = _files_root()
    abs_path = (files_root / rel).resolve()

    # 路径校验与存在性检查
    if not str(abs_path).startswith(str(files_root)) or not abs_path.exists():
        raise HTTPException(404, "File not found")

    # 猜测内容类型，默认二进制
    media_type = mimetypes.guess_type(abs_path.name)[0] or "application/octet-stream"

    # 文件名：优先使用展示名，其次实际文件名
    # 为兼容中文/Unicode，使用 RFC 5987：filename* 搭配 ASCII 回退 filename
    original_name = str(obj.get("name") or abs_path.name)
    disposition = "attachment" if download else "inline"
    # ASCII 回退名（仅保留 A-Za-z0-9_.-）
    fallback_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", original_name) or "file"
    # RFC 5987 编码（百分号编码 UTF-8）
    encoded_name = quote(original_name, safe="")
    cd_value = f"{disposition}; filename=\"{fallback_name}\"; filename*=UTF-8''{encoded_name}"
    headers = {"Content-Disposition": cd_value}

    return FileResponse(path=str(abs_path), media_type=media_type, headers=headers)


@router.get("/html/{file_id}", response_model=ApiResponse[str])
async def get_file_html(
    file_id: int,
    mode: str = Query("faithful", description="HTML 渲染模式: semantic/faithful(默认)"),
    user: dict = Depends(get_current_user),
):
    obj = await files_service.get_file_by_id(file_id)
    if not obj or (obj.get("user_id") and int(obj["user_id"]) != int(user["id"])):
        raise HTTPException(404, "File not found")
    try:
        html = await files_service.get_file_as_html(file_id, mode=mode)
    except files_service.UnsupportedFileType:
        return ApiResponse(msg="暂不支持该文件转换为HTML", status=False)
    except files_service.DependencyMissing:
        return ApiResponse(msg="缺少依赖", status=False)
    except files_service.FileExtractError as e:
        return ApiResponse(msg=f"转换失败: {e}", status=False)
    return ApiResponse(result=html)
 

@router.post("/html/{file_id}", response_model=ApiResponse[FileRead])
async def update_file_from_html(file_id: int, payload: FileHtmlPayload, user: dict = Depends(get_current_user)):
    obj = await files_service.get_file_by_id(file_id)
    if not obj or (obj.get("user_id") and int(obj["user_id"]) != int(user["id"])):
        raise HTTPException(404, "File not found")
    try:
        updated = await files_service.update_file_with_html(file_id, payload.html)
    except files_service.DependencyMissing:
        return ApiResponse(msg="缺少依赖", status=False)
    except files_service.FileExtractError:
        return ApiResponse(msg="写回失败", status=False)
    if not updated:
        raise HTTPException(404, "File not found")
    return ApiResponse(result=updated)


@router.delete("/{file_id}", response_model=ApiResponse[bool])
async def delete_file(file_id: int, user: dict = Depends(get_current_user)):
    obj = await files_service.get_file_by_id(file_id)
    if not obj or (obj.get("user_id") and int(obj["user_id"]) != int(user["id"])):
        raise HTTPException(404, "File not found")

    # 先尝试删除磁盘文件
    try:
        repo_root = _repo_root()
        rel = obj.get("doc_url") or ""
        abs_path = (repo_root / rel).resolve()
        # 防止越权删除，仅允许 files 目录
        files_root = (repo_root / "files").resolve()
        if str(abs_path).startswith(str(files_root)) and abs_path.exists():
            os.remove(abs_path)
    except Exception:
        # 删除磁盘失败不影响数据库层面的删除
        pass

    ok = await files_service.delete_file(file_id)
    if not ok:
        raise HTTPException(404, "File not found")
    return ApiResponse(result=True)

