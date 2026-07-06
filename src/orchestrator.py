"""
Orquestador simple (Etapa 3): Loop LLM → tool-calling → resultado.

Responsabilidad:
  1. Recibir mensaje del usuario + usuario/rol.
  2. Obtener tools disponibles del registry (tools/__init__.py).
  3. Llamar a Ollama con el mensaje + schemas de tools.
  4. Si Ollama hace tool_calls, ejecutar cada tool.
  5. Enviar resultados de tools de vuelta a Ollama.
  6. Repetir hasta que Ollama devuelva contenido final (sin tool_calls).
  7. Devolver respuesta al usuario.

Seguridad:
  - Los tools se obtienen de registry.get_tools_for_user(usuario).
  - Los arguments de tool_calls se validan contra el schema.
  - Cada ejecución de tool valida RBAC + inyecta zona.

Nota (Etapa 4): se agregará cache y tool genérica 'consulta_custom' aquí.
"""

import json
import logging
from typing import Generator
from . import config, tools as tools_registry, rbac
from .cache import _cache
from .llm import get_provider
from .llm.base import LLMProvider

logger = logging.getLogger(__name__)


def chat(
    usuario: str,
    mensaje: str,
    llm_provider: LLMProvider | None = None,
    provider: str | None = None,
    max_iterations: int = 3
) -> str:
    """
    Chat interactivo con tool-calling end-to-end (Etapa 4: +cache).

    Flujo:
      1. Obtiene tools disponibles para el usuario.
      2. Llama LLM con [mensaje] + [tools].
      3. Si LLM hace tool_calls, ejecuta cada uno (con cache).
      4. Envía resultados de vuelta a LLM como "tool" messages.
      5. Repite hasta que LLM devuelve contenido final (sin tool_calls).
      6. Devuelve la respuesta de texto.

    Etapa 4 refinamientos:
      - max_iterations: 10 → 3 (más conservador).
      - Cache: cada tool_call se cachea con TTL (default 300s).
      - Error handling: mejor logging de errores.

    Args:
        usuario: identificador del usuario (vendedor1, gerente1, etc).
        mensaje: pregunta/comando del usuario.
        llm_provider: instancia de LLMProvider ya creada (tiene prioridad sobre `provider`).
        provider: nombre del provider a usar ("ollama" | "claude_haiku"). Si no se pasa
            ni `llm_provider` ni `provider`, usa config.LLM_PROVIDER (default "ollama").
        max_iterations: límite de vueltas LLM→tool→LLM (default 3).

    Returns:
        str: respuesta final del LLM.

    Raises:
        PermissionError: si el usuario no tiene permisos.
        ValueError: si hay error de validación.
        Exception: si falla la conexión a Ollama o BD.

    Ejemplo:
      >>> respuesta = chat(
      ...     usuario="vendedor1",
      ...     mensaje="¿Cuánto debe el cliente 3523?"
      ... )
      >>> print(respuesta)
      "PINTO HERMANOS S.A. debe $4.730.599,72"
    """
    if llm_provider is None:
        llm_provider = get_provider(provider)

    # Paso 1: Obtener tools disponibles para este usuario
    try:
        tools_disponibles = tools_registry.get_tools_for_user(usuario)
        if not tools_disponibles:
            raise PermissionError(f"Usuario '{usuario}' no tiene acceso a ningún tool")
    except Exception as e:
        print(f"✗ Error al obtener tools: {str(e)}")
        raise

    # Paso 1.5: Crear system prompt mejorado con contexto del usuario
    perms = rbac.YamlPermissionProvider()
    rol = perms.get_rol(usuario)
    zonas = perms.get_zonas(usuario)
    tool_names = [t["function"]["name"] for t in tools_disponibles]

    logger.info(f"Usuario: {usuario}, Rol: {rol}, Zonas: {zonas}")

    if isinstance(zonas, list):
        zonas_str = ", ".join(str(z) for z in zonas)
    else:
        zonas_str = str(zonas)

    system_prompt = f"""Eres un asistente especializado en consultas de cuentas corrientes y cobranzas.
⚠️  RESTRICCIÓN CRÍTICA: Debes OBEDECER SIEMPRE las zonas asignadas al usuario.

CONTEXTO DEL USUARIO:
- Usuario: {usuario}
- Rol: {rol}
- Zonas PERMITIDAS: {zonas_str} (SOLO ESTAS)
- Tools disponibles: {', '.join(tool_names)}

REGLA DE SEGURIDAD #1 - INYECCIÓN DE ZONA:
El usuario SOLO puede ver información de zona(s): {zonas_str}
Si pregunta por otra zona, RECHAZA INMEDIATAMENTE.
NO ejecutes búsquedas de clientes/deudas fuera de {zonas_str}

REGLA DE SEGURIDAD #2 - VENDEDORES VS GERENTES:
- Si rol = "vendedor": SOLO consulta zona(s) {zonas_str}. Rechaza cualquier pregunta sobre otra zona.
- Si rol = "gerente": Puedes ver todas las zonas pero el usuario DEBE especificar zona para cada reporte.

INSTRUCCIONES:
1. "Mi zona" = zona(s) {zonas_str}
2. Si vendedor pregunta "¿deuda zona X?" donde X != {zonas_str}: "No puedo. Solo tengo acceso a zona(s) {zonas_str}"
3. Si no tienes datos: "No tengo información para eso" (NO inventar)
4. Respuestas concisas: máximo 3 párrafos
5. Incluye: cliente, deuda, mora en días, datos relevantes

GUÍA DE TOOLS (ELIGE EL CORRECTO):
1. "¿Cuánto debe cliente X?" o "deuda cliente X" → USO: consultar_deuda
2. "movimientos cliente X" o "detalle cliente X" → USO: detalle_movimientos
3. "clientes con deuda" o "listar clientes" → USO: clientes_por_zona
4. "deuda zona X" o "consolidado zona X" → USO: consulta_custom (solo gerentes)
5. Si te dan un NOMBRE en vez de un ID de cliente → USO: buscar_cliente_por_nombre primero

RESOLUCIÓN DE NOMBRE A ID (si buscar_cliente_por_nombre está disponible):
- Si el usuario menciona un cliente por NOMBRE (no por ID numérico), llamá primero a
  buscar_cliente_por_nombre con ese texto.
- Si devuelve UN solo resultado, segui automáticamente con el tool que corresponda
  (consultar_deuda, detalle_movimientos, etc.) usando ese cliente_id, sin volver a preguntar.
- Si devuelve VARIOS resultados, listalos (nombre + cliente_id) y pedile al usuario que
  aclare cuál, antes de continuar.
- Si no devuelve resultados: "No encontré ningún cliente con ese nombre en tu zona".

EJEMPLOS CRÍTICOS:
- Pregunta: "cliente 28882 zona 2?" → TOOL: consultar_deuda (cliente ESPECÍFICO)
- Pregunta: "clientes zona 1?" → TOOL: clientes_por_zona (lista de clientes)
- Pregunta: "deuda total zona 1?" → TOOL: consulta_custom (consolidado, solo gerentes)
- Pregunta: "¿cuánto debe Pinto Hermanos?" → TOOL: buscar_cliente_por_nombre, luego consultar_deuda con el ID resuelto
- Vendedor zona 1 pregunta "zona 2": ❌ "No puedo. Solo veo zona 1"
"""

    # Paso 2: Inicializar historial de mensajes con system prompt
    logger.info(f"SYSTEM PROMPT:\n{system_prompt}\n")  # DEBUG: Ver el prompt completo
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": mensaje}
    ]

    # Paso 3: Loop LLM → tool → LLM
    for iteracion in range(max_iterations):
        print(f"\n[Iteración {iteracion + 1}/{max_iterations}]")

        try:
            # Llamar LLM con tools
            response = llm_provider.chat(
                messages=messages,
                tools=tools_disponibles
            )
        except Exception as e:
            print(f"✗ Error en llamada a LLM: {str(e)}")
            raise

        # Si hay contenido final, devolver
        if response.get("content") and not response.get("tool_calls"):
            print(f"✓ Respuesta final obtenida")
            return response["content"]

        # Si hay tool_calls, ejecutar cada uno
        if response.get("tool_calls"):
            # Agregar respuesta del LLM al historial
            messages.append({
                "role": "assistant",
                "content": response.get("content", ""),
                "tool_calls": response["tool_calls"]
            })

            # Ejecutar tools y agregar resultados
            tool_results = []
            for tool_call in response["tool_calls"]:
                tool_name = tool_call["name"]
                arguments = tool_call["arguments"]

                try:
                    # Intentar obtener del cache primero
                    cached = _cache.get(usuario, tool_name, arguments)
                    if cached is not None:
                        resultado = cached
                        print(f"[CACHE HIT] Tool '{tool_name}'")
                    else:
                        # Ejecutar el tool (validación RBAC + inyección de zona dentro)
                        resultado = tools_registry.execute_tool(
                            usuario=usuario,
                            tool_name=tool_name,
                            arguments=arguments
                        )
                        # Cachear resultado
                        _cache.set(usuario, tool_name, arguments, resultado, config.CACHE_TTL_SECONDS)
                        print(f"[CACHE MISS] Tool '{tool_name}' ejecutado exitosamente")

                    # Normalizar resultado a JSON-serializable
                    resultado_str = json.dumps(resultado, default=str, ensure_ascii=False)

                    tool_results.append({
                        "type": "tool",
                        "tool_name": tool_name,
                        "content": resultado_str
                    })
                except (PermissionError, ValueError, Exception) as e:
                    # Si hay error, pasar al LLM para que lo maneje
                    error_msg = str(e)
                    print(f"✗ Error en tool '{tool_name}': {error_msg}")
                    tool_results.append({
                        "type": "tool",
                        "tool_name": tool_name,
                        "content": json.dumps({"error": error_msg}, ensure_ascii=False)
                    })

            # Agregar resultados de tools al historial
            for tool_result in tool_results:
                messages.append({
                    "role": "tool",
                    "tool_name": tool_result["tool_name"],
                    "content": tool_result["content"]
                })

            # Próxima iteración: LLM procesa los resultados
            continue

        # Si ni contenido ni tool_calls, algo raro pasó
        raise ValueError(
            f"Ollama devolvió respuesta inesperada (sin content ni tool_calls): {response}"
        )

    # Si llegamos aquí, excedimos max_iterations
    raise RuntimeError(
        f"Excedidas {max_iterations} iteraciones. Loop LLM→tool posiblemente infinito."
    )


