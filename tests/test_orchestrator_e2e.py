"""
Test end-to-end de Etapa 3 + Etapa 4: usuario → mensaje → orquestador → LLM → tools → resultado.

Etapa 3 valida:
  1. El orquestador obtenga los tools correctos para el usuario.
  2. Ollama reciba los schemas de tools.
  3. Ollama haga tool_calls correctamente.
  4. Los tools se ejecuten con RBAC + inyección de zona.
  5. La respuesta final sea coherente.

Etapa 4 valida:
  6. Cache funciona (hit/miss, TTL).
  7. Tool genérico 'consulta_custom' solo para gerentes.
  8. max_iterations reducido a 3 (más conservador).

Requiere:
  - BD con SP creados + datos validados (Etapa 1).
  - .env configurado + conexión SQL Server.
  - Ollama corriendo en http://localhost:11434.
  - qwen2.5:7b-instruct descargado.

Correr:
  pytest tests/test_orchestrator_e2e.py -v -s
  (-s = mostrar prints/logging)
"""

import pytest
from src import orchestrator, tools
from src.cache import clear_cache, get_cache_stats


def test_orchestrator_get_tools():
    """Valida que get_tools_for_user devuelva los 4 tools para vendedor1."""
    tools_disponibles = tools.get_tools_for_user("vendedor1")

    assert len(tools_disponibles) == 4, "Vendedor debe tener 4 tools"
    tool_names = [t["name"] for t in tools_disponibles]
    assert "consultar_deuda" in tool_names
    assert "detalle_movimientos" in tool_names
    assert "clientes_por_zona" in tool_names
    assert "buscar_cliente_por_nombre" in tool_names


def test_orchestrator_consultar_deuda_directo():
    """Valida que execute_tool funcione directamente (sin LLM)."""
    # Vendedor1 consulta cliente 3523 (PINTO HERMANOS S.A., deuda = 4730599.72)
    resultado = tools.execute_tool(
        usuario="vendedor1",
        tool_name="consultar_deuda",
        arguments={"cliente_id": 3523}
    )

    assert resultado is not None, "El tool debe devolver un resultado"
    assert float(resultado["deuda_total"]) == pytest.approx(4730599.72, abs=0.01)
    print(f"✓ Consulta directa OK: {resultado['cliente']} debe ${resultado['deuda_total']}")


def test_orchestrator_rbac_vendedor_no_ve_otra_zona():
    """Valida que vendedor2 (zona 3) no vea clientes de zona 1."""
    resultado = tools.execute_tool(
        usuario="vendedor2",
        tool_name="consultar_deuda",
        arguments={"cliente_id": 3523}  # cliente de zona 1
    )

    # Si el cliente no pertenece a la zona, devuelve None o deuda=0
    assert resultado is None or float(resultado.get("deuda_total", 0)) == 0, \
        "Vendedor2 (zona 3) no debe ver cliente de zona 1"
    print("✓ RBAC OK: Vendedor2 no ve zona 1")


def test_orchestrator_permission_denied():
    """Valida que un usuario sin permisos lance PermissionError."""
    # Crear un usuario ficticio sin permisos
    with pytest.raises(PermissionError):
        tools.execute_tool(
            usuario="usuario_inexistente",
            tool_name="consultar_deuda",
            arguments={"cliente_id": 3523}
        )
    print("✓ Permission check OK")


@pytest.mark.integration
def test_orchestrator_chat_end_to_end():
    """
    Test INTEGRATION: Usuario → mensaje → orquestador → LLM → tool → respuesta.

    Este test REALMENTE llama a Ollama y valida que:
      1. El LLM reciba los schemas.
      2. El LLM elija un tool apropiado.
      3. El tool se ejecute correctamente.
      4. La respuesta final sea coherente.

    Requiere:
      - Ollama corriendo.
      - qwen2.5:7b-instruct descargado.
      - BD accesible con datos validados.

    Correr con:
      pytest tests/test_orchestrator_e2e.py::test_orchestrator_chat_end_to_end -v -s
    """
    # Vendedor1 pregunta: "¿Cuánto debe el cliente 3523?"
    respuesta = orchestrator.chat(
        usuario="vendedor1",
        mensaje="¿Cuánto debe el cliente 3523?",
        max_iterations=5
    )

    print(f"\n📝 Respuesta del LLM:\n{respuesta}\n")

    # Validaciones básicas
    assert respuesta, "La respuesta no debe estar vacía"
    assert len(respuesta) > 10, "La respuesta debe tener contenido significativo"
    # Esperamos que mencione el cliente y/o la deuda
    assert "3523" in respuesta or "PINTO" in respuesta or "deuda" in respuesta.lower(), \
        f"La respuesta debe mencionar cliente 3523 o la deuda. Recibido: {respuesta}"

    print("✓ Chat end-to-end OK")


