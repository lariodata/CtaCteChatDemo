"""
Test de conexión a SQL Server y validación de login chat_app.
Útil para debuggear problemas de autenticación.

Correr:
  pytest tests/test_db_connection.py -v -s
"""

import pyodbc
import pytest
from src import config


def test_connection_user_details():
    """Verifica los valores del usuario en el .env."""
    print(f"\n📋 Configuración actual:")
    print(f"  SQL_SERVER:   {config.SQL_SERVER}")
    print(f"  SQL_DATABASE: {config.SQL_DATABASE}")
    print(f"  SQL_USER:     {config.SQL_USER}")
    print(f"  SQL_DRIVER:   {config.SQL_DRIVER}")
    print(f"  SQL_PASSWORD: {'*' * (len(config.SQL_PASSWORD) - 3) + config.SQL_PASSWORD[-3:] if config.SQL_PASSWORD else '(vacío)'}")

    assert config.SQL_SERVER, "SQL_SERVER no configurado"
    assert config.SQL_DATABASE, "SQL_DATABASE no configurado"
    assert config.SQL_USER, "SQL_USER no configurado"
    assert config.SQL_PASSWORD, "SQL_PASSWORD no configurado"
    print("✓ Todos los valores están configurados\n")


def test_connection_string():
    """Verifica que la cadena de conexión se genera correctamente."""
    conn_str = config.odbc_connection_string()
    print(f"\n📌 Connection String generada:\n{conn_str}\n")

    # Verifica que tenga los componentes críticos
    assert "DRIVER" in conn_str
    assert "SERVER" in conn_str
    assert "DATABASE" in conn_str
    assert "UID" in conn_str
    assert "PWD" in conn_str
    print("✓ Cadena de conexión OK\n")


def test_connection_without_database():
    """Intenta conectar a SQL Server SIN especificar BD (conecta a master)."""
    print(f"\n🔗 Test 1: Conectar sin especificar BD inicial (master)...\n")

    try:
        conn_str = (
            f"DRIVER={{{config.SQL_DRIVER}}};"
            f"SERVER={config.SQL_SERVER};"
            f"UID={config.SQL_USER};PWD={config.SQL_PASSWORD};"
            f"TrustServerCertificate=yes;"
        )
        print(f"Connection string: {conn_str}\n")

        with pyodbc.connect(conn_str) as conn:
            print("✓ Conexión a master OK")
            cursor = conn.cursor()
            cursor.execute("SELECT 1 AS test")
            result = cursor.fetchone()
            assert result[0] == 1
            print("✓ Query SELECT 1 OK\n")
            return True

    except Exception as e:
        print(f"✗ Error conectando a master: {e}\n")
        return False


def test_connection_with_database():
    """Intenta conectar a SQL Server especificando la BD DATOS_COBRANZAS."""
    print(f"\n🔗 Test 2: Conectar especificando BD DATOS_COBRANZAS...\n")

    try:
        conn_str = config.odbc_connection_string()
        print(f"Connection string: {conn_str}\n")

        with pyodbc.connect(conn_str) as conn:
            print("✓ Conexión a DATOS_COBRANZAS OK")
            cursor = conn.cursor()
            cursor.execute("SELECT 1 AS test")
            result = cursor.fetchone()
            assert result[0] == 1
            print("✓ Query SELECT 1 OK\n")
            return True

    except Exception as e:
        print(f"✗ Error conectando a DATOS_COBRANZAS: {e}\n")
        return False


def test_sp_chat_consultar_deuda():
    """Intenta ejecutar el SP chat_consultar_deuda."""
    print(f"\n🔍 Test 3: Ejecutar SP chat_consultar_deuda...\n")

    try:
        conn_str = config.odbc_connection_string()

        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()

            # Cliente 3523 debe devolver deuda de 4730599.72 (Etapa 1 validado)
            cursor.execute(
                "EXEC dbo.chat_consultar_deuda @nrorep = ?, @nrocli = ?",
                1, 3523
            )

            row = cursor.fetchone()
            if row:
                cols = [c[0] for c in cursor.description]
                result = dict(zip(cols, row))
                print(f"✓ SP ejecutado exitosamente")
                print(f"  Cliente ID: {result.get('cliente_id')}")
                print(f"  Cliente:    {result.get('cliente')}")
                print(f"  Deuda:      ${result.get('deuda_total')}")
                assert float(result["deuda_total"]) == pytest.approx(4730599.72, abs=0.01)
                print(f"✓ Deuda validada: $4.730.599,72 OK\n")
            else:
                raise AssertionError("SP no devolvió resultados")

    except Exception as e:
        print(f"✗ Error ejecutando SP: {e}\n")
        raise


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
