from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.domain.repositories.factura_repository import FacturaRepository
from app.domain.entities.factura import Factura
from app.infrastructure.database.models import SaFact, SaAcxc

class SaintFacturaRepository(FacturaRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def obtener_por_id(self, numero: str, tipo: str) -> Optional[Factura]:
        stmt = select(SaFact).where(
            and_(SaFact.NumeroD == numero, SaFact.TipoFac == tipo)
        )
        result = await self.session.execute(stmt)
        sa_fact = result.scalar_one_or_none()
        
        if not sa_fact:
            return None
            
        # Buscar saldo en SAACXC
        # Nota: La relación podría simplificar esto, pero lo hacemos explícito por claridad
        stmt_cxc = select(SaAcxc).where(
            and_(SaAcxc.NumeroD == numero, SaAcxc.CodClie == sa_fact.CodClie)
        )
        result_cxc = await self.session.execute(stmt_cxc)
        sa_cxc = result_cxc.scalar_one_or_none()
        
        saldo = sa_cxc.Saldo if sa_cxc else sa_fact.Monto # Si no hay CxC, asumimos monto total (o 0, depende regla negocio)

        return Factura(
            numero=sa_fact.NumeroD,
            tipo=sa_fact.TipoFac,
            sucursal=sa_fact.CodSucu,
            cliente_id=sa_fact.CodClie,
            vendedor_id=sa_fact.CodVend,
            monto_total=sa_fact.Monto,
            saldo_pendiente=saldo,
            fecha_emision=sa_fact.FechaE,
            fecha_vencimiento=sa_fact.FechaV
        )

    async def obtener_pendientes_por_cliente(self, cliente_id: str) -> List[Factura]:
        # Consultamos SAACXC directamente porque es donde vive el saldo
        stmt = select(SaAcxc).where(
            and_(
                SaAcxc.CodClie == cliente_id,
                SaAcxc.Saldo > 0
            )
        )
        result = await self.session.execute(stmt)
        cxc_records = result.scalars().all()
        
        facturas = []
        for cxc in cxc_records:
            # Podríamos hacer join con SAFACT para más detalles si fuera necesario
            facturas.append(Factura(
                numero=cxc.NumeroD,
                tipo="FAC", # Asumimos FAC, idealmente SAACXC tiene TipoDoc
                sucursal=cxc.CodSucu,
                cliente_id=cxc.CodClie,
                monto_total=cxc.Monto,
                saldo_pendiente=cxc.Saldo,
                fecha_emision=cxc.FechaE,
                fecha_vencimiento=cxc.FechaV
            ))
            
        return facturas
