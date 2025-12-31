from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from decimal import Decimal
from app.domain.repositories.saint_cxc_repository import SaintCxCRepository
from app.infrastructure.database.models import SaAcxc

class SaintCxCRepositoryImpl(SaintCxCRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

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
