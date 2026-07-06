"""Factory de providers LLM: selecciona la implementación según nombre."""
from .base import LLMProvider

PROVIDERS_VALIDOS = ("ollama", "claude_haiku")


def get_provider(nombre: str | None = None) -> LLMProvider:
    """
    Devuelve una instancia de LLMProvider según el nombre pedido.

    Args:
        nombre: "ollama" | "claude_haiku". Si None, usa config.LLM_PROVIDER (default "ollama").

    Returns:
        Instancia de LLMProvider lista para usar en el orquestador.

    Raises:
        ValueError: si el nombre no es un provider soportado.
    """
    from .. import config

    nombre = (nombre or config.LLM_PROVIDER).lower()

    if nombre == "ollama":
        from .ollama_provider import OllamaProvider
        return OllamaProvider()

    if nombre == "claude_haiku":
        from .claude_provider import ClaudeHaikuProvider
        return ClaudeHaikuProvider()

    raise ValueError(f"Provider LLM desconocido: '{nombre}'. Válidos: {PROVIDERS_VALIDOS}")
