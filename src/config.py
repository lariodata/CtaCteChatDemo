"""Configuración central. Lee variables de entorno (.env)."""
import os
from dotenv import load_dotenv

load_dotenv()

# --- Conexión SQL Server 2012 (ODBC Driver 17) ---
SQL_DRIVER = os.getenv("SQL_DRIVER", "ODBC Driver 17 for SQL Server")
SQL_SERVER = os.getenv("SQL_SERVER", "lariosql70")
SQL_DATABASE = os.getenv("SQL_DATABASE", "DATOS_COBRANZAS")
SQL_USER = os.getenv("SQL_USER", "chat_app")
SQL_PASSWORD = os.getenv("SQL_PASSWORD", "")

# --- Proveedor LLM: "ollama" | "claude_haiku" (seleccionable desde la UI) ---
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")  # 14b = modo calidad

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5")

CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))


def odbc_connection_string() -> str:
    return (
        f"DRIVER={{{SQL_DRIVER}}};SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DATABASE};UID={SQL_USER};PWD={SQL_PASSWORD};"
        f"TrustServerCertificate=yes;"
    )
