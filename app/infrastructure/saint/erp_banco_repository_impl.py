from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domain.repositories.banco_repository import BancoRepository
from app.domain.entities.banco import Banco
from app.infrastructure.database.models import SaBanc

class ERPBancoRepositoryImpl(BancoRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> List[Banco]:
        stmt = select(SaBanc)
        result = await self.session.execute(stmt)
        bancos_db = result.scalars().all()
        
        return [
            Banco(
                id=banco.CodBanc,
                descripcion=banco.descripcion,
                activo=True # Assuming all are active for now
            )
            for banco in bancos_db
        ]