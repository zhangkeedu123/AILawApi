# backend/app/core/ai_client.py
import httpx
from ..config import Settings

settings = Settings()


class QwenClient:
    def __init__(self):
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(connect=10.0, read=180.0, write=120.0, pool=60.0),
            headers={
                "Authorization": f"Bearer {settings.das_scope_api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            limits=httpx.Limits(max_keepalive_connections=100, max_connections=300),
            transport=httpx.AsyncHTTPTransport(retries=3, http2=True),
            http2=True,
            follow_redirects=True,
            trust_env=True,
        )
        self.base_url = settings.das_scope_base_url.rstrip("/")
        self.model = settings.default_model

    async def chat(self, messages: list[dict], model: str | None = None) -> str:
        """调用对话接口。
        - messages: OpenAI/Das Scope 风格消息数组
        - model: 可选，覆盖默认模型名（settings.default_model）
        """
        use_model = (model or self.model)
        payload = {"model": use_model, "messages": messages}
        url = f"{self.base_url}/chat/completions"
        try:
            resp = await self._client.post(url, json=payload)
        except httpx.RemoteProtocolError:
            # Retry once with a fresh connection where keep-alive is disabled
            async with httpx.AsyncClient(
                timeout=self._client.timeout,
                headers=self._client.headers,
                limits=httpx.Limits(max_keepalive_connections=0, max_connections=50),
                transport=httpx.AsyncHTTPTransport(retries=0),
                trust_env=True,
            ) as tmp_client:
                resp = await tmp_client.post(
                    url, json=payload, headers={"Connection": "close"}
                )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    async def aclose(self):
        await self._client.aclose()


qwen_client = QwenClient()
