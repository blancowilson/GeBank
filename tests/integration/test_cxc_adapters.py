import pytest
from app.infrastructure.saint.saint_cliente_repository import SaintClienteRepository
from app.infrastructure.saint.saint_pago_repository import SaintPagoRepository
from app.infrastructure.database.session import AsyncSessionLocal

@pytest.mark.asyncio
async def test_cliente_repository_instantiation():
    async with AsyncSessionLocal() as session:
        repo = SaintClienteRepository(session)
        assert repo is not None

@pytest.mark.asyncio
async def test_pago_repository_instantiation():
    async with AsyncSessionLocal() as session:
        repo = SaintPagoRepository(session)
        assert repo is not None
