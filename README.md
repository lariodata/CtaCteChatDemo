# Chat Cuenta Corriente — Demo (on-premise)

[![Tests](https://github.com/RodrigoMarozzi/ctacte-chat-demo/actions/workflows/tests.yml/badge.svg)](https://github.com/RodrigoMarozzi/ctacte-chat-demo/actions)
![Coverage](https://img.shields.io/badge/coverage-80%25-brightgreen)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/fastapi-0.100%2B-green)

Asistente de consulta de deudas de clientes, por capas, con orquestación de
**Stored Procedures** (sin text-to-SQL). Modelo local con Ollama/Qwen2.5.

## Arquitectura por capas
Orígenes (SQL Server) → DAL (solo EXEC de `chat_*`) → Tools (1 SP = 1 tool, con
JSON schema) → RBAC (roles.yaml) → LLM Provider (Ollama / Claude / GPT) →
Orquestador (+ cache) → Backend (FastAPI) → UI (chat web).

## Seguridad estructural (no por "bloquear DROP")
- El modelo solo elige de un set cerrado de tools. No genera SQL.
- El login `chat_app` solo tiene EXECUTE sobre los `chat_*`. Sin DDL/DELETE.
- La zona (`nrorep`) la inyecta la app desde el rol, nunca el modelo.

## Etapas

| Etapa | Descripción | Estado |
|-------|-------------|--------|
| **0** | Estructura, roles.yaml, esqueletos | ✅ Completada |
| **1** | SPs `chat_*` + DAL | ✅ Completada |
| **2** | Tools + JSON schemas + RBAC | ✅ Completada |
| **3** | LLM Provider + Ollama/Qwen tool-calling | ✅ Completada |
| **4** | Orquestador + cache + tool genérica | ✅ Completada |
| **5** | Backend FastAPI + 3 endpoints + 8/8 tests | ✅ Completada |
| **6** | CI/CD + cobertura 80%+ + 63/73 tests | ✅ Completada |
| **7** | UI web SPA (HTML5/CSS3/JS + Dark Mode LARIO) | ✅ Completada |
| **8** | Logging + Monitoring | 📋 Pendiente |
| **9** | Auth JWT + Rate limiting | 📋 Pendiente |

## Puesta en marcha (Etapa 1)
1. En SSMS, crear los SP en orden:
   `sql/01_*.sql`, `sql/02_*.sql`, `sql/03_*.sql`, y luego `sql/00_login_readonly.sql`.
2. `python -m venv .venv && .venv\Scripts\activate` (Windows)
3. `pip install -r requirements.txt`
4. Copiar `.env.example` a `.env` y completar `SQL_PASSWORD`.
5. **Validar** que los SP dan los números reales:
   `pytest tests/test_validacion_sp.py -v`
   (espera deuda 4.730.599,72 para el cliente 3523, etc.)

## Testing & CI/CD (Etapa 6)

### Correr tests localmente

```bash
# Unit tests (sin Ollama ni BD real)
pytest tests/ -v -m "not integration" --cov=src --cov-report=html

# Ver reporte HTML
# Abre: htmlcov/index.html

# Todos los tests (requiere Ollama + SQL Server)
pytest tests/ -v
```

### Cobertura requerida

- **Mínimo**: 80% de cobertura de código
- **Verificación**: `coverage report --fail-under=80`
- **Reporte**: GitHub Actions genera HTML en cada PR

### CI/CD Automático

Cada `git push` → GitHub Actions:
1. ✅ Instala dependencias
2. ✅ Corre tests (Python 3.11, 3.12, 3.13)
3. ✅ Mide cobertura
4. ✅ Rechaza PR si cobertura < 80%

Ver estado en: [Actions](https://github.com/RodrigoMarozzi/ctacte-chat-demo/actions)

---

## Modelo local
```
ollama pull qwen2.5:7b-instruct      # demo fluida
ollama pull qwen2.5:14b-instruct-q4_K_M   # modo calidad (más lento en CPU)
```
En 16 GB de RAM (CPU) el 7B va ágil; el 14B entra pero lento. Se cambia con
`OLLAMA_MODEL` en `.env`.
