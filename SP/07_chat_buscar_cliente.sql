/* =====================================================================
   chat_buscar_cliente
   Busca clientes por nombre aproximado (LIKE), dentro de una zona puntual
   o en todas las zonas (@nrorep = NULL, solo gerentes).

   No pasa por ctacte_armado_sql: es un SELECT directo y liviano sobre
   CLIENTAS, solo para resolver nombre -> cliente_id antes de llamar a
   consultar_deuda / detalle_movimientos con el ID correcto.

   VALIDACION:
     EXEC dbo.chat_buscar_cliente @nrorep = 1, @nombre = 'PETRELLI';
     EXEC dbo.chat_buscar_cliente @nrorep = NULL, @nombre = 'PETRELLI'; -- todas las zonas

   PERMISOS:
     chat_app ya tiene GRANT SELECT ON dbo.* en DATOS y DATOS_COBRANZAS,
     asi que alcanza con otorgar EXECUTE sobre este SP puntual (mas abajo).
   ===================================================================== */
USE [DATOS_COBRANZAS];
GO
SET ANSI_NULLS ON;
GO
SET QUOTED_IDENTIFIER ON;
GO
IF OBJECT_ID('dbo.chat_buscar_cliente', 'P') IS NOT NULL
    DROP PROCEDURE dbo.chat_buscar_cliente;
GO
CREATE PROCEDURE dbo.chat_buscar_cliente
    @nrorep smallint = NULL,   -- NULL = todas las zonas (solo gerente)
    @nombre varchar(100)
AS
BEGIN
    SET NOCOUNT ON;

    SELECT TOP 20 nrocli AS cliente_id, RTRIM(vcden) AS cliente, nrorep AS nro_zona
    FROM DATOS..CLIENTAS
    WHERE vcden LIKE '%' + @nombre + '%'
      AND (@nrorep IS NULL OR nrorep = @nrorep)
    ORDER BY vcden;
END
GO

-- Permiso pendiente: chat_app solo tiene EXECUTE sobre SP puntuales, hay que agregar este.
GRANT EXECUTE ON dbo.chat_buscar_cliente TO chat_app;
GO
