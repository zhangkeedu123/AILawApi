from __future__ import annotations

import json
from typing import Any, AsyncGenerator, Dict
from ..core.ai_client import qwen_client
from ..schemas.case_schema import CaseExtractResult
from ..schemas.legal_retrieval_schema import LegalRetrievalResult


_DOCUMENT_EXTRACT_PROMPT = """你是一名法律文书结构化信息抽取助手，需要从用户提供的文本中提取民事起诉状（民间借贷纠纷）
所需的全部要素，并输出 JSON，JSON 字段结构必须严格符合以下模板。

请按如下要求从用户输入中抽取信息：

【输出要求】
1. 必须输出一个结构化 JSON（不能多字、不能解释）。
2. 用户文本中未提及的字段必须输出空字符串 ""。
3. 所有日期统一格式为 yyyy年MM月dd日。
4. 金额用阿拉伯数字，不添加单位，单位另由文书模板处理。
5. 性别只能为 "男" 或 "女"（如无法判断，则为空）。
6. 所有布尔判断类字段用 true / false。
7. 不要擅自生成个人敏感信息，无法确定的保持空字符串。
8. 不要遗漏字段，字段名称必须完全一致。

【JSON 字段结构】
{
  "原告": {
    "姓名": "",
    "性别": "",
    "出生日期": "",
    "民族": "",
    "工作单位": "",
    "职务": "",
    "联系电话": "",
    "住所地": "",
    "经常居住地": "",
    "证件类型": "",
    "证件号码": ""
  },
  "被告": {
    "姓名": "",
    "性别": "",
    "出生日期": "",
    "民族": "",
    "工作单位": "",
    "职务": "",
    "联系电话": "",
    "住所地": "",
    "经常居住地": "",
    "证件类型": "",
    "证件号码": ""
  },
  "借款信息": {
    "借款本金": "",
    "利息": "",
    "借款开始日期": "",
    "借款截止日期": "",
    "利率": "",
    "借款提供方式": "",
    "是否到期": "",
    "是否逾期": "",
    "逾期天数": "",
    "已还本金": "",
    "已还利息": ""
  },
  "合同信息": {
    "合同名称": "",
    "合同签订日期": "",
    "合同地点": "",
    "合同编号": ""
  },
  "诉讼请求": "",
  "事实与理由": ""
}

【最终任务】
根据用户输入内容，抽取并填充上述 JSON，不得添加额外说明，不得输出无关文字，只输出 JSON。"""


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
        "你是法律顾问，请从用户提供的案件分析，总结出案件名称，不要超过30个字"
        "并严格以 JSON 本体返回，所有值为字符串：\n"
        "{\n"
        "  \"name\": \"\",\n"
        "}\n"
        "字段含义与规则：\n"
        "- name：总结案件名称（简洁准确）\n"
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


async def analyze_case_stream(text: str) -> AsyncGenerator[str, None]:
    """法律分析流式输出，提示词与 analyze_case_ai 保持一致"""
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
    async for chunk in qwen_client.chat_stream(messages):
        yield chunk


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


async def extract_document_elements_stream(text: str) -> AsyncGenerator[str, None]:
    """基于固定提示词流式抽取民间借贷纠纷起诉状所需字段。"""
    messages = [
        {"role": "system", "content": _DOCUMENT_EXTRACT_PROMPT},
        {"role": "user", "content": text or ""},
    ]
    async for chunk in qwen_client.chat_stream(messages):
        yield chunk


async def extract_document_elements(text: str) -> str:
    """汇总流式抽取结果，返回完整 JSON 字符串。"""
    chunks: list[str] = []
    async for part in extract_document_elements_stream(text):
        chunks.append(part)
    return "".join(chunks)


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



async def generate_legal_document_ai(doc_type: str, case_material: str) -> str:
    """根据案件材料生成指定类型的中文法律文书。

    要求模型输出：
    - 第一行仅为文书名称（示例：某某起诉状/上诉状/答辩状等，或更具体名称）
    - 第二行开始为正文内容；不要输出任何多余说明、标签或代码块标记
    - 保持中文法律写作风格，条理清晰、格式规范
    """
    system_prompt = (
        "你是一名中国法律文书写作助手。请基于提供的案件材料，制作规范的中文法律文书。\n"
        "输出规范：仅输出两部分：\n"
        "1) 第一行：文书名称（仅名称，不含前后标点或引号）\n"
        "2) 第二行及以后：文书正文内容（结构清晰，包含必要的标题与分段）\n"
        "严禁输出任何额外前后缀、解释性文字、提示语或代码块标记。"
    )

    user_content = (
        f"目标文书类型：{doc_type}\n\n"
        f"案件材料：\n{case_material}".strip()
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]
    return await qwen_client.chat(messages)


