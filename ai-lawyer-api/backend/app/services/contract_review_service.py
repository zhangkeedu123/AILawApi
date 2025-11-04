from __future__ import annotations

import json
from typing import Any, Dict, List
from pathlib import Path

from ..db.db import get_pg_pool
from ..db.repositories import contract_review_repo, contract_repo


def _load_json(s: str) -> Dict[str, Any] | List[Dict[str, Any]]:
    try:
        return json.loads(s)
    except Exception:
        try:
            start = s.find("{")
            end = s.rfind("}")
            if start != -1 and end != -1 and end > start:
                return json.loads(s[start : end + 1])
        except Exception:
            pass
    return {}


def _norm_level(v: str | None) -> str:
    x = (v or "").strip().lower()
    if x in {"高", "high", "高风险"}:
        return "high"
    if x in {"中", "medium", "中风险", "中等"}:
        return "medium"
    if x in {"低", "low", "低风险"}:
        return "low"
    return "medium"


def _to_rows(contract_id: int, data: Dict[str, Any] | List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    # 兼容两种结构：顶层含 risk_analysis 列表，或直接即为列表
    lst: List[Dict[str, Any]]
    if isinstance(data, dict) and isinstance(data.get("risk_analysis"), list):
        lst = [x for x in data.get("risk_analysis", []) if isinstance(x, dict)]
    elif isinstance(data, list):
        lst = [x for x in data if isinstance(x, dict)]
    else:
        lst = []

    for it in lst:
       
        row = {
            "contract_id": contract_id,
            "title": it.get("problem_description"),
            "risk_level": _norm_level(it.get("risk_level")),
            "position": (it.get("position") or "中立")[:20],
            "method": (it.get("analysis_method") or "").strip()[:1000],
            "risk_clause": (it.get("problem_description") or it.get("risk_type") or "").strip()[:1000],
            "result_type": "",
            "original_content": (it.get("clause_excerpt") or "").strip()[:1000],
            "suggestion": (it.get("suggested_revision") or "").strip()[:1000],
            "result_content": (it.get("result_content") or "").strip()[:1000],
            "legal_basis": (it.get("legal_basis") or "").strip()[:1000],
        }
        items.append(row)
    return items


async def persist_reviews_from_json(contract_id: int, review_json: str) -> None:
    data = _load_json(review_json)
    rows = _to_rows(contract_id, data if isinstance(data, (dict, list)) else [])
    pool = await get_pg_pool()
    await contract_review_repo.delete_by_contract(pool, contract_id)
    if rows:
        await contract_review_repo.insert_many(pool, rows)
    # 更新合同表风险统计字段
    high = 0
    medium = 0
    low = 0
    hasrisk_value: str | None = None

    if isinstance(data, dict):
        summary = data.get("summary") or {}
        if isinstance(summary, dict):
            stats = summary.get("risk_statistics") or {}
            if isinstance(stats, dict):
                try:
                    high = int(stats.get("high") or 0)
                except Exception:
                    high = 0
                try:
                    medium = int(stats.get("medium") or 0)
                except Exception:
                    medium = 0
                try:
                    low = int(stats.get("low") or 0)
                except Exception:
                    low = 0
          

    # 若 summary 缺失，则根据已解析的 rows 统计
    if high == 0 and medium == 0 and low == 0 and rows:
        for r in rows:
            lvl = (r.get("risk_level") or "").strip().lower()
            if lvl == "high":
                high += 1
            elif lvl == "medium":
                medium += 1
            elif lvl == "low":
                low += 1

    # 兜底 hasrisk 值：若无 overall，则根据是否存在风险条目判断
    if not hasrisk_value:
        total = high + medium 
        hasrisk_value = "有风险" if total > 0 else "无风险"

    await contract_repo.update(
        pool,
        contract_id,
        {
            "hasrisk": hasrisk_value,
            "high_risk": high,
            "medium_risk": medium,
            "low_risk": low,
        },
    )

 
async def list_reviews_by_contract(contract_id: int) -> list[dict]:
    pool = await get_pg_pool()
    return await contract_review_repo.select_by_contract(pool, contract_id)
