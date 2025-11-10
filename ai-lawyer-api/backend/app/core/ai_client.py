"""
OpenAI 兼容（DashScope）异步客户端封装，支持普通与流式对话。
显式传入 httpx.AsyncClient：
- trust_env=True 以读取代理环境变量（HTTPS_PROXY/NO_PROXY 等）
- http2=False 规避部分代理/网关的 HTTP/2 兼容问题
"""

from typing import AsyncGenerator
import httpx
from openai import AsyncOpenAI
from ..config import Settings

settings = Settings()


def _build_httpx_client(http2: bool = False, keepalive: bool = True) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=httpx.Timeout(connect=10.0, read=180.0, write=120.0, pool=60.0),
        limits=httpx.Limits(
            max_keepalive_connections=100 if keepalive else 0,
            max_connections=300,
        ),
        transport=httpx.AsyncHTTPTransport(http2=http2),
        trust_env=True,
    )


class QwenClient:
    def __init__(self):
        self.httpx_client = _build_httpx_client(http2=False, keepalive=True)
        self.client = AsyncOpenAI(
            api_key=settings.das_scope_api_key,
            base_url=settings.das_scope_base_url.rstrip("/"),
            http_client=self.httpx_client,
        )
        self.model = settings.default_model

    async def chat(self, messages: list[dict], model: str | None = None) -> str:
        """非流式对话，返回完整文本。"""
        use_model = model or self.model
        try:
            resp = await self.client.chat.completions.create(
                model=use_model,
                messages=messages,
            )
        except Exception as e:
            raise RuntimeError(f"LLM连接失败: {type(e).__name__}: {e}") from e
        return resp.choices[0].message.content or ""

    async def chat_stream(
        self, messages: list[dict], model: str | None = None
    ) -> AsyncGenerator[str, None]:
        """流式对话，逐段产出文本增量。"""
        use_model = model or self.model
        try:
            stream = await self.client.chat.completions.create(
                model=use_model,
                messages=messages,
                stream=True,
            )
        except Exception as e:
            raise RuntimeError(f"LLM连接失败: {type(e).__name__}: {e}") from e

        async for event in stream:
            # OpenAI Python SDK v1：choices[0].delta.content
            try:
                delta = event.choices[0].delta
                content = getattr(delta, "content", None)
            except Exception:
                content = None
            if content:
                yield content

    async def aclose(self):
        try:
            await self.httpx_client.aclose()
        except Exception:
            pass


qwen_client = QwenClient()

