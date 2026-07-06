"""
Tests para src/config.py

Valida que:
  - Connection string se arma bien
  - Tiene los componentes necesarios (Driver, SERVER, etc)
"""

from src import config


def test_odbc_connection_string_returns_string():
    """Valida que devuelve un string válido (no None, no vacío)."""
    conn_str = config.odbc_connection_string()
    assert isinstance(conn_str, str)
    assert len(conn_str) > 0
    print(f"✓ Connection string válido: {conn_str[:60]}...")


def test_odbc_connection_string_has_driver():
    """Valida que la connection string incluye Driver (ODBC)."""
    conn_str = config.odbc_connection_string()
    assert 'Driver' in conn_str
    assert 'ODBC Driver 17 for SQL Server' in conn_str
    print("✓ Connection string incluye Driver ODBC")


def test_odbc_connection_string_has_server():
    """Valida que la connection string incluye SERVER."""
    conn_str = config.odbc_connection_string()
    assert 'SERVER=' in conn_str or 'Server=' in conn_str
    print("✓ Connection string incluye SERVER")


def test_odbc_connection_string_has_database():
    """Valida que la connection string incluye DATABASE."""
    conn_str = config.odbc_connection_string()
    assert 'DATABASE=' in conn_str or 'Initial Catalog=' in conn_str
    print("✓ Connection string incluye DATABASE")


def test_odbc_connection_string_has_uid():
    """Valida que la connection string incluye UID (usuario)."""
    conn_str = config.odbc_connection_string()
    assert 'UID=' in conn_str
    print("✓ Connection string incluye UID")


def test_odbc_connection_string_has_pwd():
    """Valida que la connection string incluye PWD (password)."""
    conn_str = config.odbc_connection_string()
    assert 'PWD=' in conn_str
    print("✓ Connection string incluye PWD")


def test_odbc_connection_string_consistency():
    """Valida que llamadas sucesivas devuelven el mismo resultado (determinístico)."""
    str1 = config.odbc_connection_string()
    str2 = config.odbc_connection_string()
    assert str1 == str2
    print("✓ Connection string es determinístico")


def test_odbc_connection_string_format():
    """Valida que el formato es válido (KEY=VALUE; separados por ;)."""
    conn_str = config.odbc_connection_string()
    assert ';' in conn_str  # Debe tener múltiples parámetros
    assert '=' in conn_str  # Formato KEY=VALUE
    print("✓ Formato de connection string válido")
