"""
Proveedor Ollama (Qwen2.5). Usa la API /api/chat con tool-calling nativo.
Doc: https://github.com/ollama/ollama/blob/main/docs/api.md
"""
import httpx
from .base import LLMProvider
from .. import config


class OllamaProvider(LLMProvider):
    def __init__(self, host: str | None = None, model: str | None = None):
        self.host = host or config.OLLAMA_HOST
        self.model = model or config.OLLAMA_MODEL

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.1, "num_ctx": 8192},
        }
        if tools:
            payload["tools"] = tools

        r = httpx.post(f"{self.host}/api/chat", json=payload, timeout=180)
        r.raise_for_status()
        msg = r.json()["message"]

        tool_calls = []
        for tc in msg.get("tool_calls", []) or []:
            fn = tc["function"]
            tool_calls.append({"name": fn["name"], "arguments": fn.get("arguments", {})})

        return {"content": msg.get("content"), "tool_calls": tool_calls}
