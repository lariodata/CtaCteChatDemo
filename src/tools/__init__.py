"""
Capa de Tools: Registry y Executor con RBAC + inyección de zona.

Responsabilidad:
  1. Definir los schemas JSON de los 3 tools (consultar_deuda, detalle_movimientos, clientes_por_zona).
  2. Ejecutar tools validando:
     - Que el usuario tenga permiso RBAC para el tool.
     - Que la zona se inyecte desde el rol del usuario, NUNCA desde parámetros del usuario.
  3. Devolver resultados en formato normalizado listo para el LLM.

Seguridad:
  - El modelo SOLO elige de los 3 tools cerrados; no puede inventar tools.
  - La zona (nrorep) la inyecta la app desde rbac.zona_default(), nunca llega desde el usuario.
  - Cada tool valida can_use_tool(usuario, tool_name) antes de ejecutar.

Flujo:
  1. El orquestador llama a get_tools_for_user(usuario) -> schemas JSON para el LLM.
  2. El LLM elige un tool y parámetros.
  3. El orquestador llama a execute_tool(usuario, tool_name, args).
  4. execute_tool valida RBAC, inyecta zona, llama a dal, devuelve resultado.
"""

from .. import dal, rbac


# ============================================================================
# SCHEMAS JSON (Etapa 2: definición de tools disponibles)
# ============================================================================

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "consultar_deuda",
            "description": (
                "Devuelve el saldo y la deuda total de UN cliente por su id interno. "
                "Usar cuando se pregunta cuánto debe un cliente puntual. No sirve para listar varios."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "cliente_id": {
                        "type": "integer",
                        "description": "ID interno del cliente (nrocli). No inventar; identificarlo antes."
                    }
                },
                "required": ["cliente_id"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "detalle_movimientos",
            "description": (
                "Devuelve el detalle de facturas, notas de crédito y recibos de UN cliente "
                "en los últimos N meses. Usar cuando piden 'el detalle' o 'los movimientos'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "cliente_id": {
                        "type": "integer",
                        "description": "ID interno del cliente."
                    },
                    "meses": {
                        "type": "integer",
                        "description": "Meses hacia atrás. Default 6.",
                        "default": 6
                    }
                },
                "required": ["cliente_id"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "clientes_por_zona",
            "description": (
                "Lista los clientes con deuda de la zona del usuario, ordenados por deuda. "
                "La zona la determina el sistema según el rol; el modelo no la pasa."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "solo_con_deuda": {
                        "type": "boolean",
                        "description": "Si true, solo los que deben. Default true.",
                        "default": True
                    }
                },
                "required": [],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consulta_custom",
            "description": (
                "Consulta genérica de reportes de UNA zona puntual (SOLO GERENTES). "
                "Permite obtener deuda total, top de morosos, o un resumen ejecutivo "
                "de esa zona. A diferencia de los otros tools, acá el gerente elige "
                "QUÉ zona consultar via 'nro_zona' (obligatorio) — no es la suya propia. "
                "No existe una opción 'todas las zonas a la vez'; si preguntan por el "
                "consolidado total, pedir que aclaren una zona o consultar de a una."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "intent": {
                        "type": "string",
                        "enum": ["deuda_por_zona", "top_morosos", "resumen_zonas"],
                        "description": (
                            "Tipo de reporte: "
                            "'deuda_por_zona' = deuda total de la zona, "
                            "'top_morosos' = ranking de clientes con más deuda en la zona, "
                            "'resumen_zonas' = resumen ejecutivo de la zona (totales, promedios, mora promedio)"
                        )
                    },
                    "filtros": {
                        "type": "object",
                        "description": "Filtros para acotar el reporte. 'nro_zona' es OBLIGATORIO.",
                        "properties": {
                            "nro_zona": {
                                "type": "integer",
                                "description": "Zona a consultar. OBLIGATORIO — no se puede omitir."
                            },
                            "top_n": {
                                "type": "integer",
                                "description": "Solo para intent='top_morosos': cuántos clientes devolver. Default 10.",
                                "default": 10
                            }
                        },
                        "required": ["nro_zona"]
                    }
                },
                "required": ["intent"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_cliente_por_nombre",
            "description": (
                "Busca clientes por nombre aproximado (texto parcial) dentro de la zona "
                "del usuario. Usar cuando el usuario menciona un cliente por NOMBRE en vez "
                "de por ID numérico. Devuelve una lista de candidatos (cliente_id + nombre); "
                "si hay un solo resultado, usar ese cliente_id con el tool correspondiente "
                "(consultar_deuda, detalle_movimientos, etc). Si hay varios, pedir que el "
                "usuario aclare cuál."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre_parcial": {
                        "type": "string",
                        "description": "Texto parcial del nombre del cliente a buscar."
                    }
                },
                "required": ["nombre_parcial"],
                "additionalProperties": False
            }
        }
    }
]


# ============================================================================
# EJECUTORES: Validación RBAC + inyección de zona + llamada a DAL
# ============================================================================

