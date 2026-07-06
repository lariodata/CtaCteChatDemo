"""
Proveedor Claude Haiku (Anthropic). Usa el SDK oficial `anthropic`.
Doc: https://docs.anthropic.com/en/api/messages

Traduce entre el formato de mensajes/tools estilo Ollama (usado por el
orquestador) y el formato nativo de la API de Claude:
  - "system" (mensaje) -> parámetro top-level `system`.
  - tools {"type":"function","function":{...}} -> {"name","description","input_schema"}.
  - tool_calls del asistente -> content blocks {"type":"tool_use", "id", "name", "input"}.
  - mensajes "tool" -> content blocks {"type":"tool_result","tool_use_id","content"} agrupados
    en un mensaje "user" (requisito de la API de Claude).
"""
import uuid
import anthropic
from .base import LLMProvider
from .. import config

MAX_TOKENS = 4096


class ClaudeHaikuProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.client = anthropic.Anthropic(api_key=api_key or config.ANTHROPIC_API_KEY)
        self.model = model or config.ANTHROPIC_MODEL

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        system_prompt, claude_messages = self._convertir_mensajes(messages)

        kwargs = {
            "model": self.model,
            "max_tokens": MAX_TOKENS,
            "messages": claude_messages,
        }
        if system_prompt:
            kwargs["system"] = system_prompt
        if tools:
            kwargs["tools"] = self._convertir_tools(tools)

        response = self.client.messages.create(**kwargs)

        content_text = None
        tool_calls = []
        for block in response.content:
            if block.type == "text":
                content_text = (content_text or "") + block.text
            elif block.type == "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "name": block.name,
                    "arguments": block.input,
                })

        return {"content": content_text, "tool_calls": tool_calls}

    @staticmethod
    def _convertir_tools(tools: list[dict]) -> list[dict]:
        claude_tools = []
        for t in tools:
            fn = t["function"]
            claude_tools.append({
                "name": fn["name"],
                "description": fn.get("description", ""),
                "input_schema": fn.get("parameters", {"type": "object", "properties": {}}),
            })
        return claude_tools

    @staticmethod
    def _convertir_mensajes(messages: list[dict]) -> tuple[str | None, list[dict]]:
        system_prompt = None
        claude_messages = []
        pending_tool_ids: list[str] = []
        tool_result_buffer: list[dict] = []

        def flush_tool_results():
            if tool_result_buffer:
                claude_messages.append({"role": "user", "content": list(tool_result_buffer)})
                tool_result_buffer.clear()

        for msg in messages:
            role = msg["role"]

            if role == "system":
                system_prompt = msg["content"]
                continue

            if role == "user":
                flush_tool_results()
                claude_messages.append({"role": "user", "content": msg["content"]})
                continue

            if role == "assistant":
                flush_tool_results()
                content_blocks = []
                if msg.get("content"):
                    content_blocks.append({"type": "text", "text": msg["content"]})

                pending_tool_ids = []
                for tc in msg.get("tool_calls") or []:
                    tc_id = tc.get("id") or f"toolu_{uuid.uuid4().hex[:16]}"
                    pending_tool_ids.append(tc_id)
                    content_blocks.append({
                        "type": "tool_use",
                        "id": tc_id,
                        "name": tc["name"],
                        "input": tc.get("arguments", {}),
                    })

                claude_messages.append({"role": "assistant", "content": content_blocks})
                continue

            if role == "tool":
                tc_id = pending_tool_ids.pop(0) if pending_tool_ids else f"toolu_{uuid.uuid4().hex[:16]}"
                tool_result_buffer.append({
                    "type": "tool_result",
                    "tool_use_id": tc_id,
                    "content": msg.get("content", ""),
                })
                continue

        flush_tool_results()
        return system_prompt, claude_messages
