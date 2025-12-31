from typing import List
from datetime import datetime
from decimal import Decimal
from app.application.dto.insytech_dto import PaymentPacketDTO, DocumentDetail, InstrumentDetail
from app.domain.entities.pago_insytech import GePagos, GeDocumentos, GeInstrumentos
from app.domain.repositories.insytech_repository import InsytechRepository
from app.domain.repositories.cliente_repository import ClienteRepository

class ReceivePaymentPacketUseCase:
    def __init__(self, insytech_repo: InsytechRepository, cliente_repo: ClienteRepository):
        self.insytech_repo = insytech_repo
        self.cliente_repo = cliente_repo

    async def execute(self, packet: PaymentPacketDTO) -> GePagos:
        # 1. Validate Client Existence
        cliente = await self.cliente_repo.obtener_por_id(packet.codCliente)
        if not cliente:
            raise ValueError(f"Cliente con código {packet.codCliente} no encontrado.")

        # 2. Basic Integrity Checks (Sum of amounts)
        total_instrumentos = sum(instr.monto for instr in packet.instrumentos)
        total_documentos_afectados = sum(doc.montoDoc - doc.montoDescuento - doc.montoRetencion for doc in packet.documentos)

        # Allow for a small tolerance due to potential floating point issues if coming from external systems
        # or rounding in Insytech. The reconciliation engine will do more precise checks.
        if abs(total_instrumentos + sum(doc.montoDescuento + doc.montoRetencion for doc in packet.documentos) - packet.MontoPago) > Decimal("0.01"):
             raise ValueError("La suma de los instrumentos y componentes administrativos no coincide con MontoPago.")
        
        # 3. Create GePagos entity
        ge_pagos_entity = GePagos(
            id=None, # Will be set by DB on insert
            idPago=packet.idPago,
            codCliente=packet.codCliente,
            DescripClie=packet.DescripClie,
            Usuario=packet.Usuario,
            fecha=packet.fecha,
            MontoPago=packet.MontoPago,
            MontoCancelado=packet.MontoCancelado,
            status=GePagos.PENDIENTE if packet.status == 0 else packet.status, # Map 0 to PENDIENTE(1)
            UrlImagen=packet.UrlImagen,
            fechaCaptura=packet.fechaCaptura
        )

        # 4. Create GeDocumentos entities
        ge_documentos_entities = [
            GeDocumentos(
                id=None,
                idPago=packet.idPago, # Link to parent pago
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
            ) for doc in packet.documentos
        ]

        # 5. Create GeInstrumentos entities
        ge_instrumentos_entities = [
            GeInstrumentos(
                id=None,
                idPago=packet.idPago, # Link to parent pago
                banco=instr.banco,
                formaPago=instr.formaPago,
                nroPlanilla=instr.nroPlanilla,
                fecha=instr.fecha,
                tasa=instr.tasa,
                cheque=instr.cheque,
                bancoCliente=instr.bancoCliente,
                monto=instr.monto,
                moneda=instr.moneda # Add moneda field
            ) for instr in packet.instrumentos
        ]

        # 6. Persist to database
        await self.insytech_repo.guardar_pago_completo(ge_pagos_entity, ge_documentos_entities, ge_instrumentos_entities)
        
        return ge_pagos_entity