def _execute_consultar_deuda(usuario: str, cliente_id: int) -> dict:
    """
    Ejecuta 'consultar_deuda' con seguridad RBAC + inyección de zona.

    Args:
        usuario: identificador del usuario (vendedor1, gerente1, etc).
        cliente_id: ID interno del cliente (nrocli).

    Returns:
        dict con los campos: cliente_id, cliente, saldo, deuda_total, dias_mora_max, nota.
        Si el cliente no existe o no pertenece a la zona del usuario, devuelve None.

    Raises:
        PermissionError: si el usuario no tiene permiso para usar este tool.

    Flujo:
      1. Valida RBAC: can_use_tool(usuario, "consultar_deuda").
      2. Inyecta zona: zona_default(usuario) -> nrorep.
      3. Llama a dal.consultar_deuda(nrorep, cliente_id).
      4. Devuelve el resultado (o None si no existe/no pertenece a la zona).
    """
    perms = rbac.YamlPermissionProvider()

    if not perms.can_use_tool(usuario, "consultar_deuda"):
        raise PermissionError(f"Usuario '{usuario}' no tiene permiso para 'consultar_deuda'")

    nrorep = perms.zona_default(usuario)
    if nrorep is None:
        raise ValueError(
            f"Usuario '{usuario}' no tiene zona asignada (rol gerente debe especificar zona)"
        )

    return dal.consultar_deuda(nrorep, cliente_id)


def _execute_detalle_movimientos(usuario: str, cliente_id: int, meses: int = 6) -> list[dict]:
    """
    Ejecuta 'detalle_movimientos' con seguridad RBAC + inyección de zona.

    Args:
        usuario: identificador del usuario.
        cliente_id: ID interno del cliente.
        meses: meses hacia atrás (default 6).

    Returns:
        Lista de dicts con el detalle de movimientos (facturas, NC, recibos).
        Si el cliente no existe o no pertenece a la zona, devuelve [].

    Raises:
        PermissionError: si el usuario no tiene permiso.
    """
    perms = rbac.YamlPermissionProvider()

    if not perms.can_use_tool(usuario, "detalle_movimientos"):
        raise PermissionError(f"Usuario '{usuario}' no tiene permiso para 'detalle_movimientos'")

    nrorep = perms.zona_default(usuario)
    if nrorep is None:
        raise ValueError(
            f"Usuario '{usuario}' no tiene zona asignada"
        )

    return dal.detalle_movimientos(nrorep, cliente_id, meses)


def _execute_clientes_por_zona(usuario: str, solo_con_deuda: bool = True) -> list[dict]:
    """
    Ejecuta 'clientes_por_zona' con seguridad RBAC + inyección de zona.

    Args:
        usuario: identificador del usuario.
        solo_con_deuda: si True, solo clientes con deuda; si False, todos.

    Returns:
        Lista de dicts con los clientes de la zona del usuario, ordenados por deuda.

    Raises:
        PermissionError: si el usuario no tiene permiso.
        ValueError: si el usuario es gerente (zona "*") y debe especificar zona en consultas consolidadas.
    """
    perms = rbac.YamlPermissionProvider()

    if not perms.can_use_tool(usuario, "clientes_por_zona"):
        raise PermissionError(f"Usuario '{usuario}' no tiene permiso para 'clientes_por_zona'")

    nrorep = perms.zona_default(usuario)
    if nrorep is None:
        raise ValueError(
            f"Usuario '{usuario}' es gerente (zona '*'). "
            "Esta operación requiere especificar zona (implementar en Etapa 4)"
        )

    return dal.clientes_por_zona(nrorep, solo_con_deuda)


def _execute_consulta_custom(usuario: str, intent: str, filtros: dict | None = None) -> dict | list[dict]:
    """
    Ejecuta 'consulta_custom' (reportes consolidados, SOLO GERENTES).

    Args:
        usuario: identificador del usuario.
        intent: tipo de reporte ('deuda_por_zona', 'top_morosos', 'resumen_zonas').
        filtros: dict con 'nro_zona' (obligatorio) y, según el intent, 'top_n'.

    Returns:
        Resultado del reporte (list[dict]).

    Raises:
        PermissionError: si el usuario no es gerente o no tiene permiso.
        ValueError: si intent no es válido, o si falta 'nro_zona' en filtros.
        Exception: errores de conexión a BD.

    Nota: el gerente elige la zona explícitamente (no se inyecta desde su rol,
    porque su rol es "*" = todas). No existe modo "todas las zonas a la vez"
    (no escala recorrer la tabla completa de clientes vía el obrero legacy).
    """
    perms = rbac.YamlPermissionProvider()

    if not perms.can_use_tool(usuario, "consulta_custom"):
        raise PermissionError(
            f"Usuario '{usuario}' no tiene permiso para 'consulta_custom' "
            "(solo gerentes)"
        )

    # Validar intent
    valid_intents = ["deuda_por_zona", "top_morosos", "resumen_zonas"]
    if intent not in valid_intents:
        raise ValueError(
            f"Intent inválido: '{intent}'. Debe ser uno de {valid_intents}"
        )

    if filtros is None:
        filtros = {}

    # Despachar según intent a SP específicos
    if intent == "deuda_por_zona":
        return dal.deuda_por_zona(filtros)
    elif intent == "top_morosos":
        return dal.top_morosos(filtros)
    elif intent == "resumen_zonas":
        return dal.resumen_zonas(filtros)

    raise ValueError(f"Intent desconocido: '{intent}'")


