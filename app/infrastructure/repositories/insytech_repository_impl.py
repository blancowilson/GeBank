from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domain.entities.pago_insytech import GePagos, GeDocumentos, GeInstrumentos
from app.domain.repositories.insytech_repository import InsytechRepository
from app.infrastructure.database.models import GePagos as DBGePagos, \
                                                GeDocumentos as DBGeDocumentos, \
                                                GeInstrumentos as DBGeInstrumentos

class InsytechRepositoryImpl(InsytechRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def guardar_pago_completo(self, pago: GePagos, documentos: List[GeDocumentos], instrumentos: List[GeInstrumentos]) -> GePagos:
        db_pago = DBGePagos(
            idPago=pago.idPago,
            codCliente=pago.codCliente,
            DescripClie=pago.DescripClie,
            Usuario=pago.Usuario,
            fecha=pago.fecha,
            MontoPago=pago.MontoPago,
            MontoCancelado=pago.MontoCancelado,
            status=pago.status,
            UrlImagen=pago.UrlImagen,
            fechaCaptura=pago.fechaCaptura
        )
        self.session.add(db_pago)
        await self.session.flush() # Flush to get the DB-assigned ID for GePagos

        for doc in documentos:
            db_doc = DBGeDocumentos(
                idPago=pago.idPago, # Link using idPago
                tipoDoc=doc.tipoDoc,
                numeroDoc=doc.numeroDoc,
                emision=doc.emision,
                vencimiento=doc.vencimiento,
                montoDoc=doc.montoDoc,
                porcentajeDescuento=doc.porcentajeDescuento,
                montoDescuento=doc.montoDescuento,
                porcentajeRetencion=doc.porcentajeRetencion,
                montoRetencion=doc.montoRetencion,
                NroRetencion=doc.NroRetencion,
                UrlRetencion=doc.UrlRetencion
            )
            self.session.add(db_doc)

        for instr in instrumentos:
            db_instr = DBGeInstrumentos(
                idPago=pago.idPago, # Link using idPago
                banco=instr.banco,
                formaPago=instr.formaPago,
                nroPlanilla=instr.nroPlanilla,
                fecha=instr.fecha,
                tasa=instr.tasa,
                cheque=instr.cheque,
                bancoCliente=instr.bancoCliente,
                monto=instr.monto,
                moneda=instr.moneda
            )
            self.session.add(db_instr)
        
        await self.session.commit()
        return pago # Return the original pago entity for confirmation

    async def obtener_pago_por_id(self, pago_id: str) -> Optional[GePagos]:
        stmt = select(DBGePagos).where(DBGePagos.idPago == pago_id)
        result = await self.session.execute(stmt)
        db_pago = result.scalar_one_or_none()
        
        if db_pago:
            return GePagos(
                id=db_pago.id,
                idPago=db_pago.idPago,
                codCliente=db_pago.codCliente,
                DescripClie=db_pago.DescripClie,
                Usuario=db_pago.Usuario,
                fecha=db_pago.fecha,
                MontoPago=db_pago.MontoPago,
                MontoCancelado=db_pago.MontoCancelado,
                status=db_pago.status,
                UrlImagen=db_pago.UrlImagen,
                fechaCaptura=db_pago.fechaCaptura
            )
        return None

    async def obtener_documentos_por_pago(self, pago_id: str) -> List[GeDocumentos]:
        stmt = select(DBGeDocumentos).where(DBGeDocumentos.idPago == pago_id)
        result = await self.session.execute(stmt)
        db_docs = result.scalars().all()
        
        return [
            GeDocumentos(
                id=doc.id,
                idPago=doc.idPago,
                tipoDoc=doc.tipoDoc,
                numeroDoc=doc.numeroDoc,
                emision=doc.emision,
                vencimiento=doc.vencimiento,
                montoDoc=doc.montoDoc,
                porcentajeDescuento=doc.porcentajeDescuento,
                montoDescuento=doc.montoDescuento,
                porcentajeRetencion=doc.porcentajeRetencion,
                montoRetencion=doc.montoRetencion,
                NroRetencion=doc.NroRetencion,
                UrlRetencion=doc.UrlRetencion
            ) for doc in db_docs
        ]

    async def obtener_instrumentos_por_pago(self, pago_id: str) -> List[GeInstrumentos]:
        stmt = select(DBGeInstrumentos).where(DBGeInstrumentos.idPago == pago_id)
        result = await self.session.execute(stmt)
        db_instrs = result.scalars().all()

        return [
            GeInstrumentos(
                id=instr.id,
                idPago=instr.idPago,
                banco=instr.banco,
                formaPago=instr.formaPago,
                nroPlanilla=instr.nroPlanilla,
                fecha=instr.fecha,
                tasa=instr.tasa,
                cheque=instr.cheque,
                bancoCliente=instr.bancoCliente,
                monto=instr.monto,
                moneda=instr.moneda
            ) for instr in db_instrs
        ]

    async def obtener_pagos_por_status(self, status: int, limit: int = 100) -> List[GePagos]:
        stmt = select(DBGePagos).where(DBGePagos.status == status).limit(limit)
        result = await self.session.execute(stmt)
        db_pagos = result.scalars().all()

        return [
            GePagos(
                id=pago.id,
                idPago=pago.idPago,
                codCliente=pago.codCliente,
                DescripClie=pago.DescripClie,
                Usuario=pago.Usuario,
                fecha=pago.fecha,
                MontoPago=pago.MontoPago,
                MontoCancelado=pago.MontoCancelado,
                status=pago.status,
                UrlImagen=pago.UrlImagen,
                fechaCaptura=pago.fechaCaptura
            ) for pago in db_pagos
        ]
