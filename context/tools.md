# Tools del asistente (JSON Schema)

Cada tool mapea 1:1 a un Stored Procedure `chat_*`. El modelo SOLO puede
elegir de esta lista. La **zona (`nrorep`) NO está en el schema**: la inyecta
la app desde el rol del usuario. Así el modelo no puede salirse de su zona.

```json
[
  {
    "name": "consultar_deuda",
    "description": "Devuelve el saldo y la deuda total de UN cliente por su id interno. Usar cuando se pregunta cuánto debe un cliente puntual. No sirve para listar varios.",
    "input_schema": {
      "type": "object",
      "properties": {
        "cliente_id": {
          "type": "integer",
          "description": "ID interno del cliente (nrocli). No inventar; identificarlo antes."
        }
      },
      "required": ["cliente_id"],
      "additionalProperties": false
    }
  },
  {
    "name": "detalle_movimientos",
    "description": "Devuelve el detalle de facturas, notas de crédito y recibos de UN cliente en los últimos N meses. Usar cuando piden 'el detalle' o 'los movimientos'.",
    "input_schema": {
      "type": "object",
      "properties": {
        "cliente_id": { "type": "integer", "description": "ID interno del cliente." },
        "meses": { "type": "integer", "description": "Meses hacia atrás. Default 6.", "default": 6 }
      },
      "required": ["cliente_id"],
      "additionalProperties": false
    }
  },
  {
    "name": "clientes_por_zona",
    "description": "Lista los clientes con deuda de la zona del usuario, ordenados por deuda. La zona la determina el sistema según el rol; el modelo no la pasa.",
    "input_schema": {
      "type": "object",
      "properties": {
        "solo_con_deuda": { "type": "boolean", "description": "Si true, solo los que deben. Default true.", "default": true }
      },
      "required": [],
      "additionalProperties": false
    }
  }
]
```

## Tool genérica acotada (gerente) — Etapa 4

`consulta_custom(intent, filtros)` donde `intent` es un **enum cerrado**
(p.ej. `deuda_por_zona`, `top_morosos`, `resumen_zonas`). Cada intent mapea a un
SP `chat_*`. **No recibe SQL**: es la versión con guardarriles del "híbrido pragmático".
