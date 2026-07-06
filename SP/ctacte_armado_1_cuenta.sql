USE [DATOS_COBRANZAS]
GO
/****** Object:  StoredProcedure [dbo].[ctacte_armado_1_cuenta]    Script Date: 30/06/2026 15:08:42 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER OFF
GO
ALTER PROCEDURE [dbo].[ctacte_armado_1_cuenta] 
	@suc tinyint,
	@nrorep smallint,
	@nrocli int,
	@fechacanc  smalldatetime, -- 01/mes/año desde cancelados + pendientes
	@fechadesde smalldatetime, 
	@fechahasta smalldatetime,
	@tablaf varchar(100),
    @tablac varchar(100),
	@tablar varchar(100),
    @tablai varchar(100),
	@ccDBSQL_pru char(4),
	@saldini money 
AS

--- Saldo INICIAL resumido
------- SE BUSCA SALDO ULTIMA FECHA, POSTERIOR A LA FECHA SOLICITADA
declare @error int
declare @query varchar(6000)	
declare @fechasal smalldatetime
declare @fechasaldo smalldatetime
declare @saldini_0 money

set @query=" DECLARE cursor_temp CURSOR for "
set @query=@query+" select FECHASALDO, SALDO from DATOS_COBRANZAS"+@ccDBSQL_pru+"..SALD_CAS"
set @query=@query+"            where "
set @query=@query+"                  NRO_REPAS = "+str(@nrorep)+" and "
set @query=@query+"                  NRO_CLIAS = "+str(@nrocli)
exec(@query)
--abro y recorro el cursor, cargando la tabla local temporaria
set @fechasaldo = "1900-01-01"
set @saldini = 0

select @error = @@error
if @error=0
begin
	open cursor_temp           
	select @error=@@error
	if @error=0
	begin

		FETCH next from cursor_temp
		INTO @fechasal, @saldini_0
		if @@FETCH_STATUS = 0
		begin
			if 	@fechasal < @fechadesde  
			begin
				set @fechasaldo = @fechasal
				set @saldini = @saldini_0
			end
		end
		close cursor_temp
		deallocate cursor_temp
	end
	else
	begin
		deallocate cursor_temp
		return
	end
end

--- Consulta para incorporar otros datos
-- le agrego información final 
declare @xxtotal_adic_1 money
declare @xxtotal_adic_2 money
exec datos_cobranzas..ctacte_genero_final @suc,@nrorep ,@nrocli,@ccDBSQL_pru,
			@xxtotal_adic_1 output,
			@xxtotal_adic_2 output

--- Incorporo Comprobantes
declare @saldo_1 money
exec	[dbo].[ctacte_inc_movs_f]
		@suc ,
		@nrorep ,
		@nrocli ,
		@fechasaldo ,
		@fechacanc,
		@fechadesde,
		@fechahasta,	
		@tablaf,
		@ccDBSQL_pru,
		@xxtotal_adic_1 ,
		@xxtotal_adic_2 ,
		@saldini,	--trae el saldo resumido
		@saldo = @saldo_1 output

--- Incorporo Minutas - pasar el saldini del paso anterior
declare @saldo_2 money
exec	[dbo].[ctacte_inc_movs_C]
		@suc ,
		@nrorep ,
		@nrocli ,
		@fechasaldo ,
		@fechacanc,
		@fechadesde,
		@fechahasta,	
		@tablaC,
		@ccDBSQL_pru,
		@xxtotal_adic_1 ,
		@xxtotal_adic_2 ,
		@saldo_1,	--- trae el saldo del paso anterior
		@saldo = @saldo_2 output
--- Incorporo Recibos - pasar el saldini del paso anterior
declare @saldo_3 money
exec	[dbo].[ctacte_inc_movs_r]
		@suc ,
		@nrorep ,
		@nrocli ,
		@fechasaldo ,
		@fechacanc,
		@fechadesde,
		@fechahasta,	
		@tablar,
		@ccDBSQL_pru,
		@xxtotal_adic_1 ,
		@xxtotal_adic_2 ,
		@saldo_2,	--- trae el saldo del paso anterior
		@saldo = @saldo_3 output
--- Incorporo Informes de Reclamos - pasar el saldini del paso anterior
declare @saldo_4 money
exec	[dbo].[ctacte_inc_movs_i]
		@suc ,
		@nrorep ,
		@nrocli ,
		@fechasaldo ,
		@fechacanc,
		@fechadesde,
		@fechahasta,	
		@tablai,
		@ccDBSQL_pru,
		@xxtotal_adic_1 ,
		@xxtotal_adic_2 ,
		@saldo_3,	--- trae el saldo del paso anterior
		@saldo = @saldo_4 output
--- el saldini de la 4º tabla es el que sirve
--	select @saldini_0 as 'Saldo Inicial', @saldo_1 as 'Saldo 1',  @saldo_2 as 'Saldo 2',
--			@saldo_3 as 'Saldo 3', @saldo_4 as 'Saldo 4'

--- Incorporo Saldo Inicial
	  insert into #ctacte_t
		(NRO_REPAS,NRO_CLIAS,FECHA_FACT,TIPO_COMP2,IMPORTE_D,IMPORTE_H,CH_POSTDATA,CH_XACREDIT) 
		values
		(@nrorep,@nrocli,@fechadesde-1,'S',
		(case when @saldo_4 >= 0 then @saldo_4 else 0 end),
		(case when @saldo_4 >= 0 then 0 else -@saldo_4 end),
		@xxtotal_adic_1 ,
		@xxtotal_adic_2 
		) --- le agregué los 2 últimos campos, porque si la cuenta estaba en 0, no le mostraba los posibles cheques postdatados

























