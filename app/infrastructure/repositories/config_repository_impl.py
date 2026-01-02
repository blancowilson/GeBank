from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from app.domain.repositories.config_repository import IConfigRepository
from app.infrastructure.database.models import SystemConfig
from datetime import datetime

class ConfigRepositoryImpl(IConfigRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_config(self, key: str) -> Optional[str]:
        stmt = select(SystemConfig.value).where(SystemConfig.key == key)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def set_config(self, key: str, value: str) -> None:
        # Intentar actualizar
        stmt = update(SystemConfig).where(SystemConfig.key == key).values(
            value=value,
            updated_at=datetime.now()
        )
        result = await self.session.execute(stmt)
        
        if result.rowcount == 0:
            # Si no existe, insertar
            stmt_ins = insert(SystemConfig).values(
                key=key,
                value=value,
                updated_at=datetime.now()
            )
            await self.session.execute(stmt_ins)
        
        await self.session.commit()
