from __future__ import annotations

import json
from typing import Dict
from ..core.ai_client import qwen_client
from ..schemas.case_schema import CaseExtractResult


def _normalize_case_json(s: str) -> Dict[str, str]:
    """将模型回复规范化为仅包含目标5个键的字典，值均为字符串。"""
    try:
        data = json.loads(s)
    except Exception:
        try:
            start = s.find("{")
            end = s.rfind("}")
            if start != -1 and end != -1 and end > start:
                data = json.loads(s[start : end + 1])
            else:
                data = {}
        except Exception:
            data = {}

    allowed = {"name", "plaintiff", "defendant", "claims", "facts"}
    out = {k: "" for k in allowed}
    if isinstance(data, dict):
        for k in allowed:
            v = data.get(k, "")
            out[k] = v if isinstance(v, str) else ("" if v is None else str(v))
    return out


async def extract_case_info_ai(text: str) -> CaseExtractResult:
    """调用大模型识别案件关键信息，严格返回五个字段。"""
    system_prompt = (
        "你是法律助理，请从用户提供的文本中识别案件信息，尽量保持原文，"
        "并严格以 JSON 本体返回，仅包含以下 5 个键，所有值为字符串：\n"
        "{\n"
        "  \"name\": \"\",\n"
        "  \"plaintiff\": \"\",\n"
        "  \"defendant\": \"\",\n"
        "  \"claims\": \"\",\n"
        "  \"facts\": \"\"\n"
        "}\n"
        "字段含义与规则：\n"
        "- name：总结案件名称（简洁准确，不包含案号、时间、法院名等冗余）\n"
        "- plaintiff：原告名称（多人用中文逗号分隔，无法确定填空字符串）\n"
        "- defendant：被告名称（多人用中文逗号分隔，无法确定填空字符串）\n"
        "- claims：诉讼请求（提取用户表述中的诉请要点，尽量保留原文表达）\n"
        "- facts：事实与理由（提取用户表述中的事实和理由，尽量保留原文表达）\n"
        "严格要求：只输出 JSON 本体，不要输出任何多余文字、注释或代码块标记。"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text},
    ]

    raw = await qwen_client.chat(messages)
    normalized = _normalize_case_json(raw)
    return CaseExtractResult(**normalized)


async def analyze_case_ai(text: str) -> str:
    """法律分析：使用固定的详细中文提示词，对输入文本进行结构化分析。"""
    system_prompt = (
        "你是一位中国法律专业助手。请基于用户提供的材料进行结构化法律分析，"
        "输出清晰、专业、客观的结论与依据。分析要求：\n"
        "1) 明确案件基本事实、时间线、当事人关系与争议焦点；\n"
        "2) 确认法律关系及适用法律条文（注明关键条款或法律要点）；\n"
        "3) 对原告诉讼请求逐项分析其成立与否，理由与证据要求；\n"
        "4) 对被告主要抗辩意见逐项分析其成立与否，理由与证据要求；\n"
        "5) 列出关键证据清单与证明目的，说明证据缺口与举证责任；\n"
        "6) 风险点与不确定性评估（举证难点、司法观点分歧、程序性风险等）；\n"
        "7) 可行的处理建议与策略（和解/诉讼策略、证据补强、程序建议等）。\n"
        "注意：保持中立、谨慎，不泄露隐私信息，不提供保证性承诺。语言简明清晰，专业实际，结构化分点输出。"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text},
    ]
    return await qwen_client.chat(messages)
