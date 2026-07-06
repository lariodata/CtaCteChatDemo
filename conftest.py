"""
Configuración global para pytest.

Asegura que:
  1. El path incluya la raíz del proyecto (para importar 'src').
  2. Las variables de entorno estén correctas.
"""

import sys
from pathlib import Path

# Agregar raíz al path para que pytest pueda importar 'src'
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Cargar .env si existe
try:
    from dotenv import load_dotenv
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass
