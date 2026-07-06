"""
Tests para src/dal.py CON MOCKS (sin BD real).

Usa unittest.mock para simular respuestas de SQL Server.
Valida que:
  - DAL arma las queries correctamente
  - DAL convierte resultados correctamente
  - DAL maneja errores (sin BD)
"""

import pytest
from unittest.mock import patch, MagicMock
from src import dal


@patch('src.dal.pyodbc.connect')
def test_consultar_deuda_success(mock_connect):
    """Valida que consultar_deuda devuelve resultado correcto."""
    # Simula cursor + resultado de BD
    mock_cursor = MagicMock()
    mock_cursor.description = [
        ('cliente_id',),
        ('cliente',),
        ('saldo',),
        ('deuda_total',),
        ('dias_mora_max',)
    ]
    mock_cursor.fetchall.return_value = [
        (3523, 'PINTO HERMANOS S.A.', 0, 4730599.72, 45)
    ]

    mock_connect.return_value.__enter__.return_value.cursor.return_value = mock_cursor

    # Ejecuta
    resultado = dal.consultar_deuda(nrorep=1, nrocli=3523)

    # Valida
    assert resultado is not None
    assert resultado['cliente_id'] == 3523
    assert resultado['cliente'] == 'PINTO HERMANOS S.A.'
    assert float(resultado['deuda_total']) == 4730599.72
    print(f"✓ Consultar deuda mock: {resultado}")


@patch('src.dal.pyodbc.connect')
def test_consultar_deuda_not_found(mock_connect):
    """Valida que devuelve None si cliente no existe."""
    mock_cursor = MagicMock()
    mock_cursor.description = [('cliente_id',), ('deuda_total',)]
    mock_cursor.fetchall.return_value = []  # Sin resultados

    mock_connect.return_value.__enter__.return_value.cursor.return_value = mock_cursor

    resultado = dal.consultar_deuda(nrorep=1, nrocli=99999)

    assert resultado is None
    print("✓ Consultar deuda not found: retorna None")


@patch('src.dal.pyodbc.connect')
def test_clientes_por_zona_success(mock_connect):
    """Valida que clientes_por_zona devuelve lista correcta."""
    mock_cursor = MagicMock()
    mock_cursor.description = [
        ('cliente_id',),
        ('cliente',),
        ('deuda_total',)
    ]
    mock_cursor.fetchall.return_value = [
        (3523, 'PINTO HERMANOS', 4730599.72),
        (100, 'ACME INC', 500000.00)
    ]

    mock_connect.return_value.__enter__.return_value.cursor.return_value = mock_cursor

    resultado = dal.clientes_por_zona(nrorep=1, solo_con_deuda=True)

    assert isinstance(resultado, list)
    assert len(resultado) == 2
    assert resultado[0]['cliente'] == 'PINTO HERMANOS'
    print(f"✓ Clientes por zona mock: {len(resultado)} clientes")


@patch('src.dal.pyodbc.connect')
def test_clientes_por_zona_empty(mock_connect):
    """Valida que devuelve lista vacía si no hay clientes."""
    mock_cursor = MagicMock()
    mock_cursor.description = [('cliente_id',), ('cliente',)]
    mock_cursor.fetchall.return_value = []

    mock_connect.return_value.__enter__.return_value.cursor.return_value = mock_cursor

    resultado = dal.clientes_por_zona(nrorep=1, solo_con_deuda=True)

    assert isinstance(resultado, list)
    assert len(resultado) == 0
    print("✓ Clientes por zona vacío: retorna []")


