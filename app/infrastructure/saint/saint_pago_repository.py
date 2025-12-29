from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, text
from app.domain.repositories.pago_repository import PagoRepository
from app.domain.entities.pago import Pago
from app.infrastructure.database.models import SaAcxc, SaPagcxc
from datetime import datetime

class SaintPagoRepository(PagoRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def registrar(self, pago: Pago) -> Pago:
        async with self.session.begin():
            # 1. Update SAACXC saldo
            # Note: We find by NumeroD and CodClie. 
            # In a real scenario, we might need NroUnico.
            stmt = update(SaAcxc).where(
                SaAcxc.NumeroD == pago.factura_numero,
                SaAcxc.CodClie == pago.cliente_id
            ).values(
                Saldo=SaAcxc.Saldo - pago.monto.valor,
                CancelE=SaAcxc.CancelE + pago.monto.valor # Assuming effective payment for simplicity
            ).execution_options(synchronize_session="fetch")
            
            await self.session.execute(stmt)

            # 2. Get NroUnico of the CxC document to link payment
            # (Simplified: we should query it first if not provided)
            
            # 3. Insert into SAPAGCXC
            # This is a simplified insert. Saint has many fields.
            # We would typically use a stored procedure or trigger in a real Saint setup.
            # new_pago = SaPagcxc(
            #     CodClie=pago.cliente_id,
            #     FechaE=pago.fecha,
            #     Monto=pago.monto.valor,
            #     NumeroD=pago.factura_numero,
            #     Referen=pago.referencia
            # )
            # self.session.add(new_pago)
            
        await self.session.commit()
        return pago
