USE [DATOS_COBRANZAS]
GO
/****** Object:  StoredProcedure [dbo].[ctacte_armado_sql]    Script Date: 30/06/2026 14:57:39 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER OFF
GO
ALTER PROCEDURE [dbo].[ctacte_armado_sql] 
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
--- si bien está preparado (aunque no probado) para traer datos de las tablas históricas,
--- no se lo implementó adrede, para que vía internet no se pida tanta información histórica.
	create table #ctacte_t(
		TABLA_SQL	[varchar] (100),
		CLAVE1_SQL	[varchar] (15),
		CLAVE2_SQL	[varchar] (15),
		CLAVE3_SQL	[varchar] (15),
		CLAVE4_SQL	[varchar] (15),
		CLAVE5_SQL	[varchar] (15),
		NRO_REPAS 	int,
		NRO_CLIAS 	int,
		FECHA_FACT 	smalldatetime,
		TIPO_COMP	char(1),
		TIPO_FACT	char(1),
		NRO_SER		smallint,
		NRO_FACT	int,
		TIPO_COMP2	char(1),
		TIPO_FACT2	char(1),
		NRO_SER2	smallint,
		NRO_COMP	int,
		TIPO_RECL	char(1),
		FECHA_RECL	smalldatetime,
		IMPORTE_D	money,
		IMPORTE_H	money,
		FECH_CANC	smalldatetime,
		OTRA_DESCR	varchar(50),
		ES_DEVUELT  bit,
		NRO_55		smallint,
		DIAS		int,
		ORDEN		int,
		ID_AUTOMATICA int IDENTITY,
		ABREVIATURA char(6),
		CH_POSTDATA money,
		CH_XACREDIT	money,
		SALDO_COMPROBANTE money
	)

delete from #ctacte_t --- borro tabla temporaria

declare @error int
declare @que_cliente int

--- si @nrocli = 0, es porque se solicito la Cuenta Corriente de toda la Zona
if @nrocli <> 0
begin
	exec [dbo].[ctacte_armado_1_cuenta] 
		@suc,
		@nrorep,
		@nrocli,
		@fechacanc, -- 01/mes/año desde cancelados + pendientes
		@fechadesde, 
		@fechahasta,
		@tablaf,
		@tablac,
		@tablar,
		@tablai,
		@ccDBSQL_pru,
		@saldini

	--- Ordeno la Cuenta Corriente 
	exec ctacte_xComp_sql @nrorep, @nrocli, 0

end

else   --- @nrocli = 0 => solicitó toda la zona
begin
	DECLARE cursor_CLI CURSOR for 
	select nrocli
		from DATOS..CLIENTAS
		where NROREP = @nrorep

	select @error = @@error
	if @error=0
	begin
		open cursor_CLI           
		select @error=@@error
		if @error=0
		begin

			FETCH next from cursor_CLI
				INTO @que_cliente
			
			while @@FETCH_STATUS = 0
			begin
				----------------------------ejecuto el procedimiento para cada cta.cte.
				exec [dbo].[ctacte_armado_1_cuenta] 
					@suc,
					@nrorep,
					@que_cliente,		--- averiguado
					@fechacanc, -- 01/mes/año desde cancelados + pendientes
					@fechadesde, 
					@fechahasta,
					@tablaf,
					@tablac,
					@tablar,
					@tablai,
					@ccDBSQL_pru,
					@saldini

				--- Ordeno la Cuenta Corriente 
				exec ctacte_xComp_sql @nrorep, @que_cliente, 0

				-- avanzo 1 registro
				FETCH next from cursor_CLI
				INTO @que_cliente
			end
			close cursor_CLI
			deallocate cursor_CLI
		end
		else
		begin
			deallocate cursor_CLI
			return
		end
	end
end

--- si se pidió PENDIENTES
--- borro los que a pesar de estar cancelados, no están con la FECH_CANC
if @fechacanc > getdate()
begin
	delete from #ctacte_t
	where STR(NRO_REPAS,3)+STR(NRO_CLIAS,5)+TIPO_COMP+TIPO_FACT+STR(NRO_SER,4)+STR(NRO_FACT,10) IN
		(SELECT STR(NRO_REPAS,3)+STR(NRO_CLIAS,5)+TIPO_COMP+TIPO_FACT+STR(NRO_SER,4)+STR(NRO_FACT,10)
			from #ctacte_t
			where TIPO_COMP2 <> 'S' 
			GROUP BY STR(NRO_REPAS,3)+STR(NRO_CLIAS,5)+TIPO_COMP+TIPO_FACT+STR(NRO_SER,4)+STR(NRO_FACT,10)
			HAVING SUM(IMPORTE_D-IMPORTE_H)= 0
		)
end

-- le agrego encabezado(s)
	select case when OTRA_DESCR = ' - sin Comp.Afect.' then 'PAGOS NO AFECTADOS' 
				when ORDEN = 999999 then 'RESTO NO AFECTADO'
				else tipo_comp+tipo_fact+str(nro_ser,4)+' '+str(nro_fact,8) end as AFECTADO,

				b.vcden+'(Tipo/Nº.Doc:'+rtrim(ltrim(str(b.vcccu)))+'/'+str(b.vcncu,11)+')'+
				char(13)+char(10)+b.vcdom+'-('+substring(str(b.vccpo,6),1,4)+') '+b.vcloc+
				case when b.id_cliente > 0 then '*** ID_CLIENTE: '+ltrim(STR(b.id_cliente,10))+' ***' else '' end
				--char(13)+char(10)+replicate('...',40)+
				--char(13)+char(10)+'Alta:'+substring(str(b.vcfal,6),1,2)+'/'+substring(str(b.vcfal,6),3,2)+'/'+substring(str(b.vcfal,6),5,2)+'-' 
						as vcden,
				a.* 
		from #ctacte_t a
		left join datos..clientas b
			on a.nro_repas = b.nrorep and a.nro_clias = b.nrocli
		ORDER BY a.nro_repas, a.nro_clias,ORDEN asc


	drop table #ctacte_t



























