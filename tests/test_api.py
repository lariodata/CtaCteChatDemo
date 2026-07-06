"""
Tests para Etapa 5: FastAPI endpoints.

Requiere: pytest, httpx (cliente HTTP async para tests)

Correr:
    pytest tests/test_api.py -v -s
"""

import pytest
from fastapi.testclient import TestClient
from src.api import app


client = TestClient(app)


def test_api_health():
    """GET /health debe devolver 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    print("✓ Health check OK")


def test_api_tools_vendedor():
    """GET /tools/vendedor1 devuelve 4 tools (sin consulta_custom)."""
    response = client.get("/tools/vendedor1")
    assert response.status_code == 200
    data = response.json()
    assert data["usuario"] == "vendedor1"
    assert len(data["tools"]) == 3, "Vendedor debe tener 3 tools"
    tool_names = [t["name"] for t in data["tools"]]
    assert "consultar_deuda" in tool_names
    assert "detalle_movimientos" in tool_names
    assert "clientes_por_zona" in tool_names
    print("✓ Tools vendedor OK (3 tools)")


def test_api_tools_gerente():
    """GET /tools/gerente1 devuelve 4 tools (con consulta_custom)."""
    response = client.get("/tools/gerente1")
    assert response.status_code == 200
    data = response.json()
    assert data["usuario"] == "gerente1"
    assert len(data["tools"]) == 4, "Gerente debe tener 4 tools"
    tool_names = [t["name"] for t in data["tools"]]
    assert "consulta_custom" in tool_names, "Gerente debe tener consulta_custom"
    print("✓ Tools gerente OK (4 tools)")


def test_api_tools_invalid_user():
    """GET /tools/{usuario_inexistente} devuelve 400."""
    response = client.get("/tools/usuario_fantasma")
    assert response.status_code == 400
    print("✓ Invalid user rejected (400)")


def test_api_chat_request_schema():
    """POST /chat valida el schema del request."""
    # Falta 'usuario'
    response = client.post(
        "/chat",
        json={"mensaje": "hola"}
    )
    assert response.status_code == 422  # Unprocessable Entity (Pydantic validation error)
    print("✓ Request schema validation OK")


def test_api_chat_invalid_user():
    """POST /chat con usuario inválido devuelve 400."""
    response = client.post(
        "/chat",
        json={
            "usuario": "usuario_inexistente",
            "mensaje": "¿Cuánto debe el cliente 3523?",
            "max_iterations": 3
        }
    )
    assert response.status_code == 400
    print("✓ Invalid user in chat rejected (400)")


def test_api_chat_vendedor_deuda(mark_integration=True):
    """
    POST /chat: vendedor1 pregunta cuánto debe cliente 3523.

    Requiere:
      - BD operativa con datos de prueba
      - Ollama corriendo con qwen2.5:7b-instruct

    Nota: test de integración, puede ser lento (~10s).
    """
    response = client.post(
        "/chat",
        json={
            "usuario": "vendedor1",
            "mensaje": "¿Cuánto debe el cliente 3523?",
            "max_iterations": 3
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "respuesta" in data
    assert len(data["respuesta"]) > 10
    assert data["usuario"] == "vendedor1"
    assert data["iterations_used"] == 3
    print(f"✓ Chat vendedor OK: {data['respuesta'][:100]}...")


def test_api_chat_gerente_deuda_por_zona(mark_integration=True):
    """
    POST /chat: gerente1 pregunta deuda de zona 1.

    Requiere: BD + Ollama.
    """
    response = client.post(
        "/chat",
        json={
            "usuario": "gerente1",
            "mensaje": "¿Cuál es la deuda total de la zona 1?",
            "max_iterations": 3
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "respuesta" in data
    assert len(data["respuesta"]) > 10
    assert data["usuario"] == "gerente1"
    print(f"✓ Chat gerente OK: {data['respuesta'][:100]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "-k", "not integration"])