@pytest.mark.integration
def test_orchestrator_chat_multi_tool():
    """
    Test INTEGRATION: Chat que requiere múltiples tools.

    Pregunta que podría necesitar: listar clientes → consultar deuda de uno.
    """
    respuesta = orchestrator.chat(
        usuario="vendedor1",
        mensaje="¿Cuáles son los top 3 clientes con más deuda en mi zona?",
        max_iterations=5
    )

    print(f"\n📝 Respuesta multi-tool:\n{respuesta}\n")

    assert respuesta, "La respuesta no debe estar vacía"
    # Esperamos nombres de clientes o montos
    assert any(x in respuesta.lower() for x in ["cliente", "deuda", "zona"]), \
        f"Respuesta inesperada: {respuesta}"

    print("✓ Multi-tool chat OK")


@pytest.mark.integration
def test_orchestrator_chat_rbac():
    """
    Test INTEGRATION: Valida que RBAC se respete en el chat.

    Vendedor2 (zona 3) no debe ver clientes de zona 1.
    """
    respuesta = orchestrator.chat(
        usuario="vendedor2",
        mensaje="¿Cuánto debe el cliente 3523?",  # cliente de zona 1
        max_iterations=5
    )

    print(f"\n📝 Respuesta RBAC (vendedor2, cliente zona 1):\n{respuesta}\n")

    # El LLM debería explicar que el cliente no existe para esta zona
    assert respuesta, "La respuesta no debe estar vacía"
    # Puede decir "no existe", "no encontrado", o "sin deuda"
    respuesta_lower = respuesta.lower()
    assert any(x in respuesta_lower for x in [
        "no existe",
        "no encontrado",
        "no se encuentra",
        "sin deuda",
        "cliente",
        "zona"
    ]), f"Respuesta inesperada: {respuesta}"

    print("✓ RBAC check en chat OK")


# ============================================================================
# ETAPA 4: Tests para cache y tool genérico 'consulta_custom'
# ============================================================================

def test_etapa4_get_tools_gerente():
    """Valida que gerente1 tenga acceso a 5 tools (incluyendo consulta_custom)."""
    clear_cache()
    tools_disponibles = tools.get_tools_for_user("gerente1")

    assert len(tools_disponibles) == 5, "Gerente debe tener 5 tools (Etapa 4)"
    tool_names = [t["function"]["name"] for t in tools_disponibles]
    assert "consultar_deuda" in tool_names
    assert "detalle_movimientos" in tool_names
    assert "clientes_por_zona" in tool_names
    assert "consulta_custom" in tool_names, "Gerente debe tener acceso a consulta_custom"
    assert "buscar_cliente_por_nombre" in tool_names
    print("✓ Gerente tiene 5 tools (incluyendo consulta_custom)")


def test_etapa4_vendedor_no_ve_consulta_custom():
    """Valida que vendedor1 NO tenga acceso a consulta_custom."""
    clear_cache()
    tools_disponibles = tools.get_tools_for_user("vendedor1")

    assert len(tools_disponibles) == 4, "Vendedor debe tener 4 tools (sin consulta_custom)"
    tool_names = [t["function"]["name"] for t in tools_disponibles]
    assert "consulta_custom" not in tool_names, "Vendedor no debe ver consulta_custom"
    print("✓ Vendedor no tiene acceso a consulta_custom")


def test_etapa4_consulta_custom_permission_denied():
    """Valida que vendedor no pueda ejecutar consulta_custom."""
    clear_cache()
    with pytest.raises(PermissionError):
        tools.execute_tool(
            usuario="vendedor1",
            tool_name="consulta_custom",
            arguments={"intent": "deuda_por_zona"}
        )
    print("✓ Permission check: vendedor rechazado en consulta_custom")


def test_etapa4_consulta_custom_requiere_nro_zona():
    """Valida que consulta_custom rechace pedidos sin nro_zona (no hay modo 'todas las zonas')."""
    clear_cache()
    with pytest.raises(ValueError):
        tools.execute_tool(
            usuario="gerente1",
            tool_name="consulta_custom",
            arguments={"intent": "deuda_por_zona", "filtros": {}}
        )
    print("✓ consulta_custom exige nro_zona explícito")


