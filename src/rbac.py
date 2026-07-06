"""
RBAC liviano y PLUGGABLE.
Hoy lee config/roles.yaml. Mañana se implementa SqlPermissionProvider con la
MISMA interfaz (get_zonas / can_use_tool) y se cambia sin tocar el resto.
"""
from pathlib import Path
import yaml

_ROLES_PATH = Path(__file__).resolve().parent.parent / "config" / "roles.yaml"


class PermissionProvider:
    """Interfaz. Cualquier backend (YAML, tabla SQL, LDAP) la implementa."""
    def get_rol(self, usuario: str) -> str | None: ...
    def get_zonas(self, usuario: str): ...
    def can_use_tool(self, usuario: str, tool: str) -> bool: ...


class YamlPermissionProvider(PermissionProvider):
    def __init__(self, path: Path = _ROLES_PATH):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        self._usuarios = data["usuarios"]
        self._permisos = data["permisos"]

    def get_rol(self, usuario: str) -> str | None:
        u = self._usuarios.get(usuario)
        return u["rol"] if u else None

    def get_zonas(self, usuario: str):
        u = self._usuarios.get(usuario)
        if not u:
            return []
        z = u["zonas"]
        return "*" if z == "*" else list(z)

    def can_use_tool(self, usuario: str, tool: str) -> bool:
        rol = self.get_rol(usuario)
        return bool(rol) and tool in self._permisos.get(rol, [])

    def zona_default(self, usuario: str) -> int | None:
        """Zona que se inyecta como @nrorep para un vendedor (la primera)."""
        z = self.get_zonas(usuario)
        if z == "*":
            return None  # gerente: debe especificar zona en consultas consolidadas
        return z[0] if z else None

    def user_exists(self, usuario: str) -> bool:
        """Valida que un usuario exista en RBAC."""
        return usuario in self._usuarios

    def list_users(self) -> list[str]:
        """Devuelve la lista de usuarios válidos."""
        return list(self._usuarios.keys())
