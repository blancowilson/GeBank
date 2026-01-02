from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.domain.repositories.erp_cxc_repository import ERPCxCRepository
from app.domain.entities.factura import Factura
from app.infrastructure.database.models import SaAcxc, SaPagcxc
from decimal import Decimal

class ERPCxCRepositoryImpl(ERPCxCRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def obtener_facturas_pendientes(self, cod_cliente: str) -> List[Factura]:
        """
        Consulta las facturas y notas de débito pendientes de un cliente en SAACXC.
        """
        stmt = select(SaAcxc).where(
            SaAcxc.CodClie == cod_cliente,
            SaAcxc.Saldo > 0,
            SaAcxc.TipoCXC.in_(['10', '20']) # 10=Factura, 20=Nota de Débito
        ).order_by(SaAcxc.FechaE.asc())
        
        result = await self.session.execute(stmt)
        rows = result.scalars().all()
        
        return [
            Factura(
                numero=r.NumeroD,
                tipo=r.TipoCXC,
                fecha_emision=r.FechaE,
                fecha_vencimiento=r.FechaV,
                monto_original=r.Monto,
                saldo=r.Saldo,
                cod_cliente=r.CodClie
            ) for r in rows
        ]

    async def aplicar_pago_documento(
        self,
        numero_documento: str,
        cod_cliente: str,
        monto_pago: Decimal,
        monto_descuento: Decimal,
        monto_retencion: Decimal
    ) -> None:
        """
        Actualiza el saldo de una factura en SAACXC.
        - `monto_pago` se suma a los campos de cancelación (ej. CancelE para efectivo/transfer).
        - `monto_descuento` se suma a `CancelD`.
        - `monto_retencion` se suma a `CancelI` y `RetenIVA`.
        - El saldo (`Saldo`) se reduce por la suma de los tres.
        """
        total_a_cancelar = monto_pago + monto_descuento + monto_retencion
        
        stmt = update(SaAcxc).where(
            SaAcxc.NumeroD == numero_documento,
            SaAcxc.CodClie == cod_cliente
        ).values(
            Saldo=SaAcxc.Saldo - total_a_cancelar,
            CancelE=SaAcxc.CancelE + monto_pago, # Asume que el pago es efectivo/transferencia
            CancelD=SaAcxc.CancelD + monto_descuento,
            CancelI=SaAcxc.CancelI + monto_retencion,
            RetenIVA=SaAcxc.RetenIVA + monto_retencion
        ).execution_options(synchronize_session=False)

        await self.session.execute(stmt)
        # El commit se manejará en el use case.