def _execute_buscar_cliente_por_nombre(usuario: str, nombre_parcial: str) -> list[dict]:
    """
    Ejecuta 'buscar_cliente_por_nombre' con seguridad RBAC + inyección de zona.

    Args:
        usuario: identificador del usuario.
        nombre_parcial: texto parcial del nombre del cliente a buscar.

    Returns:
        Lista de candidatos: cliente_id, cliente, nro_zona.
        Para gerentes (zona "*"), busca en todas las zonas.
        Para vendedores, restringido a su zona (igual que el resto de los tools).

    Raises:
        PermissionError: si el usuario no tiene permiso para 'buscar_cliente_por_nombre'.
    """
    perms = rbac.YamlPermissionProvider()

    if not perms.can_use_tool(usuario, "buscar_cliente_por_nombre"):
        raise PermissionError(f"Usuario '{usuario}' no tiene permiso para 'buscar_cliente_por_nombre'")

    nrorep = perms.zona_default(usuario)  # None = gerente -> busca en todas las zonas
    return dal.buscar_cliente(nrorep, nombre_parcial)


# ============================================================================
# REGISTRY: Interfaz pública para el orquestador
# ============================================================================

def get_tools_for_user(usuario: str) -> list[dict]:
    """
    Devuelve los schemas JSON de los tools disponibles para un usuario.

    Validación: solo devuelve los tools para los que el usuario tiene permiso RBAC.

    Args:
        usuario: identificador del usuario.

    Returns:
        Lista de dicts con los schemas en formato Ollama (type: "function").
        Formato para Ollama:
        [
            {
                "type": "function",
                "function": {
                    "name": "consultar_deuda",
                    "description": "...",
                    "parameters": {...}
                }
            },
            ...
        ]

    Nota (Etapa 4):
      - Orden: consultar_deuda (0), detalle_movimientos (1), clientes_por_zona (2), consulta_custom (3).
      - Todos los usuarios: 3 tools básicos.
      - Gerentes: +1 tool adicional (consulta_custom) para reportes consolidados.
    """
    perms = rbac.YamlPermissionProvider()

    # Mapeo de tool_name -> posición en TOOL_SCHEMAS
    tool_name_to_index = {
        "consultar_deuda": 0,
        "detalle_movimientos": 1,
        "clientes_por_zona": 2,
        "consulta_custom": 3,
        "buscar_cliente_por_nombre": 4
    }

    disponibles = []
    for tool_name, idx in tool_name_to_index.items():
        if perms.can_use_tool(usuario, tool_name):
            disponibles.append(TOOL_SCHEMAS[idx])

    return disponibles


def execute_tool(usuario: str, tool_name: str, arguments: dict) -> dict | list[dict]:
    """
    Ejecuta un tool validando RBAC e inyectando zona.

    Punto de entrada único para el orquestador (Etapa 4).

    Args:
        usuario: identificador del usuario.
        tool_name: nombre del tool (p.ej. 'consultar_deuda', 'consulta_custom').
        arguments: dict con los argumentos (cliente_id, meses, intent, filtros, etc).

    Returns:
        Resultado del tool (dict o list[dict], dependiendo del tool).

    Raises:
        ValueError: si el tool no existe.
        PermissionError: si el usuario no tiene permiso.
        Exception: otros errores de ejecución (p.ej. conexión a BD).

    Flujo (Etapa 4):
      1. Valida que el tool exista.
      2. Despacha al ejecutor (_execute_*).
      3. El ejecutor valida RBAC + inyecta zona (si aplica) + llama a dal.
      4. Devuelve el resultado.

    Tools disponibles:
      - consultar_deuda: query de deuda de UN cliente.
      - detalle_movimientos: movimientos de UN cliente.
      - clientes_por_zona: lista de clientes de la zona del usuario.
      - consulta_custom: reportes consolidados (SOLO gerentes).
    """
    if tool_name == "consultar_deuda":
        return _execute_consultar_deuda(
            usuario,
            cliente_id=arguments["cliente_id"]
        )

    elif tool_name == "detalle_movimientos":
        return _execute_detalle_movimientos(
            usuario,
            cliente_id=arguments["cliente_id"],
            meses=arguments.get("meses", 6)
        )

    elif tool_name == "clientes_por_zona":
        return _execute_clientes_por_zona(
            usuario,
            solo_con_deuda=arguments.get("solo_con_deuda", True)
        )

    elif tool_name == "consulta_custom":
        return _execute_consulta_custom(
            usuario,
            intent=arguments["intent"],
            filtros=arguments.get("filtros", {})
        )

    elif tool_name == "buscar_cliente_por_nombre":
        return _execute_buscar_cliente_por_nombre(
            usuario,
            nombre_parcial=arguments["nombre_parcial"]
        )

    else:
        raise ValueError(f"Tool desconocido: '{tool_name}'")
