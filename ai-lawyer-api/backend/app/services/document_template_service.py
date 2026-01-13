import json
import re
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..db.db import get_pg_pool
from ..db.repositories import document_template_repo
from . import files_service, document_service
from docxtpl import DocxTemplate

async def list_document_templates_service(
    *,
    name: Optional[str] = None,
    p_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Dict[str, Any]], int]:
    pool = await get_pg_pool()
    skip = (page - 1) * page_size
    items = await document_template_repo.get_all(
        pool,
        skip=skip,
        limit=page_size,
        name=name,
        p_id=p_id,
    )
    total = await document_template_repo.count(
        pool,
        name=name,
        p_id=p_id,
    )
    return items, total


async def get_document_template_by_id(id_: int) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    return await document_template_repo.get_by_id(pool, id_)


async def create_document_template(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    new_id = await document_template_repo.create(pool, data)
    return await document_template_repo.get_by_id(pool, new_id)


async def update_document_template(id_: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pool = await get_pg_pool()
    ok = await document_template_repo.update(pool, id_, data)
    if not ok:
        return None
    return await document_template_repo.get_by_id(pool, id_)


async def delete_document_template(id_: int) -> bool:
    pool = await get_pg_pool()
    return await document_template_repo.delete(pool, id_)


def extract_json_from_text(text: str) -> str:
    """从流式文本中尽量截取第一个 JSON 对象字符串。"""
    try:
        json.loads(text)
        return text
    except Exception:
        pass
    try:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1]
    except Exception:
        pass
    return text


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def resolve_template_path(url: str) -> Path:
    """根据模板 url 定位文件路径，支持仓库相对路径或 FILES_ROOT 下路径。"""
    rel = (url or "").strip()
    if not rel:
        raise FileNotFoundError("模板 URL 为空")
    candidate_paths = []
    raw_path = Path(rel)
    if raw_path.is_absolute():
        candidate_paths.append(raw_path)
    else:
        safe_rel = rel.lstrip("/\\")
        candidate_paths.append(_repo_root() / safe_rel)
        candidate_paths.append(files_service._files_root() / safe_rel)
    for p in candidate_paths:
        abs_p = p.resolve()
        if abs_p.exists():
            return abs_p
    raise FileNotFoundError(f"模板文件不存在: {rel}")


def _safe_filename(name: str) -> str:
    base = name or "document"
    return re.sub(r"[\\\\/:*?\"<>|]+", "_", str(base))


def build_template_context(ai_result: dict) -> dict:
    """构造 DocxTpl 渲染上下文，包含嵌套与常用扁平别名。"""
    context: dict[str, Any] = {}
    if isinstance(ai_result, dict):
        context.update(ai_result)
    plaintiff = ai_result.get("原告") if isinstance(ai_result, dict) else {}
    defendant = ai_result.get("被告") if isinstance(ai_result, dict) else {}
    loan_info = ai_result.get("借款信息") if isinstance(ai_result, dict) else {}
    contract_info = ai_result.get("合同信息") if isinstance(ai_result, dict) else {}

    def _norm_val(v):
        if isinstance(v, bool):
            return v
        if v is None:
            return ""
        if isinstance(v, (int, float)):
            return str(v)
        return v

    context["原告"] = plaintiff if isinstance(plaintiff, dict) else {}
    context["被告"] = defendant if isinstance(defendant, dict) else {}
    context["借款信息"] = loan_info if isinstance(loan_info, dict) else {}
    context["合同信息"] = contract_info if isinstance(contract_info, dict) else {}
    context["诉讼请求"] = _norm_val(ai_result.get("诉讼请求") if isinstance(ai_result, dict) else "")
    context["事实与理由"] = _norm_val(ai_result.get("事实与理由") if isinstance(ai_result, dict) else "")
    evidence_list = ai_result.get("证据清单") if isinstance(ai_result, dict) else []
    context["证据清单"] = evidence_list if isinstance(evidence_list, list) else []

    if isinstance(plaintiff, dict):
        for key, val in plaintiff.items():
            context[f"原告{key}"] = _norm_val(val)
        context["姓名"] = _norm_val(plaintiff.get("姓名"))
        context["性别"] = _norm_val(plaintiff.get("性别"))
    if isinstance(defendant, dict):
        for key, val in defendant.items():
            context[f"被告{key}"] = _norm_val(val)
    if isinstance(loan_info, dict):
        for key, val in loan_info.items():
            context[f"借款{key}"] = _norm_val(val)
    if isinstance(contract_info, dict):
        for key, val in contract_info.items():
            context[f"合同{key}"] = _norm_val(val)
    return context


async def render_and_persist_document(
    *,
    template_path: Path,
    template_info: dict,
    ai_result: dict,
    user: dict,
) -> dict:
    """渲染模板生成 docx，保存文件并写入文书记录。"""

    doc = DocxTemplate(str(template_path))
    context = build_template_context(ai_result or {})
    doc.render(context)

    files_root = files_service._files_root()
    out_dir = files_root / str(int(user["id"]))
    out_dir.mkdir(parents=True, exist_ok=True)

    base_name = template_info.get("name") or "生成文书"
    # 统一只追加一次 .docx，防止出现 double suffix
    # 去掉尾部所有重复的 .docx，再统一补一次
    clean_base = re.sub(r"(?:\.docx)+$", "", str(base_name), flags=re.IGNORECASE)
    fname = f"{int(time.time())}_{uuid.uuid4().hex[:8]}_{_safe_filename(clean_base)}.docx"
    abs_path = out_dir / fname
    doc.save(abs_path)

    text_content = None
    try:
        with open(abs_path, "rb") as f:
            data = f.read()
        try:
            text_content = files_service._extract_docx_text(data)
        except Exception:
            text_content = None
    except Exception:
        text_content = None

    rel_path = Path("files") / str(int(user["id"])) / fname
    display_name = f"{clean_base}.docx"
    file_obj = await files_service.create_file(
        {
            "user_id": int(user["id"]),
            "name": display_name,
            "doc_url": str(rel_path).replace("\\", "/"), 
            "content": text_content,
        }
    )
    if not file_obj or "id" not in file_obj:
        raise RuntimeError("文件保存失败")

    file_id = int(file_obj["id"])
    doc_obj = await document_service.create_document(
        {
            "user_id": int(user["id"]),
            "doc_name": str(base_name),
            "doc_type": template_info.get("name"),
            "doc_content": str(file_id),
        }
    )
    if not doc_obj:
        raise RuntimeError("文书入库失败")
    return doc_obj
