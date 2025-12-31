import pytest
from httpx import AsyncClient
from app.main import app
from app.infrastructure.database.session import AsyncSessionLocal
from app.infrastructure.database.models import GePagos, GeDocumentos, GeInstrumentos, StagingBancos, SaClie
from sqlalchemy import delete
from datetime import datetime
from decimal import Decimal

@pytest.fixture(scope="module")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c

@pytest.fixture(autouse=True)
async def setup_and_cleanup_db():
    async with AsyncSessionLocal() as session:
        # Clean before test
        await session.execute(delete(GeInstrumentos))
        await session.execute(delete(GeDocumentos))
        await session.execute(delete(GePagos))
        await session.execute(delete(StagingBancos))
        await session.execute(delete(SaClie).where(SaClie.CodClie == "RECON_CLIENT"))
        await session.commit()
        
        # Setup test data
        session.add(SaClie(CodClie="RECON_CLIENT", Descrip="Client for Reconciliation Test", ID3="V999", tipoid3=1, Pais=1, Estado=1, Ciudad=1, Municipio=1, TipoCli=1, LimiteCred=Decimal(0), DiasCred=0, Descto=Decimal(0), Saldo=Decimal(0), SaldoPtos=Decimal(0), Activo=1))
        
        session.add(GePagos(idPago="RECON001", codCliente="RECON_CLIENT", DescripClie="Recon Client", Usuario="testuser", fecha=datetime.now(), MontoPago=Decimal("1500.00"), MontoCancelado=Decimal("1500.00"), status=1, fechaCaptura=datetime.now()))
        
        session.add(GeInstrumentos(idPago="RECON001", formaPago="TRANSFERENCIA", nroPlanilla="MATCH_REF_001", monto=Decimal("1500.00"), moneda="USD", banco="BANESCO", fecha=datetime.now()))

        session.add(StagingBancos(cod_banco="BANESCO", referencia="MATCH_REF_001", monto=Decimal("1500.00"), moneda="USD", tipo_movimiento="CREDITO", fecha=datetime.now()))
        
        await session.commit()
        
    yield
    
    # Teardown
    async with AsyncSessionLocal() as session:
        await session.execute(delete(GeInstrumentos))
        await session.execute(delete(GeDocumentos))
        await session.execute(delete(GePagos))
        await session.execute(delete(StagingBancos))
        await session.execute(delete(SaClie).where(SaClie.CodClie == "RECON_CLIENT"))
        await session.commit()

@pytest.mark.asyncio
async def test_reconciliation_success(client: AsyncClient):
    # 1. Make the request to reconcile the payment
    response = await client.post("/reconciliation/attempt/RECON001")
    
    # 2. Assert the response
    assert response.status_code == 200
    assert "Match Encontrado" in response.text
    assert "Pago Reportado" in response.text
    assert "ID: RECON001" in response.text
    assert "1500.00 USD" in response.text
    
    # Verify that the final status is "Conciliado"
    assert "Conciliado" in response.text
