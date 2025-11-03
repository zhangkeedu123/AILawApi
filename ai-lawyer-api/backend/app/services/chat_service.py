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


def _extract_json_block(s: str) -> str:
    """尽力从回复中提取第一个完整的 JSON 对象字符串；失败则原样返回。"""
    try:
        # 快速路径：本身即为 JSON
        json.loads(s)
        return s
    except Exception:
        pass
    try:
        start = s.find("{")
        end = s.rfind("}")
        if start != -1 and end != -1 and end > start:
            return s[start : end + 1]
    except Exception:
        pass
    return s


async def analyze_contract_ai(text: str) -> str:
    """合同审查：根据固定系统提示词，输出严格 JSON 结构的审查结果。"""
    system_prompt = (
        "你是一名资深律师助理和合同审查专家，熟悉中国《民法典》《劳动合同法》《公司法》《数据安全法》等法律法规。\n"
        "请仔细审查以下合同文本，从法律合规性、履约风险、财务风险、保密风险、争议条款等方面全面分析。\n\n"
        "要求：\n"
        "1. 全面识别合同中存在的潜在法律风险与条款隐患；\n"
        "2. 为每个风险条款提供修改建议与法律依据；\n"
        "3. 评估每个条款的风险等级（高/中/低）；\n"
        "4. 最终以 JSON 格式输出结果。\n\n"
        "输出 JSON 格式如下（严格遵守结构与字段命名）：\n\n"
        "{\n"
        "  \"contract_overview\": {\n"
        "    \"contract_type\": \"（自动判断合同类型，如劳动合同、技术服务合同等）\",\n"
        "    \"main_parties\": [\"（甲方名称）\", \"（乙方名称）\"],\n"
        "    \"background\": \"（简要说明合同目的或合作背景）\"\n"
        "  },\n"
        "  \"risk_analysis\": [\n"
        "    {\n"
        "      \"id\": 1,\n"
        "      \"risk_type\": \"（风险类型，如法律风险/履约风险/保密风险等）\",\n"
        "      \"clause_excerpt\": \"（引用存在风险的合同片段）\",\n"
        "      \"problem_description\": \"（说明问题及隐患）\",\n"
        "      \"suggested_revision\": \"（提出修改或补充建议）\",\n"
        "      \"result_content\": \"（修改示范）\",\n"
        "      \"legal_basis\": \"（引用相关法律条文）\",\n"
        "      \"risk_level\": \"（高/中/低）\"\n"
        "    }\n"
        "  ],\n"
        "  \"summary\": {\n"
        "    \"overall_risk_level\": \"（综合评估：高/中/低）\",\n"
        "    \"risk_statistics\": {\n"
        "      \"high\": 0,\n"
        "      \"medium\": 0,\n"
        "      \"low\": 0\n"
        "    },\n"
        "    \"conclusion\": \"（简要说明合同总体风险与签署建议）\",\n"
        "    \"recommendation\": \"（提出修改与完善的方向）\"\n"
        "  }\n"
        "}\n\n"
        "请根据上述要求审查以下合同文本，并仅返回符合此 JSON 结构的结果，不输出任何其他说明或文字。"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text},
    ]
    raw = await qwen_client.chat(messages)
    return _extract_json_block(raw)
