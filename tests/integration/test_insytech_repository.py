import pytest
from app.infrastructure.database.session import AsyncSessionLocal
from app.infrastructure.database.models import GePagos
from app.infrastructure.repositories.portal_repository_impl import PortalRepositoryImpl
from sqlalchemy import delete
from datetime import datetime
from decimal import Decimal

@pytest.fixture(autouse=True)
async def setup_and_cleanup_db():
    async with AsyncSessionLocal() as session:
        # Clean before test
        await session.execute(delete(GePagos))
        await session.commit()
        
        # Setup test data
        session.add_all([
            GePagos(idPago="P_01", codCliente="C1", DescripClie="Test 1", Usuario="test", fecha=datetime.now(), MontoPago=Decimal("100"), MontoCancelado=Decimal("100"), status=1, fechaCaptura=datetime.now()),
            GePagos(idPago="A_01", codCliente="C2", DescripClie="Test 2", Usuario="test", fecha=datetime.now(), MontoPago=Decimal("200"), MontoCancelado=Decimal("200"), status=3, fechaCaptura=datetime.now()),
            GePagos(idPago="P_02", codCliente="C3", DescripClie="Test 3", Usuario="test", fecha=datetime.now(), MontoPago=Decimal("300"), MontoCancelado=Decimal("300"), status=1, fechaCaptura=datetime.now())
        ])
        await session.commit()
        
    yield
    
    # Teardown
    async with AsyncSessionLocal() as session:
        await session.execute(delete(GePagos))
        await session.commit()

@pytest.mark.asyncio
async def test_obtener_pagos_por_status():
    async with AsyncSessionLocal() as session:
        repo = PortalRepositoryImpl(session)
        
        # Test fetching PENDIENTE payments
        pagos_pendientes = await repo.obtener_pagos_por_status(1)
        assert len(pagos_pendientes) == 2
        assert {p.idPago for p in pagos_pendientes} == {"P_01", "P_02"}
        
        # Test fetching APROBADO payments
        pagos_aprobados = await repo.obtener_pagos_por_status(3)
        assert len(pagos_aprobados) == 1
        assert pagos_aprobados[0].idPago == "A_01"
        
        # Test fetching a status with no payments
        pagos_otros = await repo.obtener_pagos_por_status(9) # RECHAZADO
        assert len(pagos_otros) == 0
