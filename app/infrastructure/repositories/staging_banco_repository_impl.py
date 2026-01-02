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

    async def find_candidates(
        self, 
        amount: Decimal, 
        date_ref, 
        bank_code: Optional[str] = None, 
        tolerance_days: int = 5, 
        tolerance_amount: Decimal = Decimal("0.50")
    ) -> List[StagingTransaction]:
        """
        Busca transacciones candidatas en Staging para conciliación manual.
        Filtra por:
        - Rango de fechas (+/- tolerance_days)
        - Rango de monto (+/- tolerance_amount)
        - Banco (si se especifica)
        - Estatus PENDIENTE
        """
        from datetime import timedelta
        
        date_start = date_ref - timedelta(days=tolerance_days)
        date_end = date_ref + timedelta(days=tolerance_days)
        
        min_amount = amount - tolerance_amount
        max_amount = amount + tolerance_amount
        
        stmt = select(StagingBancos).where(
            StagingBancos.estatus == StagingTransaction.PENDIENTE,
            StagingBancos.fecha >= date_start,
            StagingBancos.fecha <= date_end,
            StagingBancos.monto >= min_amount,
            StagingBancos.monto <= max_amount
        )
        
        if bank_code:
            stmt = stmt.where(StagingBancos.cod_banco == bank_code)
            
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

    async def buscar_por_id(self, id: int) -> Optional[StagingTransaction]:
        stmt = select(StagingBancos).where(StagingBancos.id == id)
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

    async def actualizar_staging(self, staging: StagingTransaction) -> None:
        from sqlalchemy import update
        stmt = update(StagingBancos).where(StagingBancos.id == staging.id).values(
            estatus=staging.estatus
        )
        await self.session.execute(stmt)
        await self.session.commit()
