# backend/app/core/ai_client.py
import httpx
from ..config import Settings

settings = Settings()

class QwenClient:
    def __init__(self):
        self._client = httpx.AsyncClient(
            timeout=60,
            headers={
                "Authorization": f"Bearer {settings.das_scope_api_key}",
                "Content-Type": "application/json",
            },
            limits=httpx.Limits(max_keepalive_connections=50, max_connections=200),
        )
        self.base_url = settings.das_scope_base_url.rstrip("/")  # ✅ 不再作为 httpx base_url
        self.model = settings.default_model

    async def chat(self, messages: list[dict]) -> str:
        payload = {"model": self.model, "messages": messages}
        url = f"{self.base_url}/chat/completions"  # ✅ 手动拼完整 URL
        resp = await self._client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    async def aclose(self):
        await self._client.aclose()

qwen_client = QwenClient()
