from typing import Optional, Tuple, List, Dict, Any
from ..db.db import get_pg_pool
from ..db.repositories import files_repo
from pathlib import Path
from io import BytesIO
from html.parser import HTMLParser


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


# ------------------ HTML/Docx 转换与读取磁盘辅助 ------------------

def _repo_root() -> Path:
    # 与 router 中逻辑保持一致：/app/app/services/... -> parents[3] 指向代码根
    return Path(__file__).resolve().parents[3]


def _safe_join_file_path(doc_url: str) -> Path:
    repo_root = _repo_root()
    abs_path = (repo_root / (doc_url or "")).resolve()
    files_root = (repo_root / "files").resolve()
    if not str(abs_path).startswith(str(files_root)):
        raise FileExtractError("非法文件路径")
    return abs_path


def _escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _docx_to_html(data: bytes) -> str:
    try:
        import docx  # python-docx
    except Exception as e:
        raise DependencyMissing(f"python-docx 加载失败: {e}")
    try:
        document = docx.Document(BytesIO(data))
        html_parts: List[str] = ["<div>"]
        for p in document.paragraphs:
            if not p.runs:
                html_parts.append("<p>")
                html_parts.append("<br/>")
                html_parts.append("</p>")
                continue
            html_parts.append("<p>")
            for r in p.runs:
                t = _escape_html(r.text or "")
                if not t:
                    continue
                open_tags = ""
                close_tags = ""
                if r.bold:
                    open_tags += "<strong>"
                    close_tags = "</strong>" + close_tags
                if r.italic:
                    open_tags += "<em>"
                    close_tags = "</em>" + close_tags
                if r.underline:
                    open_tags += "<u>"
                    close_tags = "</u>" + close_tags
                html_parts.append(f"{open_tags}{t}{close_tags}")
            html_parts.append("</p>")
        html_parts.append("</div>")
        return "".join(html_parts)
    except Exception as e:
        raise FileExtractError(f"DOCX 转 HTML 失败: {e}")


def _text_to_html(text: str) -> str:
    # 将多段文本按空行拆分为<p>，行内保持简单换行
    parts: List[str] = ["<div>"]
    for para in (text or "").splitlines():
        parts.append(f"<p>{_escape_html(para)}</p>")
    parts.append("</div>")
    return "".join(parts)


def _pdf_to_html(data: bytes) -> str:
    # 以提取文本为主，再转为简单段落
    text = _extract_pdf_text(data)
    return _text_to_html(text)


async def get_file_as_html(file_id: int) -> str:
    obj = await get_file_by_id(file_id)
    if not obj:
        raise FileExtractError("文件不存在")
    abs_path = _safe_join_file_path(obj.get("doc_url") or "")
    if not abs_path.exists():
        raise FileExtractError("文件不存在")
    suffix = abs_path.suffix.lower()
    data = abs_path.read_bytes()
    if suffix == ".docx":
        return _docx_to_html(data)
    if suffix == ".pdf":
        return _pdf_to_html(data)
    # 其他文本类：按 utf-8 解码并包装为简单 HTML
    try:
        text = data.decode("utf-8", errors="ignore")
        return _text_to_html(text)
    except Exception:
        raise UnsupportedFileType("暂不支持该文件格式的 HTML 预览")


class _HTMLToDocxParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.blocks: List[Dict[str, Any]] = []  # 每个 block: {tag: 'p'|'h1'..., runs: [{text, bold, italic, underline}]}
        self.current_runs: List[Dict[str, Any]] = []
        self.style_stack: List[Dict[str, bool]] = []
        self.current_block_tag: str = "p"

    def _push_block(self, tag: str):
        if self.current_runs:
            self.blocks.append({"tag": self.current_block_tag, "runs": self.current_runs})
            self.current_runs = []
        self.current_block_tag = tag

    def handle_starttag(self, tag, attrs):
        t = tag.lower()
        if t in ("p", "div", "h1", "h2", "h3", "h4", "h5", "h6"):
            self._push_block(t if t != "div" else "p")
        elif t == "br":
            self.current_runs.append({"text": "\n", "bold": False, "italic": False, "underline": False})
        style = {"bold": False, "italic": False, "underline": False}
        if t in ("strong", "b"):
            style["bold"] = True
        if t in ("em", "i"):
            style["italic"] = True
        if t == "u":
            style["underline"] = True
        # 入栈，与上层样式合并（简单处理）
        if self.style_stack:
            parent = self.style_stack[-1].copy()
            for k, v in style.items():
                parent[k] = parent.get(k, False) or v
            self.style_stack.append(parent)
        else:
            self.style_stack.append(style)

    def handle_endtag(self, tag):
        t = tag.lower()
        if t in ("p", "div", "h1", "h2", "h3", "h4", "h5", "h6"):
            if self.current_runs:
                self.blocks.append({"tag": self.current_block_tag, "runs": self.current_runs})
                self.current_runs = []
            self.current_block_tag = "p"
        if self.style_stack:
            self.style_stack.pop()

    def handle_data(self, data):
        text = data or ""
        if not text:
            return
        style = self.style_stack[-1] if self.style_stack else {"bold": False, "italic": False, "underline": False}
        self.current_runs.append({
            "text": text,
            "bold": bool(style.get("bold")),
            "italic": bool(style.get("italic")),
            "underline": bool(style.get("underline")),
        })


def _html_to_docx_bytes(html: str) -> bytes:
    try:
        import docx
    except Exception as e:
        raise DependencyMissing(f"python-docx 加载失败: {e}")
    parser = _HTMLToDocxParser()
    parser.feed(html or "")
    document = docx.Document()
    for block in (parser.blocks or [{"tag": "p", "runs": [{"text": html or ""}]}]):
        tag = block.get("tag") or "p"
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            p = document.add_paragraph()
            p.style = f"Heading {tag[1:]}" if tag[1:].isdigit() else None
        else:
            p = document.add_paragraph()
        for r in block.get("runs", []):
            run = p.add_run(r.get("text", ""))
            run.bold = r.get("bold", False)
            run.italic = r.get("italic", False)
            run.underline = r.get("underline", False)
    bio = BytesIO()
    document.save(bio)
    return bio.getvalue()


async def update_file_with_html(file_id: int, html: str) -> Optional[Dict[str, Any]]:
    obj = await get_file_by_id(file_id)
    if not obj:
        return None
    # 目标写入路径（优先覆盖 .docx，非 docx 则改为 .docx 并更新记录）
    repo_root = _repo_root()
    rel = obj.get("doc_url") or ""
    old_abs = (repo_root / rel).resolve()
    files_root = (repo_root / "files").resolve()
    if not str(old_abs).startswith(str(files_root)):
        raise FileExtractError("非法文件路径")
    if old_abs.suffix.lower() == ".docx":
        target_abs = old_abs
        new_rel = rel
        new_name = obj.get("name") or old_abs.name
    else:
        target_abs = old_abs.with_suffix('.docx')
        new_rel = str(Path(rel).with_suffix('.docx')).replace('\\', '/')
        stem = (obj.get("name") or old_abs.name)
        new_name = str(Path(stem).with_suffix('.docx'))

    data = _html_to_docx_bytes(html or "")
    # 确保目录存在
    target_abs.parent.mkdir(parents=True, exist_ok=True)
    target_abs.write_bytes(data)

    # 如果更名为 .docx，尝试删除旧文件
    if target_abs != old_abs and old_abs.exists():
        try:
            old_abs.unlink()
        except Exception:
            pass

    # 更新数据库记录
    updated = await update_file(file_id, {
        "doc_url": new_rel,
        "name": new_name,
    })
    return updated
