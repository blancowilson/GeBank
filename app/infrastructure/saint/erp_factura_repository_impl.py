from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.domain.repositories.factura_repository import FacturaRepository
from app.domain.entities.factura import Factura
from app.infrastructure.database.models import SaFact, SaAcxc, VwAdmFactConBs

class ERPFacturaRepositoryImpl(FacturaRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def obtener_por_id(self, numero: str, tipo: str) -> Optional[Factura]:
        stmt = select(
            SaFact, 
            (func.isnull(VwAdmFactConBs.SUBTOTAL_BS, 0) + func.isnull(VwAdmFactConBs.IMPUESTO_BS, 0)).label("total_bs")
        ).join_from(
            SaFact, VwAdmFactConBs, and_(
                SaFact.NumeroD == VwAdmFactConBs.NumeroD,
                SaFact.TipoFac == VwAdmFactConBs.TipoFac
            ),
            isouter=True
        ).where(
            and_(SaFact.NumeroD == numero, SaFact.TipoFac == tipo)
        )
        record = (await self.session.execute(stmt)).first()
        
        if not record:
            return None

        sa_fact, total_bs = record
        saldo = (await self.session.execute(
            select(SaAcxc.Saldo).where(and_(SaAcxc.NumeroD == numero, SaAcxc.CodClie == sa_fact.CodClie))
        )).scalar_one_or_none() or sa_fact.Monto

        return Factura(
            numero=sa_fact.NumeroD,
            tipo=sa_fact.TipoFac,
            sucursal=sa_fact.CodSucu,
            cliente_id=sa_fact.CodClie,
            vendedor_id=sa_fact.CodVend,
            monto_total=sa_fact.Monto,
            monto_total_bs=total_bs if total_bs is not None else Decimal("0.00"),
            saldo_pendiente=saldo,
            fecha_emision=sa_fact.FechaE,
            fecha_vencimiento=sa_fact.FechaV
        )

    async def obtener_pendientes_por_cliente(self, cliente_id: str) -> List[Factura]:
        stmt = select(
            SaAcxc.NumeroD, SaAcxc.CodSucu, SaAcxc.CodClie, SaAcxc.Monto, 
            SaAcxc.Saldo, SaAcxc.FechaE, SaAcxc.FechaV, SaAcxc.TipoCXC,
            (func.isnull(VwAdmFactConBs.SUBTOTAL_BS, 0) + func.isnull(VwAdmFactConBs.IMPUESTO_BS, 0)).label("total_bs")
        ).join_from(
            SaAcxc, VwAdmFactConBs, and_(
                SaAcxc.NumeroD == VwAdmFactConBs.NumeroD
            ),
            isouter=True
        ).where(
            and_(
                SaAcxc.CodClie == cliente_id,
                SaAcxc.Saldo > 0,
                SaAcxc.TipoCXC == '10' # Filter for invoices (TipoCXC = '10')
            )
        )
        records = (await self.session.execute(stmt)).all()
        
        facturas = []
        for cxc in records:
            total_bs = cxc.total_bs or Decimal("0.00")
            facturas.append(Factura(
                numero=cxc.NumeroD,
                tipo=cxc.TipoCXC, # Use TipoCXC from SAACXC
                sucursal=cxc.CodSucu,
                cliente_id=cxc.CodClie,
                monto_total=cxc.Monto,
                monto_total_bs=total_bs,
                saldo_pendiente=cxc.Saldo,
                fecha_emision=cxc.FechaE,
                fecha_vencimiento=cxc.FechaV
            ))
            
        return facturas