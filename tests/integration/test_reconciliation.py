import pytest
from httpx import AsyncClient
from app.main import app
from app.infrastructure.database.session import AsyncSessionLocal
from app.infrastructure.database.models import GePagos, GeDocumentos, GeInstrumentos, StagingBancos, SaClie, BankMapping
from sqlalchemy import delete, select
from datetime import datetime
from decimal import Decimal
from app.infrastructure.tasks.celery_app import celery_app

@pytest.fixture(scope="module", autouse=True)
def setup_celery():
    celery_app.conf.update(
        task_always_eager=True,
        task_store_eager_result=True
    )
    yield
    celery_app.conf.update(task_always_eager=False)

@pytest.fixture(scope="module")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c

@pytest.fixture(autouse=True)
async def setup_and_cleanup_db():
    async with AsyncSessionLocal() as session:
        # Clean
        await session.execute(delete(GeInstrumentos))
        await session.execute(delete(GeDocumentos))
        await session.execute(delete(GePagos))
        await session.execute(delete(StagingBancos))
        await session.execute(delete(BankMapping))
        await session.execute(delete(SaClie).where(SaClie.CodClie == "RECON_CLIENT"))
        await session.commit()
        
        # Setup
        session.add(SaClie(CodClie="RECON_CLIENT", Descrip="Client", ID3="V999", tipoid3=1, Pais=1, Estado=1, Ciudad=1, Municipio=1, TipoCli=1, LimiteCred=Decimal(0), DiasCred=0, Descto=Decimal(0), Saldo=Decimal(0), SaldoPtos=Decimal(0), Activo=1))
        session.add(BankMapping(portal_code="B_01", erp_code="110201", currency="USD", is_cash=0)) 
        session.add(GePagos(idPago="R_01", codCliente="RECON_CLIENT", DescripClie="Recon Client", Usuario="testuser", fecha=datetime.now(), MontoPago=Decimal("1500.00"), MontoCancelado=Decimal("1500.00"), status=1, fechaCaptura=datetime.now()))
        session.add(GeInstrumentos(idPago="R_01", formaPago="TRANSFERENCIA", nroPlanilla="M_01", monto=Decimal("1500.00"), moneda="USD", banco="B_01", fecha=datetime.now()))
        session.add(StagingBancos(cod_banco="110201", referencia="M_01", monto=Decimal("1500.00"), moneda="USD", tipo_movimiento="CREDITO", fecha=datetime.now()))
        await session.commit()
        
    yield
    
    async with AsyncSessionLocal() as session:
        await session.execute(delete(GeInstrumentos))
        await session.execute(delete(GeDocumentos))
        await session.execute(delete(GePagos))
        await session.execute(delete(StagingBancos))
        await session.execute(delete(BankMapping))
        await session.execute(delete(SaClie).where(SaClie.CodClie == "RECON_CLIENT"))
        await session.commit()

@pytest.mark.asyncio
async def test_reconciliation_success(client: AsyncClient):
    response = await client.post("/reconciliation/attempt/R_01")
    assert response.status_code == 200
    
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(GePagos).where(GePagos.idPago == "R_01"))
        pago = res.scalar_one()
        assert pago.status == 3 # APROBADO