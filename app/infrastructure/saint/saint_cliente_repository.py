from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.domain.repositories.cliente_repository import ClienteRepository
from app.domain.entities.cliente import Cliente
from app.domain.value_objects.monto import Monto, Moneda
from app.infrastructure.database.models import SaClie
from decimal import Decimal

class SaintClienteRepository(ClienteRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def obtener_todos(self, skip: int = 0, limit: int = 100) -> List[Cliente]:
        stmt = (
            select(
                SaClie.CodClie,
                SaClie.Descrip,
                SaClie.ID3,
                SaClie.Saldo,
                SaClie.Activo,
            )
            .order_by(SaClie.CodClie)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        sa_clientes = result.all() # Use .all() for tuples
        return [self._map_to_domain(c) for c in sa_clientes]

    async def obtener_por_id(self, cliente_id: str) -> Optional[Cliente]:
        stmt = select(
            SaClie.CodClie, SaClie.Descrip, SaClie.ID3, SaClie.Saldo, SaClie.Activo
        ).where(SaClie.CodClie == cliente_id)
        result = await self.session.execute(stmt)
        sa_cliente = result.first()  # Use .first() for tuple result
        if not sa_cliente:
            return None
        return self._map_to_domain(sa_cliente)

    async def buscar_por_nombre(self, query: str) -> List[Cliente]:
        stmt = select(
            SaClie.CodClie, SaClie.Descrip, SaClie.ID3, SaClie.Saldo, SaClie.Activo
        ).where(
            or_(
                SaClie.Descrip.ilike(f"%{query}%"),
                SaClie.ID3.ilike(f"%{query}%"),
                SaClie.CodClie.ilike(f"%{query}%")
            )
        )
        result = await self.session.execute(stmt)
        sa_clientes = result.all()
        return [self._map_to_domain(c) for c in sa_clientes]

    def _map_to_domain(self, sa_cliente: SaClie) -> Cliente:
        # Note: In Saint, 'Saldo' usually refers to VES. 
        # For multimoneda, we might need more logic later.
        return Cliente(
            id=sa_cliente.CodClie,
            descripcion=sa_cliente.Descrip,
            rif=sa_cliente.ID3,
            saldo_ves=Monto(valor=sa_cliente.Saldo or Decimal("0.00"), moneda=Moneda.VES),
            # Mocking USD balance for now until we have exchange rate logic
            saldo_usd=Monto(valor=Decimal("0.00"), moneda=Moneda.USD),
            activo=sa_cliente.Activo == 1
        )
