"""
Capa de acceso a datos (DAL).
REGLA DE ORO: esta capa SOLO ejecuta los SP chat_* con parámetros.
Nunca arma SQL a partir de texto del modelo. Sin SQL libre = sin inyección.
"""
import pyodbc
from . import config


def _connect():
    return pyodbc.connect(config.odbc_connection_string())


def _rows_to_dicts(cursor):
    cols = [c[0] for c in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


def consultar_deuda(nrorep: int, nrocli: int) -> dict | None:
    with _connect() as cn:
        cur = cn.cursor()
        print(f"🔍 [DAL] Consultando deuda: nrorep={nrorep}, nrocli={nrocli}")  # DEBUG
        cur.execute(
            "EXEC dbo.chat_consultar_deuda @nrorep = ?, @nrocli = ?",
            nrorep, nrocli,
        )
        rows = _rows_to_dicts(cur)
        result = rows[0] if rows else None
        print(f"   Resultado: {result}")  # DEBUG
        return result


def clientes_por_zona(nrorep: int, solo_con_deuda: bool = True) -> list[dict]:
    with _connect() as cn:
        cur = cn.cursor()
        cur.execute(
            "EXEC dbo.chat_clientes_por_zona @nrorep = ?, @solo_con_deuda = ?",
            nrorep, 1 if solo_con_deuda else 0,
        )
        return _rows_to_dicts(cur)


def detalle_movimientos(nrorep: int, nrocli: int, meses: int = 6) -> list[dict]:
    with _connect() as cn:
        cur = cn.cursor()
        cur.execute(
            "EXEC dbo.chat_detalle_movimientos @nrorep = ?, @nrocli = ?, @meses = ?",
            nrorep, nrocli, meses,
        )
        return _rows_to_dicts(cur)


# ============================================================================
# Reportes consolidados (Etapa 4): solo gerentes
# ============================================================================

def _require_nro_zona(filtros: dict) -> int:
    """
    Los reportes consolidados (Etapa 4) solo aceptan UNA zona puntual.
    "Todas las zonas" no escala: recorrer toda CLIENTAS (millones de filas)
    vía el obrero legacy por cliente no termina en tiempo razonable.
    """
    nro_zona = filtros.get("nro_zona")
    if nro_zona is None:
        raise ValueError(
            "Este reporte requiere especificar 'nro_zona' (no se admite 'todas las zonas')."
        )
    return nro_zona


def deuda_por_zona(filtros: dict) -> list[dict]:
    """
    Devuelve deuda total de UNA zona puntual.

    Args:
        filtros: dict con 'nro_zona' (int, obligatorio).

    Returns:
        list[dict] con una fila: nro_zona, clientes_totales,
        clientes_con_deuda, deuda_total, deuda_promedio.
    """
    nro_zona = _require_nro_zona(filtros)
    with _connect() as cn:
        cur = cn.cursor()
        cur.execute(
            "EXEC dbo.chat_deuda_por_zona @nro_zona = ?",
            nro_zona,
        )
        return _rows_to_dicts(cur)


def top_morosos(filtros: dict) -> list[dict]:
    """
    Devuelve el top N de clientes con más deuda de UNA zona puntual.

    Args:
        filtros: dict con 'nro_zona' (int, obligatorio) y 'top_n' (int, default 10).

    Returns:
        list[dict] con: cliente_id, cliente, nro_zona, deuda_total, dias_mora_max.
    """
    nro_zona = _require_nro_zona(filtros)
    top_n = filtros.get("top_n", 10)
    with _connect() as cn:
        cur = cn.cursor()
        cur.execute(
            "EXEC dbo.chat_top_morosos @nro_zona = ?, @top_n = ?",
            nro_zona, top_n,
        )
        return _rows_to_dicts(cur)


def resumen_zonas(filtros: dict) -> list[dict]:
    """
    Devuelve resumen ejecutivo de UNA zona puntual (totales, promedios, mora promedio).

    Args:
        filtros: dict con 'nro_zona' (int, obligatorio).

    Returns:
        list[dict] con una fila: nro_zona, clientes_totales, clientes_con_deuda,
        deuda_total, deuda_promedio, dias_mora_promedio.
    """
    nro_zona = _require_nro_zona(filtros)
    with _connect() as cn:
        cur = cn.cursor()
        cur.execute(
            "EXEC dbo.chat_resumen_zonas @nro_zona = ?",
            nro_zona,
        )
        return _rows_to_dicts(cur)


def buscar_cliente(nrorep: int | None, nombre: str) -> list[dict]:
    """
    Busca clientes por nombre aproximado (LIKE). Devuelve candidatos (id + nombre + zona)
    para resolver el ID antes de llamar a consultar_deuda/detalle_movimientos.

    Args:
        nrorep: zona a la que restringir la búsqueda. None = todas las zonas
            (solo gerentes; un vendedor siempre debe pasar su zona).
        nombre: texto parcial del nombre del cliente.

    Returns:
        list[dict] con: cliente_id, cliente, nro_zona (hasta 20 resultados).
    """
    with _connect() as cn:
        cur = cn.cursor()
        cur.execute(
            "EXEC dbo.chat_buscar_cliente @nrorep = ?, @nombre = ?",
            nrorep, nombre,
        )
        return _rows_to_dicts(cur)
