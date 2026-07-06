"""
Capa de modelo: interfaz única para cualquier LLM.
Cambiar de Ollama/Qwen a Claude o GPT = cambiar la implementación, no el resto.
"""
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        """
        Recibe mensajes (formato OpenAI-like) y, opcionalmente, tools.
        Devuelve un dict normalizado:
          {
            "content": str | None,
            "tool_calls": [ {"name": str, "arguments": dict}, ... ]
          }
        Cada provider traduce desde/hacia su formato nativo.
        """
        raise NotImplementedError
