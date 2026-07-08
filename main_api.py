"""
Punto de entrada para la API HTTP (Etapa 5).

Uso:
    python main_api.py                                  # Corre en http://localhost:8080
    uvicorn main_api:app --reload                       # Con hot-reload (desarrollo)
    uvicorn main_api:app --host 0.0.0.0 --port 8080   # Para acceso externo (producción)

Documentación interactiva:
    - Swagger UI: http://localhost:8080/docs
    - ReDoc: http://localhost:8080/redoc

Endpoints disponibles:
    - POST /chat          - Envía un mensaje, devuelve respuesta del LLM
    - GET /health         - Health check
    - GET /tools/{usuario} - Lista tools disponibles para un usuario
"""

import uvicorn
from src.api import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8080,
        log_level="info"
    )
