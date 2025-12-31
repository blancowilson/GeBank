from typing import List, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domain.entities.staging_transaction import StagingTransaction
from app.domain.repositories.staging_banco_repository import StagingBancoRepository
from app.infrastructure.database.models import StagingBancos

class StagingBancoRepositoryImpl(StagingBancoRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def guardar_lote(self, transacciones: List[StagingTransaction]) -> None:
        db_objs = [
            StagingBancos(
                cod_banco=t.cod_banco,
                referencia=t.referencia,
                fecha=t.fecha,
                monto=t.monto,
                moneda=t.moneda,
                tipo_movimiento=t.tipo_movimiento,
                descripcion=t.descripcion,
                estatus=t.estatus,
                nombre_archivo=t.nombre_archivo
            )
            for t in transacciones
        ]
        self.session.add_all(db_objs)
        await self.session.commit()

    async def buscar_por_referencia_y_monto(self, referencia: str, monto: Decimal, cod_banco: str) -> Optional[StagingTransaction]:
        stmt = select(StagingBancos).where(
            StagingBancos.referencia == referencia,
            StagingBancos.monto == monto,
            StagingBancos.cod_banco == cod_banco
        )
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        
        if row:
            return StagingTransaction(
                id=row.id,
                cod_banco=row.cod_banco,
                referencia=row.referencia,
                fecha=row.fecha,
                monto=row.monto,
                moneda=row.moneda,
                tipo_movimiento=row.tipo_movimiento,
                descripcion=row.descripcion,
                estatus=row.estatus,
                nombre_archivo=row.nombre_archivo
            )
        return None

    async def obtener_pendientes(self, limit: int = 100) -> List[StagingTransaction]:
        stmt = select(StagingBancos).where(
            StagingBancos.estatus == StagingTransaction.PENDIENTE
        ).limit(limit)
        
        result = await self.session.execute(stmt)
        rows = result.scalars().all()
        
        return [
            StagingTransaction(
                id=row.id,
                cod_banco=row.cod_banco,
                referencia=row.referencia,
                fecha=row.fecha,
                monto=row.monto,
                moneda=row.moneda,
                tipo_movimiento=row.tipo_movimiento,
                descripcion=row.descripcion,
                estatus=row.estatus,
                nombre_archivo=row.nombre_archivo
            )
            for row in rows
        ]
