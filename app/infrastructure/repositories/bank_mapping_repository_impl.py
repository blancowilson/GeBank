from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.domain.repositories.bank_mapping_repository import IBankMappingRepository, BankMappingDTO
from app.infrastructure.database.models import BankMapping
from datetime import datetime

class BankMappingRepositoryImpl(IBankMappingRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> List[BankMappingDTO]:
        stmt = select(BankMapping).order_by(BankMapping.portal_code)
        result = await self.session.execute(stmt)
        rows = result.scalars().all()
        return [
            BankMappingDTO(
                id=r.id,
                portal_code=r.portal_code,
                erp_code=r.erp_code,
                description=r.description,
                is_cash=bool(r.is_cash),
                currency=r.currency
            ) for r in rows
        ]

    async def get_by_portal_code(self, portal_code: str) -> Optional[BankMappingDTO]:
        stmt = select(BankMapping).where(BankMapping.portal_code == portal_code)
        result = await self.session.execute(stmt)
        r = result.scalar_one_or_none()
        if r:
            return BankMappingDTO(
                id=r.id,
                portal_code=r.portal_code,
                erp_code=r.erp_code,
                description=r.description,
                is_cash=bool(r.is_cash),
                currency=r.currency
            )
        return None

    async def save(self, mapping: BankMappingDTO) -> BankMappingDTO:
        if mapping.id:
            stmt = select(BankMapping).where(BankMapping.id == mapping.id)
            result = await self.session.execute(stmt)
            db_mapping = result.scalar_one()
            db_mapping.portal_code = mapping.portal_code
            db_mapping.erp_code = mapping.erp_code
            db_mapping.description = mapping.description
            db_mapping.is_cash = 1 if mapping.is_cash else 0
            db_mapping.currency = mapping.currency
            db_mapping.updated_at = datetime.now()
        else:
            db_mapping = BankMapping(
                portal_code=mapping.portal_code,
                erp_code=mapping.erp_code,
                description=mapping.description,
                is_cash=1 if mapping.is_cash else 0,
                currency=mapping.currency,
                updated_at=datetime.now()
            )
            self.session.add(db_mapping)
        
        await self.session.commit()
        await self.session.refresh(db_mapping)
        
        mapping.id = db_mapping.id
        return mapping

    async def delete(self, mapping_id: int) -> None:
        stmt = delete(BankMapping).where(BankMapping.id == mapping_id)
        await self.session.execute(stmt)
        await self.session.commit()