def compose_case_material(case: dict | None, extra_facts: str | None) -> str:
    """将案件信息与补充事实整理为给模型的材料文本。

    """
    if not case:
        return (extra_facts or "").strip()
    parts: list[str] = []
    name = (case.get("name") or "").strip()
    plaintiff = (case.get("plaintiff") or "").strip()
    defendant = (case.get("defendant") or "").strip()
    location = (case.get("location") or "").strip()
    status_name = (case.get("status_name") or case.get("status") or "").strip()
    claims = (case.get("claims") or "").strip()
    facts = (case.get("facts") or "").strip()
    if name:
        parts.append(f"案名：{name}")
    parties_lines = []
    if plaintiff:
        parties_lines.append(f"原告：{plaintiff}")
    if defendant:
        parties_lines.append(f"被告：{defendant}")
    if parties_lines:
        parts.append("当事人：" + "；".join(parties_lines))
    base_info = []
    if location:
        base_info.append(f"地点：{location}")
    if status_name:
        base_info.append(f"状态：{status_name}")
    if base_info:
        parts.append("基本情况：" + "；".join(base_info))
    if claims:
        parts.append(f"诉讼请求：{claims}")
    if facts:
        parts.append(f"事实与理由：{facts}")
    if extra_facts and extra_facts.strip():
        parts.append(f"补充事实：{extra_facts.strip()}")
    return "\n".join(parts).strip()


async def legal_retrieval_ai(text: str) -> str:
    """
    法律案件检索：返回包含“相关法律”“相关案件”“律师务实观点”的严格 JSON 结构。

    结构设计（仅输出 JSON 本体，键与字段均为中文）：
    {
      "法律集合": [
        {"法律名称": "", "第几条": "", "法律内容": ""}
      ],
      "案件集合": [
        {"案件名称": "", "时间": "", "案号": "", "案情摘要": "", "判决结果": ""}
      ],
      "律师务实观点集合": [
        {"标题": "", "观点建议": ""}
      ]
    }

    规则：
    - 仅返回上述 JSON 本体，不要任何多余前后缀、说明文字或 Markdown 代码块标记。
    - 内容以中文表述，尽量准确、简洁；无法确定的字段使用空字符串；对应集合可为空数组。
    - 法律条文与案件如无法确定具体来源，可给出通用、普适的表述，避免杜撰具体编号。
    """

    system_prompt = (
        "你是一名中国法律检索与分析助手。请基于用户提供的问题或案件描述，"
        "组织输出：相关法律条文、参考案件，以及务实可操作的律师观点建议。\n\n"
        "严格只输出如下 JSON 结构（键与字段均为中文；集合为空时使用空数组）：\n"
        "{\n"
        "  \"法律集合\": [\n"
        "    {\"法律名称\": \"\", \"第几条\": \"\", \"法律内容\": \"\"}\n"
        "  ],\n"
        "  \"案件集合\": [\n"
        "    {\"案件名称\": \"\", \"时间\": \"\", \"案号\": \"\", \"案情摘要\": \"\", \"判决结果\": \"\"}\n"
        "  ],\n"
        "  \"律师务实观点集合\": [\n"
        "    {\"标题\": \"\", \"观点建议\": \"\"}\n"
        "  ]\n"
        "}\n\n"
        "要求：\n"
        "- 仅输出 JSON 本体，不要任何解释或多余符号（包括 Markdown 代码块）。\n"
        "- 内容以中文表达，尽可能准确并可操作；无法确定处留空字符串。\n"
    )

    messages = [ 
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text},
    ]

    raw = await qwen_client.chat(messages)
    return _extract_json_block(raw)


async def legal_retrieval_structured_v2(text: str) -> LegalRetrievalResult:
    """返回英文字段的结构化对象，直接反序列化。"""
    system_prompt = (
        "你是一名中国法律检索与分析助手。请基于用户提供的问题或案件描述，"
        "输出：相关法律条文、以及务实可操作的律师观点建议。详细表述清楚，数据要全面\n\n"
        "输出 JSON 格式如下（严格遵守结构与字段命名）：\n\n"
        "{\n"
        "  \"search\":  \"\" , \n "
        "  \"laws\": [ {\"law_name\": \"\", \"article\": \"\", \"content\": \"\"} ],\n"
        "  \"opinions\": [ {\"title\": \"\", \"advice\": \"\"} ]\n"
        "}\n\n"
        "字段含义与规则：\n"
        "- laws：法律集合\n"
        "- law_name：法律名称\n"
        "- article：章节（第几条）\n"
        "- content：法律内容（原文表达）\n"
        "- opinions：律师务实观点集合\n"
        "- title：标题\n"
        "- advice：关于用户问题的相关法律案件的务实观点建议\n"
        "- search:从用户问题中提取用于检索裁判文书的关键词，保留场景、行为、对象、争议词。5个词语以内 "
        "严格要求：只输出 JSON 本体，不要输出任何多余文字、注释或代码块标记。"
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text+" 的相关法律和律师观点建议 "},
    ]
    raw = await qwen_client.chat(messages, "qwen3-max")
    raw_json = _extract_json_block(raw)
    try:
        data = json.loads(raw_json)
    except Exception:
        data = {}
    return LegalRetrievalResult(
        laws=data.get("laws", []),
        cases=data.get("search", []),
        opinions=data.get("opinions", []),
    )
