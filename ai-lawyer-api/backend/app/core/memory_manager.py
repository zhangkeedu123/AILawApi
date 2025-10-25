from collections import defaultdict
from typing import Dict, List, Tuple
from .ai_client import qwen_client
from ..config import Settings

settings = Settings()

def estimate_tokens(text: str) -> int:
    # 粗略估算：约 1 token ≈ 4 字符
    return max(1, len(text) // 4)

class MemoryManager:
    def __init__(self):
        # { conversation_id: {"summary": str, "count": int} }
        self._cache: Dict[int, Dict[str, int | str]] = defaultdict(lambda: {"summary": "", "count": 0})

    def get_summary(self, conversation_id: int) -> str:
        return str(self._cache[conversation_id]["summary"])

    def incr_summary_count(self, conversation_id: int):
        self._cache[conversation_id]["count"] = int(self._cache[conversation_id]["count"]) + 1

    def summary_count(self, conversation_id: int) -> int:
        return int(self._cache[conversation_id]["count"])

    def _join(self, messages: List[dict]) -> str:
        return "\n".join(f"{m['role']}: {m['content']}" for m in messages)

    def _need_summary(self, messages: List[dict]) -> bool:
        ctx = self._join(messages)
        ctx_tokens = estimate_tokens(ctx)
        return ctx_tokens > int(settings.max_context_tokens * settings.summary_trigger_ratio)

    async def summarize_if_needed(self, conversation_id: int, messages: List[dict]) -> Tuple[str, List[dict], bool]:
        if not self._need_summary(messages) or len(messages) <= 4:
            return self.get_summary(conversation_id), messages, False

        split_idx = len(messages) // 2
        older = messages[:split_idx]
        newer = messages[split_idx:]

        summary_prompt = [
            {"role": "system", "content": "请把以下对话做成简洁可延续的中文摘要，保留关键事实、目标与限制。"},
            {"role": "user", "content": self._join(older)},
        ]
        summary_piece = await qwen_client.chat(summary_prompt)

        prev = self.get_summary(conversation_id)
        merged = (prev + "\n" if prev else "") + summary_piece.strip()
        self._cache[conversation_id]["summary"] = merged
        self.incr_summary_count(conversation_id)

        return merged, newer, True

    def should_remind_new_conversation(self, conversation_id: int) -> bool:
        return self.summary_count(conversation_id) >= settings.summary_remind_after

memory_manager = MemoryManager()
