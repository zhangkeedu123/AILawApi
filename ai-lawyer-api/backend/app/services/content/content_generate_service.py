from typing import AsyncGenerator, Dict, Any, Optional
from ...core.ai_client import qwen_client
from ...db.db import get_pg_pool
from ...db.repositories.content import content_prompts_repo, contents_repo


async def generate_stream(filled_prompt: str) -> AsyncGenerator[str, None]:
    messages = [{"role": "user", "content": filled_prompt}]
    system_prompt=(
        "你是一名律师行业营销专家。请根据用户的问题，创作专业高质量的文案内容，内容要能吸引用户阅读"
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": filled_prompt},
    ]
    async for chunk in qwen_client.chat_stream(messages):
        yield chunk


async def generate_text(filled_prompt: str) -> str:
    parts: list[str] = []
    async for chunk in generate_stream(filled_prompt):
        parts.append(chunk)
    return "".join(parts)


def _parse_title_body_md(text: str) -> tuple[str, str]:
    s = (text or "").strip()
    if s.startswith("```") and s.endswith("```"):
        s = s.strip("`\n")
    lines = [ln.strip() for ln in s.splitlines()]
    while lines and not lines[0]:
        lines.pop(0)
    title = lines[0][:200] if lines else "生成内容"
    body = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
    return title, body


async def generate_and_persist_by_prompt_id(prompt_id: int, employees_id: int) -> Optional[int]:
    pool = await get_pg_pool()
    prompt = await content_prompts_repo.get_by_id(pool, int(prompt_id))
    if not prompt:
        return None
    filled_prompt = prompt.get("filled_prompt") or ""
    text = await generate_text(filled_prompt)
    title, body_md = _parse_title_body_md(text)
    data: Dict[str, Any] = {
        "employees_id": employees_id,
        "title": title,
        "body_md": body_md,
    }
    new_id = await contents_repo.create(pool, data)
    return int(new_id)

