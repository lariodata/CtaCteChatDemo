"""
Test de validación de la Etapa 1 (estilo TDD).
Antes de construir nada de IA encima, confirmamos que los SP devuelven los
números REALES del reporte. Si esto pasa, la base está bien.

Requiere: SP creados + .env configurado + acceso a la base.
Correr:  pytest tests/test_validacion_sp.py -v
"""
import pytest
from src import dal

# Anclas de verdad sacadas del reporte real (zona 1)
CASOS = [
    (1, 3523, 4730599.72),    # PINTO HERMANOS S.A.
    (1, 33595, 5160920.23),   # SUPERMERCADOS PETRELLI
    (1, 34056, 5872167.95),   # BALEAR S.A.
    (1, 32449, 966731.60),    # COMERCIAL GALETTI
]


@pytest.mark.parametrize("nrorep,nrocli,esperado", CASOS)
def test_consultar_deuda(nrorep, nrocli, esperado):
    r = dal.consultar_deuda(nrorep, nrocli)
    assert r is not None, "el SP no devolvió fila"
    assert float(r["deuda_total"]) == pytest.approx(esperado, abs=0.01)


def test_saldo_general_zona1():
    """La suma de la zona debe dar el 'Saldo General (sin Cheques)' = 16.730.419,5"""
    filas = dal.clientes_por_zona(nrorep=1, solo_con_deuda=False)
    total = sum(float(f["saldo"] or 0) for f in filas)
    assert total == pytest.approx(16730419.5, abs=0.5)


def test_vendedor_no_ve_otra_zona():
    """Un cliente de zona 1 consultado como zona 3 no debe devolver deuda."""
    r = dal.consultar_deuda(nrorep=3, nrocli=3523)
    assert r is None or float(r.get("deuda_total") or 0) == 0
