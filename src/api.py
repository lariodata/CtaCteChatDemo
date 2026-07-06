"""
FastAPI para Etapa 5: Chat HTTP endpoint.

Endpoints:
  POST /chat          - envía un mensaje, devuelve respuesta del LLM
  GET /health         - health check
  GET /tools/{usuario} - lista tools disponibles para un usuario

Requiere: FastAPI, uvicorn, pydantic
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
import logging

from . import orchestrator, tools, rbac
from .llm import PROVIDERS_VALIDOS

logger = logging.getLogger(__name__)
app = FastAPI(
    title="ctacte-chat-demo API",
    description="Chat con LLM sobre cuentas corrientes (RBAC, cache, tools)",
    version="1.0.0"
)


# ============================================================================
# MODELOS PYDANTIC
# ============================================================================

class ChatRequest(BaseModel):
    """Request body para POST /chat."""
    usuario: str = Field(
        ...,
        description="ID del usuario (ej. 'vendedor1', 'gerente1')",
        examples=["vendedor1", "gerente1"]
    )
    mensaje: str = Field(
        ...,
        description="Pregunta o comando del usuario",
        examples=["¿Cuánto debe el cliente 3523?", "Dame el top 3 morosos de zona 1"]
    )
    max_iterations: int = Field(
        3,
        ge=1,
        le=10,
        description="Máximo de iteraciones LLM→tool (default 3)"
    )
    provider: str | None = Field(
        None,
        description="Proveedor LLM a usar ('ollama' | 'claude_haiku'). Default: config.LLM_PROVIDER",
        examples=["ollama", "claude_haiku"]
    )


class ToolInfo(BaseModel):
    """Info de un tool disponible."""
    name: str
    description: str


class ChatResponse(BaseModel):
    """Response body para POST /chat."""
    respuesta: str = Field(
        ...,
        description="Respuesta final del LLM"
    )
    usuario: str = Field(
        ...,
        description="Usuario que hizo la consulta"
    )
    iterations_used: int = Field(
        ...,
        description="Cuántas iteraciones se usaron (debug)"
    )


class HealthResponse(BaseModel):
    """Response para GET /health."""
    status: str
    message: str


class ToolsListResponse(BaseModel):
    """Response para GET /tools/{usuario}."""
    usuario: str
    tools: list[ToolInfo]


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/health", response_model=HealthResponse, tags=["health"])
def health_check():
    """Health check simple."""
    return {
        "status": "ok",
        "message": "ctacte-chat-demo API está operativa"
    }


@app.get("/tools/{usuario}", response_model=ToolsListResponse, tags=["tools"])
def get_user_tools(usuario: str):
    """
    Devuelve los tools disponibles para un usuario.

    Útil para saber qué puede hacer cada usuario sin ejecutar un chat.
    """
    # Validar que el usuario exista ANTES del try-except
    perms = rbac.YamlPermissionProvider()
    if not perms.user_exists(usuario):
        raise HTTPException(
            status_code=400,
            detail=f"Usuario '{usuario}' no existe en RBAC"
        )

    try:
        # Obtener tools disponibles
        disponibles = tools.get_tools_for_user(usuario)

        # Mapear a respuesta legible
        tool_list = [
            ToolInfo(
                name=t["function"]["name"],
                description=t["function"]["description"]
            )
            for t in disponibles
        ]

        return {
            "usuario": usuario,
            "tools": tool_list
        }

    except Exception as e:
        logger.error(f"Error en GET /tools/{usuario}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse, tags=["chat"])
def chat_endpoint(request: ChatRequest):
    """
    Endpoint principal: envía un mensaje al chat, devuelve respuesta del LLM.

    Flujo:
      1. Valida que el usuario exista (RBAC).
      2. Llama al orquestador con el mensaje.
      3. Devuelve la respuesta con metadata.

    Errores:
      - 400: usuario inválido, formato incorrecto.
      - 500: error interno (BD, LLM, etc).
    """
    # Validar usuario ANTES del try-except principal
    perms = rbac.YamlPermissionProvider()
    if not perms.user_exists(request.usuario):
        raise HTTPException(
            status_code=400,
            detail=f"Usuario '{request.usuario}' no existe. Válidos: {perms.list_users()}"
        )

    if request.provider is not None and request.provider not in PROVIDERS_VALIDOS:
        raise HTTPException(
            status_code=400,
            detail=f"Provider '{request.provider}' inválido. Válidos: {PROVIDERS_VALIDOS}"
        )

    try:
        # Ejecutar chat
        logger.info(
            f"Chat request: usuario={request.usuario}, provider={request.provider}, "
            f"mensaje={request.mensaje[:50]}..."
        )
        respuesta = orchestrator.chat(
            usuario=request.usuario,
            mensaje=request.mensaje,
            provider=request.provider,
            max_iterations=request.max_iterations
        )

        logger.info(f"Chat response (OK): usuario={request.usuario}")

        return ChatResponse(
            respuesta=respuesta,
            usuario=request.usuario,
            iterations_used=request.max_iterations  # Aproximado; el orquestador podría trackear mejor
        )

    except PermissionError as e:
        logger.warning(f"Permission denied: {e}")
        raise HTTPException(status_code=403, detail=str(e))

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Unexpected error in /chat: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor. Contactar administrador."
        )


# ============================================================================
# SETUP LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
