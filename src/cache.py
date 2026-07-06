"""
Cache en memoria con TTL para resultados de tools.

Responsabilidad:
  1. Almacenar resultados de tools en dict con TTL.
  2. Clave: hash(usuario, tool_name, arguments).
  3. Validar expiración antes de devolver.
  4. Logging de hits/misses para debugging.

Nota: Etapa 4 usa cache en memoria. Etapa 5+ podría usar Redis.
"""

import hashlib
import json
import time
from functools import wraps
from typing import Any, Callable


class SimpleCache:
    """Cache en memoria con TTL."""

    def __init__(self):
        self._store: dict[str, tuple[Any, float]] = {}
        self._hits = 0
        self._misses = 0

    def _make_key(self, usuario: str, tool_name: str, arguments: dict) -> str:
        """Genera clave hash única para (usuario, tool_name, arguments)."""
        data = f"{usuario}:{tool_name}:{json.dumps(arguments, sort_keys=True)}"
        return hashlib.sha256(data.encode()).hexdigest()

    def get(self, usuario: str, tool_name: str, arguments: dict) -> Any | None:
        """Devuelve valor si existe y no está expirado. None si no existe o expiró."""
        key = self._make_key(usuario, tool_name, arguments)

        if key not in self._store:
            self._misses += 1
            return None

        value, expiry = self._store[key]
        if time.time() > expiry:
            del self._store[key]
            self._misses += 1
            return None

        self._hits += 1
        return value

    def set(self, usuario: str, tool_name: str, arguments: dict, value: Any, ttl_seconds: int) -> None:
        """Almacena valor con TTL."""
        key = self._make_key(usuario, tool_name, arguments)
        expiry = time.time() + ttl_seconds
        self._store[key] = (value, expiry)

    def clear(self) -> None:
        """Limpia toda la cache."""
        self._store.clear()
        self._hits = 0
        self._misses = 0

    def stats(self) -> dict:
        """Devuelve estadísticas de cache (hits, misses, ratio)."""
        total = self._hits + self._misses
        ratio = self._hits / total if total > 0 else 0
        return {
            "hits": self._hits,
            "misses": self._misses,
            "total_requests": total,
            "hit_ratio": ratio,
            "cached_items": len(self._store)
        }


# Instancia global de cache
_cache = SimpleCache()


def with_cache(ttl_seconds: int) -> Callable:
    """
    Decorador para cachear resultados de funciones.

    Clave de cache: hash(usuario, tool_name, arguments).
    TTL: ttl_seconds (segundos).

    Uso:
        @with_cache(ttl_seconds=300)
        def _execute_consulta_custom(usuario: str, intent: str, ...):
            ...

    Args:
        ttl_seconds: tiempo de vida de la cache en segundos.

    Returns:
        Función decorada con cache automática.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(usuario: str, tool_name: str, arguments: dict, *args, **kwargs) -> Any:
            # Intenta obtener del cache
            cached = _cache.get(usuario, tool_name, arguments)
            if cached is not None:
                print(f"[CACHE HIT] usuario={usuario}, tool={tool_name}")
                return cached

            # Si no está en cache, ejecuta la función
            print(f"[CACHE MISS] usuario={usuario}, tool={tool_name}")
            result = func(usuario, tool_name, arguments, *args, **kwargs)

            # Almacena en cache
            _cache.set(usuario, tool_name, arguments, result, ttl_seconds)
            return result

        return wrapper
    return decorator


def get_cache_stats() -> dict:
    """Devuelve estadísticas de la cache global."""
    return _cache.stats()


def clear_cache() -> None:
    """Limpia la cache global (útil para testing)."""
    _cache.clear()
