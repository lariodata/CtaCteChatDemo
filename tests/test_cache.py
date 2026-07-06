"""
Tests para el módulo de cache (Etapa 4).

Validar:
  1. Cache hit/miss básico.
  2. TTL expiración.
  3. Clave única por (usuario, tool_name, arguments).
  4. Estadísticas (hits, misses, ratio).
"""

import time
import pytest
from src.cache import SimpleCache, clear_cache, get_cache_stats


class TestSimpleCache:
    """Test suite para SimpleCache."""

    def setup_method(self):
        """Limpia cache antes de cada test."""
        clear_cache()

    def test_cache_hit_miss_basic(self):
        """Valida hit/miss básico."""
        cache = SimpleCache()

        # Miss inicial
        result = cache.get("user1", "tool1", {"arg": "value"})
        assert result is None
        assert cache.stats()["misses"] == 1

        # Set valor
        cache.set("user1", "tool1", {"arg": "value"}, {"result": "data"}, ttl_seconds=60)

        # Hit
        result = cache.get("user1", "tool1", {"arg": "value"})
        assert result == {"result": "data"}
        assert cache.stats()["hits"] == 1

    def test_cache_expiration(self):
        """Valida expiración por TTL."""
        cache = SimpleCache()

        # Set con TTL de 1 segundo
        cache.set("user1", "tool1", {"arg": "x"}, {"data": "value"}, ttl_seconds=1)

        # Hit inmediato
        result = cache.get("user1", "tool1", {"arg": "x"})
        assert result == {"data": "value"}

        # Esperar a que expire
        time.sleep(1.1)

        # Miss porque expiró
        result = cache.get("user1", "tool1", {"arg": "x"})
        assert result is None

    def test_cache_key_uniqueness(self):
        """Valida que claves diferentes produzcan resultados diferentes."""
        cache = SimpleCache()

        # Set dos valores con argumentos diferentes
        cache.set("user1", "tool1", {"arg": "x"}, {"result": "X"}, ttl_seconds=60)
        cache.set("user1", "tool1", {"arg": "y"}, {"result": "Y"}, ttl_seconds=60)
        cache.set("user2", "tool1", {"arg": "x"}, {"result": "Z"}, ttl_seconds=60)

        # Cada clave debe devolver su valor
        assert cache.get("user1", "tool1", {"arg": "x"}) == {"result": "X"}
        assert cache.get("user1", "tool1", {"arg": "y"}) == {"result": "Y"}
        assert cache.get("user2", "tool1", {"arg": "x"}) == {"result": "Z"}
        assert cache.get("user1", "tool2", {"arg": "x"}) is None

    def test_cache_stats(self):
        """Valida estadísticas de cache."""
        cache = SimpleCache()

        # 3 misses
        cache.get("u1", "t1", {})
        cache.get("u1", "t2", {})
        cache.get("u1", "t3", {})

        # 2 hits
        cache.set("u1", "t1", {}, "data1", 60)
        cache.get("u1", "t1", {})
        cache.set("u1", "t2", {}, "data2", 60)
        cache.get("u1", "t2", {})

        stats = cache.stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 3
        assert stats["total_requests"] == 5
        assert stats["hit_ratio"] == 2 / 5

    def test_cache_clear(self):
        """Valida que clear() limpia todo."""
        cache = SimpleCache()

        cache.set("u1", "t1", {}, "data", 60)
        cache.set("u1", "t2", {}, "data", 60)
        assert cache.stats()["cached_items"] == 2

        cache.clear()

        assert cache.stats()["cached_items"] == 0
        assert cache.stats()["hits"] == 0
        assert cache.stats()["misses"] == 0

    def test_cache_json_key_ordering(self):
        """Valida que argumentos con distinto orden de keys produzcan la misma clave."""
        cache = SimpleCache()

        # Mismo contenido, diferente orden de keys
        args1 = {"a": 1, "b": 2}
        args2 = {"b": 2, "a": 1}

        cache.set("user", "tool", args1, "result", 60)

        # Debe encontrar el mismo resultado con keys en orden diferente
        result = cache.get("user", "tool", args2)
        assert result == "result"


class TestGlobalCacheStats:
    """Test suite para estadísticas globales de cache."""

    def setup_method(self):
        clear_cache()

    def test_global_cache_stats(self):
        """Valida que get_cache_stats() devuelve stats globales."""
        stats = get_cache_stats()
        assert isinstance(stats, dict)
        assert "hits" in stats
        assert "misses" in stats
        assert "hit_ratio" in stats
        assert "cached_items" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
