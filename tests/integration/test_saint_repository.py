import pytest
from app.infrastructure.database.session import AsyncSessionLocal
from app.infrastructure.saint.erp_factura_repository_impl import ERPFacturaRepositoryImpl

@pytest.mark.asyncio
async def test_factura_repository_instantiation():
    async with AsyncSessionLocal() as session:
        repo = ERPFacturaRepositoryImpl(session)
        assert repo is not None
