from typing import Optional, Tuple, List, Dict, Any
from ..db.db import get_pg_pool
from ..db.repositories import files_repo
from pathlib import Path
from io import BytesIO


class FileExtractError(Exception):
    pass


class UnsupportedFileType(FileExtractError):
    pass


class DependencyMissing(FileExtractError):
    pass


def _extract_docx_text(data: bytes) -> str:
    try:
        import docx  # python-docx
    except Exception as e:
        raise DependencyMissing(f"python-docx 加载失败: {e}")
    try:
        document = docx.Document(BytesIO(data))
        paras = [p.text for p in document.paragraphs if p.text]
        return "\n".join(paras).strip()
    except Exception as e:
        raise FileExtractError(f"DOCX 文本抽取失败: {e}")


def _extract_pdf_text(data: bytes) -> str:
    reader = None
    try:
        import pypdf  # type: ignore
        reader = pypdf.PdfReader(BytesIO(data))
    except Exception:
        try:
            import PyPDF2  # type: ignore
            reader = PyPDF2.PdfReader(BytesIO(data))
        except Exception as e:
            raise DependencyMissing(f"pypdf/PyPDF2 加载失败: {e}")
    try:
        texts = []
        for page in reader.pages:
            t = page.extract_text() or ""
            if t:
                texts.append(t)
        return "\n\n".join(texts).strip()
    except Exception as e:
        raise FileExtractError(f"PDF 文本抽取失败: {e}")


def _is_text_like(filename: str, content_type: Optional[str]) -> bool:
    ct = (content_type or "").lower()
    if ct.startswith("text/"):
        return True
    if ct in {"application/json", "application/xml"}:
        return True
    suffix = Path(filename or "").suffix.lower()
    return suffix in {".txt", ".md", ".json", ".csv", ".log"}


def extract_file_text(data: bytes, filename: str, content_type: Optional[str]) -> str:
    """从上传数据中提取文本（不落盘）。
    仅支持 docx/pdf/文本类文件，不支持图片、加密 PDF 等。
    失败时抛出 FileExtractError 派生异常，调用方根据异常类型映射 HTTP 状态码。
    """
    if not data:
        raise FileExtractError("空文件")
    suffix = Path(filename or "").suffix.lower()
    ct = (content_type or "").lower()

    if suffix == ".docx" or "word" in ct:
        return _extract_docx_text(data)
    if suffix == ".pdf" or ct == "application/pdf":
        return _extract_pdf_text(data)
    if _is_text_like(filename, content_type):
        try:
            return data.decode("utf-8", errors="ignore").strip()
        except Exception:
            raise FileExtractError("文本解码失败")

    raise UnsupportedFileType("仅支持 docx、pdf、文本类文件")


async def list_files_service(
    *,
    name: Optional[str] = None,
    user_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Dict[str, Any]], int]:
    """分页查询文件列表，可按名称和用户过滤"""
    pool = await get_pg_pool()
    skip = (page - 1) * page_size
    items = await files_repo.get_all(
        pool,
        skip=skip,
        limit=page_size,
        name=name,
        user_id=user_id,
    )
    total = await files_repo.count(pool, name=name, user_id=user_id)
    return items, total


async def get_file_by_id(file_id: int) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    return await files_repo.get_by_id(pool, file_id)


async def create_file(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    new_id = await files_repo.create(pool, data)
    return await files_repo.get_by_id(pool, new_id)


async def update_file(file_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    ok = await files_repo.update(pool, file_id, data)
    if not ok:
        return None
    return await files_repo.get_by_id(pool, file_id)


async def delete_file(file_id: int) -> bool:
    pool = await get_pg_pool()
    return await files_repo.delete(pool, file_id)
