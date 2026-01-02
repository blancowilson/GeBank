import pytest
import pytest
from app.infrastructure.database.session import AsyncSessionLocal
from app.infrastructure.saint.erp_cliente_repository_impl import ERPClienteRepositoryImpl
from app.infrastructure.saint.erp_pago_repository_impl import ERPPagoRepositoryImpl

@pytest.mark.asyncio
async def test_cliente_repository_instantiation():
    async with AsyncSessionLocal() as session:
        repo = ERPClienteRepositoryImpl(session)
        assert repo is not None

@pytest.mark.asyncio
async def test_pago_repository_instantiation():
    async with AsyncSessionLocal() as session:
        repo = ERPPagoRepositoryImpl(session)
        assert repo is not None
