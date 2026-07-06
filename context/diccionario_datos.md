# Diccionario de datos — Cuenta Corriente

Este archivo le da al modelo el **significado de negocio** de cada cosa.
No incluye SQL: el modelo nunca escribe consultas, solo elige tools.

## Tablas base (referencia, el modelo NO las consulta)

- **`DATOS..CLIENTAS`** — maestro de clientes.
  - `nrocli` — id interno del cliente.
  - `nrorep` — **zona / vendedor** (clave de seguridad). Cada vendedor
    maneja los clientes con su `nrorep`.
  - `vcden` — razón social / nombre.
  - `vcdom`, `vccpo`, `vcloc` — domicilio, código postal, localidad.
  - `vcccu`, `vcncu` — tipo y número de documento (CUIT).
  - `id_cliente` — id alternativo.

## Campos que devuelve la cuenta corriente (tabla #ctacte_t)

| Campo | Significado |
|---|---|
| `NRO_REPAS` | Zona / vendedor del movimiento |
| `NRO_CLIAS` | Cliente del movimiento |
| `FECHA_FACT` | Fecha del comprobante |
| `TIPO_COMP` + `TIPO_FACT` | Tipo de comprobante (FA = factura, NC = nota de crédito, Rec = recibo, etc.) |
| `NRO_SER`, `NRO_FACT` | Serie y número del comprobante |
| `IMPORTE_D` | **Debe** (lo que el cliente debe: facturas) |
| `IMPORTE_H` | **Haber** (lo que descuenta: recibos, NC) |
| `SALDO_COMPROBANTE` | Saldo abierto de ese comprobante (si > 0, sigue impago) |
| `DIAS` | Días transcurridos / mora del comprobante |
| `CH_POSTDATA` | Cheques postdatados |
| `CH_XACREDIT` | Cheques pendientes de acreditar |
| `FECH_CANC` | Fecha de cancelación (si fue pagado) |

## Métricas derivadas (lo que devuelven los SP del chat)

- **saldo** = `SUM(IMPORTE_D - IMPORTE_H)` — lo que el cliente debe hoy.
- **deuda_total** = `saldo + cheques_postdatados + cheques_pend_acred`.
- **dias_mora_max** = mayor `DIAS` entre los comprobantes con `SALDO_COMPROBANTE > 0`.

## Anclas de validación (datos reales, zona 1)

- Cliente 3523 (PINTO HERMANOS S.A.) → deuda_total **4.730.599,72**
- Cliente 33595 (SUPERMERCADOS PETRELLI) → deuda_total **5.160.920,23**
- Cliente 34056 (BALEAR S.A.) → deuda_total **5.872.167,95**
- Cliente 32449 (COMERCIAL GALETTI) → deuda_total **966.731,60**
- **Saldo general zona 1 (sin cheques) = 16.730.419,5**