@patch('src.dal.pyodbc.connect')
def test_detalle_movimientos_success(mock_connect):
    """Valida que detalle_movimientos devuelve movimientos correctos."""
    mock_cursor = MagicMock()
    mock_cursor.description = [
        ('fecha',),
        ('tipo_comprobante',),
        ('numero',),
        ('debe',),
        ('haber',),
        ('saldo',),
        ('dias_mora',)
    ]
    mock_cursor.fetchall.return_value = [
        ('2026-06-04', 'FA', '801-779', 483577.65, 0, 483577.65, 26),
        ('2026-06-10', 'RC', '001-001', 0, 100000, 383577.65, 20)
    ]

    mock_connect.return_value.__enter__.return_value.cursor.return_value = mock_cursor

    resultado = dal.detalle_movimientos(nrorep=1, nrocli=3523, meses=6)

    assert isinstance(resultado, list)
    assert len(resultado) == 2
    assert resultado[0]['tipo_comprobante'] == 'FA'
    print(f"✓ Detalle movimientos mock: {len(resultado)} movimientos")


@patch('src.dal.pyodbc.connect')
def test_deuda_por_zona_success(mock_connect):
    """Valida que deuda_por_zona devuelve resumen correcto."""
    mock_cursor = MagicMock()
    mock_cursor.description = [
        ('nro_zona',),
        ('clientes_totales',),
        ('clientes_con_deuda',),
        ('deuda_total',),
        ('deuda_promedio',)
    ]
    mock_cursor.fetchall.return_value = [
        (1, 100, 45, 12075391.02, 268341.80)
    ]

    mock_connect.return_value.__enter__.return_value.cursor.return_value = mock_cursor

    resultado = dal.deuda_por_zona(filtros={'nro_zona': 1})

    assert isinstance(resultado, list)
    assert len(resultado) == 1
    assert resultado[0]['nro_zona'] == 1
    assert resultado[0]['clientes_totales'] == 100
    print(f"✓ Deuda por zona mock: {resultado[0]}")


@patch('src.dal.pyodbc.connect')
def test_top_morosos_success(mock_connect):
    """Valida que top_morosos devuelve ranking correcto."""
    mock_cursor = MagicMock()
    mock_cursor.description = [
        ('cliente_id',),
        ('cliente',),
        ('deuda_total',)
    ]
    mock_cursor.fetchall.return_value = [
        (1000, 'SUPERMERCADOS PETRELLI', 4171930.95),
        (2000, 'BALEAR S.A.', 3696479.54),
        (3523, 'PINTO HERMANOS', 3530557.32)
    ]

    mock_connect.return_value.__enter__.return_value.cursor.return_value = mock_cursor

    resultado = dal.top_morosos(filtros={'nro_zona': 1, 'top_n': 3})

    assert isinstance(resultado, list)
    assert len(resultado) == 3
    assert resultado[0]['cliente'] == 'SUPERMERCADOS PETRELLI'
    print(f"✓ Top morosos mock: {len(resultado)} clientes")


def test_require_nro_zona_validates():
    """Valida que _require_nro_zona rechaza filtros sin nro_zona."""
    with pytest.raises(ValueError, match="nro_zona"):
        dal._require_nro_zona({})


def test_require_nro_zona_accepts():
    """Valida que _require_nro_zona acepta nro_zona válido."""
    nro = dal._require_nro_zona({'nro_zona': 1})
    assert nro == 1
    print("✓ _require_nro_zona validación OK")


@patch('src.dal.pyodbc.connect')
def test_resumen_zonas_success(mock_connect):
    """Valida que resumen_zonas devuelve resumen ejecutivo."""
    mock_cursor = MagicMock()
    mock_cursor.description = [
        ('nro_zona',),
        ('clientes_totales',),
        ('clientes_con_deuda',),
        ('deuda_total',),
        ('deuda_promedio',),
        ('dias_mora_promedio',)
    ]
    mock_cursor.fetchall.return_value = [
        (1, 100, 45, 12075391.02, 268341.80, 35.5)
    ]

    mock_connect.return_value.__enter__.return_value.cursor.return_value = mock_cursor

    resultado = dal.resumen_zonas(filtros={'nro_zona': 1})

    assert isinstance(resultado, list)
    assert len(resultado) == 1
    assert resultado[0]['dias_mora_promedio'] == 35.5
    print(f"✓ Resumen zonas mock: {resultado[0]}")
