/* =====================================================================
   chat_top_morosos
   Devuelve el TOP N de clientes con mas deuda de UNA zona puntual
   (reporte para GERENTES).

   Version simple (demo): @nro_zona es OBLIGATORIO (ver chat_deuda_por_zona
   para la razon: recorrer todas las zonas via el obrero legacy no escala).

   VALIDACION:
     EXEC dbo.chat_top_morosos @nro_zona = 1, @top_n = 5;
   ===================================================================== */
USE [DATOS_COBRANZAS];
GO
SET ANSI_NULLS ON;
GO
SET QUOTED_IDENTIFIER ON;
GO
IF OBJECT_ID('dbo.chat_top_morosos','P') IS NOT NULL
    DROP PROCEDURE dbo.chat_top_morosos;
GO
CREATE PROCEDURE dbo.chat_top_morosos
    @nro_zona smallint,            -- OBLIGATORIO, sin default
    @top_n    int       = 10
WITH EXECUTE AS OWNER
AS
BEGIN
    SET NOCOUNT ON;

    CREATE TABLE #result (
        AFECTADO           varchar(30),
        vcden               varchar(800),
        TABLA_SQL           varchar(100),
        CLAVE1_SQL          varchar(15),
        CLAVE2_SQL          varchar(15),
        CLAVE3_SQL          varchar(15),
        CLAVE4_SQL          varchar(15),
        CLAVE5_SQL          varchar(15),
        NRO_REPAS           int,
        NRO_CLIAS           int,
        FECHA_FACT          smalldatetime,
        TIPO_COMP           char(1),
        TIPO_FACT           char(1),
        NRO_SER             smallint,
        NRO_FACT            int,
        TIPO_COMP2          char(1),
        TIPO_FACT2          char(1),
        NRO_SER2            smallint,
        NRO_COMP            int,
        TIPO_RECL           char(1),
        FECHA_RECL          smalldatetime,
        IMPORTE_D           money,
        IMPORTE_H           money,
        FECH_CANC           smalldatetime,
        OTRA_DESCR          varchar(50),
        ES_DEVUELT          bit,
        NRO_55              smallint,
        DIAS                int,
        ORDEN               int,
        ID_AUTOMATICA       int,
        ABREVIATURA         char(6),
        CH_POSTDATA         money,
        CH_XACREDIT         money,
        SALDO_COMPROBANTE   money
    );

    DECLARE @hasta smalldatetime = CAST(GETDATE() AS smalldatetime);

    INSERT INTO #result
    EXEC dbo.ctacte_armado_sql
        @suc            = 0,
        @nrorep         = @nro_zona,
        @nrocli         = 0,           -- 0 = toda la zona
        @fechacanc      = '20360101',
        @fechadesde     = '19000102',
        @fechahasta     = @hasta,
        @tablaf         = 'DATOS..FACTURAP',
        @tablac         = 'DATOS_COBRANZAS..CCMINUTA',
        @tablar         = 'DATOS_COBRANZAS..RECIFACT',
        @tablai         = 'DATOS_COBRANZAS..INF_RECL',
        @ccDBSQL_pru    = ' ',
        @saldini        = 0;

    ;WITH por_cliente AS (
        SELECT
            c.nrocli,
            RTRIM(c.vcden)                                              AS cliente,
            ISNULL(SUM(r.IMPORTE_D - r.IMPORTE_H), 0)
                + ISNULL(MAX(r.CH_POSTDATA), 0)
                + ISNULL(MAX(r.CH_XACREDIT), 0)                         AS deuda_total,
            MAX(CASE WHEN r.SALDO_COMPROBANTE > 0 THEN r.DIAS END)      AS dias_mora_max
        FROM DATOS..CLIENTAS c
        LEFT JOIN #result r
            ON r.NRO_CLIAS = c.nrocli AND r.NRO_REPAS = c.nrorep
        WHERE c.nrorep = @nro_zona
        GROUP BY c.nrocli, c.vcden
    )
    SELECT TOP (@top_n)
        nrocli                          AS cliente_id,
        cliente,
        @nro_zona                       AS nro_zona,
        deuda_total,
        dias_mora_max
    FROM por_cliente
    WHERE deuda_total <> 0
    ORDER BY deuda_total DESC;

    DROP TABLE #result;
END
GO
