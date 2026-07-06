# API HTTP (Etapa 5)

## Inicio rápido

### 1. Arranca el servidor

```bash
python main_api.py
```

La API estará disponible en `http://localhost:8000`

Documentación interactiva:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 2. Llamadas de ejemplo

#### Health check
```bash
curl http://localhost:8000/health
```

#### Obtener tools disponibles para un usuario
```bash
curl http://localhost:8000/tools/vendedor1
```

#### Enviar un chat
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "usuario": "vendedor1",
    "mensaje": "¿Cuánto debe el cliente 3523?",
    "max_iterations": 3
  }'
```

#### Reportes de gerente
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "usuario": "gerente1",
    "mensaje": "¿Cuál es la deuda total de la zona 1?",
    "max_iterations": 3
  }'
```

---

## Endpoints

### `GET /health`

Health check simple.

**Response:**
```json
{
  "status": "ok",
  "message": "ctacte-chat-demo API está operativa"
}
```

---

### `GET /tools/{usuario}`

Devuelve los tools disponibles para un usuario.

**Parámetros:**
- `usuario` (path): ID del usuario (ej. `vendedor1`, `gerente1`)

**Response (200):**
```json
{
  "usuario": "vendedor1",
  "tools": [
    {
      "name": "consultar_deuda",
      "description": "Devuelve el saldo y la deuda total de UN cliente..."
    },
    {
      "name": "detalle_movimientos",
      "description": "Devuelve el detalle de facturas, notas de crédito..."
    },
    {
      "name": "clientes_por_zona",
      "description": "Lista los clientes con deuda de la zona del usuario..."
    }
  ]
}
```

**Errores:**
- `400`: Usuario no existe
- `500`: Error interno

---

### `POST /chat`

Endpoint principal: envía un mensaje al chat, devuelve respuesta del LLM.

**Request:**
```json
{
  "usuario": "string",
  "mensaje": "string",
  "max_iterations": 3
}
```

**Parámetros:**
- `usuario` (required): ID del usuario (ej. `vendedor1`, `gerente1`)
- `mensaje` (required): Pregunta o comando del usuario
- `max_iterations` (optional, default=3): Máximo de iteraciones LLM→tool (1-10)

**Response (200):**
```json
{
  "respuesta": "El cliente 3523 (PINTO HERMANOS S.A.) debe $4,730,599.72...",
  "usuario": "vendedor1",
  "iterations_used": 3
}
```

**Errores:**
- `400`: Usuario inválido, validación fallida
- `403`: Usuario sin permisos para esa operación
- `422`: Schema incorrecto (Pydantic validation)
- `500`: Error interno (BD, LLM, etc)

---

## Cliente Python

Usa `client_api_example.py` para probar desde Python:

```bash
# Health check
python client_api_example.py health

# Listar tools
python client_api_example.py tools vendedor1

# Chat
python client_api_example.py chat vendedor1 "¿Cuánto debe el cliente 3523?"

# Gerente consultando reportes
python client_api_example.py chat gerente1 "¿Cuál es la deuda total de la zona 1?"
```

---

## Usuarios disponibles

| Usuario | Rol | Zonas | Tools |
|---------|-----|-------|-------|
| `vendedor1` | vendedor | 1 | 3 (consultar_deuda, detalle_movimientos, clientes_por_zona) |
| `vendedor2` | vendedor | 2, 3 | 3 (idem) |
| `gerente1` | gerente | * (todas) | 4 (idem + consulta_custom) |

---

## Validación y seguridad

1. **RBAC**: Solo usuarios válidos pueden acceder.
2. **Inyección de zona**: Vendedores solo ven su zona(s); gerentes eligen explícitamente.
3. **Tool whitelist**: El LLM solo puede usar los tools disponibles para el usuario.
4. **SQL parametrizado**: Todas las queries usan parámetros (sin inyección SQL).

---

## Ejemplos de uso real

### Vendedor consultando deuda de un cliente
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "usuario": "vendedor1",
    "mensaje": "¿Cuánto debe PINTO HERMANOS?",
    "max_iterations": 5
  }'
```

### Vendedor listando clientes morosos de su zona
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "usuario": "vendedor1",
    "mensaje": "Dame los clientes con mayor deuda de mi zona",
    "max_iterations": 5
  }'
```

### Gerente obtiene reportes consolidados
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "usuario": "gerente1",
    "mensaje": "¿Cuál es el resumen de la zona 2? Dame los totales, promedios y mora promedio",
    "max_iterations": 5
  }'
```

### Gerente compara zonas
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "usuario": "gerente1",
    "mensaje": "Comparame la deuda total entre zona 1 y zona 2",
    "max_iterations": 5
  }'
```

---

## Limitaciones y próximos pasos

### Actual (Etapa 5)
- Single API endpoint `/chat` (sin persistencia).
- Autenticación básica (validación de usuario).
- Cache en memoria (TTL) compartido entre requests.

### Próximos (Etapa 6+)
- Autenticación OAuth / JWT.
- Persistencia de conversaciones (DB).
- Logging y auditoría.
- Rate limiting.
- WebSocket para streaming de respuestas.
- Admin endpoints para CRUD de usuarios/permisos.

---

## Debugging

### Ver logs en tiempo real
```bash
uvicorn main_api:app --host 127.0.0.1 --port 8000 --log-level debug
```

### Probar conexión a BD
Desde Python:
```python
from src import dal
dal._connect()  # Si no lanza excepción, BD está OK
```

### Probar Ollama
```bash
curl http://localhost:11434/api/tags
```

Debe devolver lista de modelos disponibles.