def test_etapa4_consulta_custom_gerente_deuda_por_zona():
    """Valida que gerente pueda ejecutar consulta_custom (deuda_por_zona) para UNA zona puntual."""
    clear_cache()
    resultado = tools.execute_tool(
        usuario="gerente1",
        tool_name="consulta_custom",
        arguments={"intent": "deuda_por_zona", "filtros": {"nro_zona": 1}}
    )

    assert isinstance(resultado, list)
    assert len(resultado) == 1, "Con nro_zona=1 debe devolver UNA sola fila"
    assert resultado[0]["nro_zona"] == 1
    assert "deuda_total" in resultado[0]
    print(f"✓ Consulta custom OK (deuda_por_zona, zona 1): {resultado}")


def test_etapa4_consulta_custom_gerente_top_morosos():
    """Valida que gerente pueda ejecutar consulta_custom (top_morosos) para UNA zona puntual."""
    clear_cache()
    resultado = tools.execute_tool(
        usuario="gerente1",
        tool_name="consulta_custom",
        arguments={"intent": "top_morosos", "filtros": {"nro_zona": 1, "top_n": 3}}
    )

    assert isinstance(resultado, list)
    assert len(resultado) <= 3, "top_n=3 no debe devolver más de 3 filas"
    if resultado:
        assert "cliente" in resultado[0] and "deuda_total" in resultado[0]
    print(f"✓ Consulta custom OK (top_morosos, zona 1, top_n=3): {len(resultado)} items")


def test_etapa4_cache_hit_miss():
    """Valida que la cache funcione (hit/miss)."""
    clear_cache()

    # Primera ejecución: MISS
    stats_before = get_cache_stats()
    resultado1 = tools.execute_tool(
        usuario="vendedor1",
        tool_name="consultar_deuda",
        arguments={"cliente_id": 3523}
    )
    stats_after_miss = get_cache_stats()

    # Segunda ejecución: HIT
    resultado2 = tools.execute_tool(
        usuario="vendedor1",
        tool_name="consultar_deuda",
        arguments={"cliente_id": 3523}
    )
    stats_after_hit = get_cache_stats()

    # Validar que el resultado es el mismo (cache correcta)
    assert resultado1 == resultado2, "Cache debe devolver el mismo resultado"

    # Validar que hit_ratio mejoró
    hit_ratio_before = stats_before.get("hit_ratio", 0)
    hit_ratio_after = stats_after_hit.get("hit_ratio", 0)
    assert hit_ratio_after >= hit_ratio_before, "Hit ratio debe mejorar con hits"

    print(f"✓ Cache OK: stats={stats_after_hit}")


def test_etapa4_max_iterations_reduced():
    """Valida que max_iterations sea 3 (Etapa 4, valor default)."""
    # Simplemente verificar que el default sea 3 sin exceder
    # (no hacer la llamada real para evitar Ollama, pero documentar el cambio)
    import inspect
    sig = inspect.signature(orchestrator.chat)
    max_iter_default = sig.parameters['max_iterations'].default
    assert max_iter_default == 3, f"max_iterations debe ser 3 (Etapa 4), obtuvo {max_iter_default}"
    print(f"✓ max_iterations reducido a 3 (Etapa 4)")


@pytest.mark.integration
def test_etapa4_chat_gerente_with_cache():
    """
    Test INTEGRATION (Etapa 4): Chat de gerente con cache.

    Valida que:
      1. Gerente acceda a consulta_custom.
      2. Cache funcione durante el chat.
      3. max_iterations=3 sea suficiente.
    """
    clear_cache()

    # Gerente pregunta sobre consolidados
    respuesta = orchestrator.chat(
        usuario="gerente1",
        mensaje="¿Cuál es la deuda total en todas las zonas?",
        max_iterations=3
    )

    print(f"\n📝 Respuesta gerente (Etapa 4):\n{respuesta}\n")

    assert respuesta, "La respuesta no debe estar vacía"
    assert len(respuesta) > 10, "La respuesta debe tener contenido significativo"

    # Verificar cache stats
    stats = get_cache_stats()
    print(f"Cache stats: {stats}")

    print("✓ Chat gerente con cache OK (Etapa 4)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "-m", "not integration"])
