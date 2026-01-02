from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.domain.repositories.pago_repository import PagoRepository
from app.domain.entities.pago import Pago
from app.infrastructure.database.models import SaPagcxc, SaAcxc

class ERPPagoRepositoryImpl(PagoRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def registrar(self, pago: Pago) -> Pago:
        # 1. Update SAACXC saldo
        stmt = update(SaAcxc).where(
            SaAcxc.NumeroD == pago.factura_numero,
            SaAcxc.CodClie == pago.cliente_id
        ).values(
            Saldo=SaAcxc.Saldo - pago.monto.valor,
            CancelE=SaAcxc.CancelE + pago.monto.valor
        ).execution_options(synchronize_session="fetch")
        
        await self.session.execute(stmt)
        # Commit should be handled by Use Case for atomicity
        return pago