def chat_stream(
    usuario: str,
    mensaje: str,
    llm_provider: LLMProvider | None = None,
    provider: str | None = None,
    max_iterations: int = 3
) -> Generator[str, None, None]:
    """
    Chat interactivo con streaming de eventos (para Etapa 5: API).

    Yielda eventos JSON-lines para que el cliente (UI web) los procese:
      - {"type": "thinking", "content": "..."}  (si el LLM piensa)
      - {"type": "tool_call", "tool": "...", "args": {...}}
      - {"type": "tool_result", "tool": "...", "result": {...}}
      - {"type": "response", "content": "..."}  (respuesta final)
      - {"type": "error", "message": "..."}

    Nota: Etapa 3 usa chat() (simple). Etapa 5 lo usará para streaming a la UI.

    Args:
        usuario, mensaje, llm_provider, max_iterations: igual que chat().

    Yields:
        str: líneas JSON con eventos.
    """
    # Etapa 3 no implementa streaming; usamos chat() internamente.
    # En Etapa 5, se reemplazará con streaming real.
    try:
        respuesta = chat(
            usuario=usuario,
            mensaje=mensaje,
            llm_provider=llm_provider,
            provider=provider,
            max_iterations=max_iterations
        )
        yield json.dumps({"type": "response", "content": respuesta}, ensure_ascii=False)
    except Exception as e:
        yield json.dumps({"type": "error", "message": str(e)}, ensure_ascii=False)
