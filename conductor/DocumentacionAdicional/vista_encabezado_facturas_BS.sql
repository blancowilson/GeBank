USE [SEA_InversionesHJDB_Test]
GO

/****** Object:  View [dbo].[VW_ADM_FACT_CONBS]    Script Date: 29/12/2025 19:49:51 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO










ALTER VIEW [dbo].[VW_ADM_FACT_CONBS] AS 


SELECT        T1.TipoFac, T1.NumeroD,T1.MtoTax,
				ISNULL(T2.BASEIMPONIBLE, 0) + ISNULL(T3.EXENTO, 0)  AS SUBTOTAL_MAS_DESCUENTO, 
				ISNULL(T2.BASEIMPONIBLE, 0) + ISNULL(T3.EXENTO, 0) AS SUBTOTAL, 
                ISNULL(T2.BASEIMPONIBLE, 0) AS BASEIMPONIBLE, ISNULL(T2.IMPUESTO, 0) AS IMPUESTO,
				ISNULL(T3.EXENTO, 0) AS EXENTO, ISNULL(T1.Descto1, 0) AS DESCUENTO,
				ISNULL(T2.BASEIMPONIBLEBS, 0) + ISNULL(T3.EXENTO, 0)  AS SUBTOTAL_MAS_DESCUENTO_BS,
				ISNULL(T2.BASEIMPONIBLEBS, 0) + ISNULL(T3.EXENTO, 0) AS SUBTOTAL_BS,
				ISNULL(T2.BASEIMPONIBLEBS, 0) AS BASEIMPONIBLE_BS, 
				ISNULL(T2.IMPUESTOBs, 0) AS IMPUESTO_BS, ISNULL(T3.EXENTO, 0) * T1.Factor AS EXENTO_BS,
				ISNULL(T1.Descto1, 0) * T1.Factor AS DESCUENTO_BS,
				T1.FACTOR AS FACTOR
FROM            dbo.SAFACT AS T1 LEFT OUTER JOIN
                             (SELECT        TipoFac, NumeroD, SUM(TotalItem*0.16) AS IMPUESTO,  SUM((ROUND(Precio*tasa,4)*CANTIDAD)*0.16) AS IMPUESTOBS,
								SUM(Precio*Cantidad) AS BASEIMPONIBLE,SUM(ROUND(Precio*tasa,4)*CANTIDAD) AS BASEIMPONIBLEBS
                               FROM            dbo.SAITEMFAC
                               GROUP BY TipoFac, NumeroD) AS T2 ON T1.TipoFac = T2.TipoFac AND T1.NumeroD = T2.NumeroD LEFT OUTER JOIN
                             (SELECT        T1.TipoFac, T1.NumeroD, SUM(T1.TotalItem) AS EXENTO
                               FROM            dbo.SAITEMFAC AS T1 INNER JOIN
                                                         dbo.SAPROD AS T2 ON T1.CodItem = T2.CodProd
                               WHERE        (T2.EsExento = 1)
                               GROUP BY T1.TipoFac, T1.NumeroD) AS T3 ON T1.TipoFac = T3.TipoFac AND T1.NumeroD = T3.NumeroD


Where t1.TipoFac in ('A','B')
GO


