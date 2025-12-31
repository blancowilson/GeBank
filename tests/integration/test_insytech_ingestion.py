import pytest
from httpx import AsyncClient
from app.main import app
from app.infrastructure.database.session import AsyncSessionLocal
from app.infrastructure.database.models import GePagos, GeDocumentos, GeInstrumentos, SaClie
from app.domain.entities.pago_insytech import GePagos as DomainGePagos # For status constants
from datetime import datetime
from decimal import Decimal
from sqlalchemy import select, delete
from fastapi import status

@pytest.fixture(scope="module")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c

@pytest.fixture(autouse=True)
async def cleanup_db():
    async with AsyncSessionLocal() as session:
        # Create a dummy client to satisfy FK constraint if needed
        # In a real test setup, you'd manage test data more robustly
        dummy_client = await session.execute(select(SaClie).where(SaClie.CodClie == "TESTCLIENT"))
        if not dummy_client.scalar_one_or_none():
            session.add(SaClie(
                CodClie="TESTCLIENT",
                Descrip="Test Client",
                ID3="V123456789",
                tipoid3=1,
                Pais=1,
                Estado=1,
                Ciudad=1,
                Municipio=1,
                Telef="000",
                Email="test@test.com",
                TipoCli=1,
                LimiteCred=Decimal("0.00"),
                DiasCred=0,
                Descto=Decimal("0.00"),
                Saldo=Decimal("0.00"),
                SaldoPtos=Decimal("0.00"),
                Activo=1
            ))
            await session.commit()

        yield
        # Clean up GePagos and related tables after each test
        await session.execute(delete(GeInstrumentos))
        await session.execute(delete(GeDocumentos))
        await session.execute(delete(GePagos))
        await session.execute(delete(SaClie).where(SaClie.CodClie == "TESTCLIENT")) # Clean up dummy client
        await session.commit()

@pytest.mark.asyncio
async def test_receive_insytech_payment(client: AsyncClient):
    # Prepare test data
    packet_data = {
        "idPago": "INSY001",
        "codCliente": "TESTCLIENT",
        "DescripClie": "Test Client",
        "Usuario": "vendedor1",
        "fecha": datetime.now().isoformat(),
                                            "MontoPago": "1040.00", # Corrected to match sum of components (1000 from instrs + 40 from doc discounts)
                                            "MontoCancelado": "950.00",        "status": 0, # Should map to GePagos.PENDIENTE (1)
        "UrlImagen": "http://example.com/img1.jpg",
        "documentos": [
            {
                "numeroDoc": "FAC001",
                "tipoDoc": "FACT",
                "emision": datetime.now().isoformat(),
                "vencimiento": datetime.now().isoformat(),
                "montoDoc": "800.00",
                "porcentajeDescuento": "5.00",
                "montoDescuento": "40.00",
                "porcentajeRetencion": "0.00",
                "montoRetencion": "0.00"
            },
            {
                "numeroDoc": "NC001",
                "tipoDoc": "N/E",
                "emision": datetime.now().isoformat(),
                "vencimiento": datetime.now().isoformat(),
                "montoDoc": "200.00", # This is a credit note, reducing montoDoc
                "porcentajeDescuento": "0.00",
                "montoDescuento": "0.00",
                "porcentajeRetencion": "0.00",
                "montoRetencion": "0.00"
            }
        ],
        "instrumentos": [
            {
                "formaPago": "TRANSFERENCIA",
                "nroPlanilla": "BANKREF123",
                "fecha": datetime.now().isoformat(),
                "monto": "960.00",
                "moneda": "USD",
                "banco": "Banco XYZ",
                "bancoCliente": "Cliente Bank"
            },
            {
                "formaPago": "EFECTIVO",
                "nroPlanilla": "CASH001",
                "fecha": datetime.now().isoformat(),
                "monto": "40.00",
                "moneda": "USD"
            }
        ]
    }

    response = await client.post("/api/v1/integration/payments", json=packet_data)
    print(response.json()) # Debugging line
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"message": "Payment packet received and persisted successfully", "idPago": "INSY001"}

    # Verify data in DB
    async with AsyncSessionLocal() as session:
        # Check GePagos
        db_pago = await session.execute(select(GePagos).where(GePagos.idPago == "INSY001"))
        pago = db_pago.scalar_one_or_none()
        assert pago is not None
        assert pago.codCliente == "TESTCLIENT"
        assert pago.MontoPago == Decimal("1040.00")
        assert pago.status == DomainGePagos.PENDIENTE # Mapped from 0 to 1

        # Check GeDocumentos
        db_docs = await session.execute(select(GeDocumentos).where(GeDocumentos.idPago == "INSY001"))
        docs = db_docs.scalars().all()
        assert len(docs) == 2
        assert any(d.numeroDoc == "FAC001" for d in docs)
        assert any(d.numeroDoc == "NC001" for d in docs)
        
        fac001_doc = next(d for d in docs if d.numeroDoc == "FAC001")
        assert fac001_doc.montoDoc == Decimal("800.00")
        assert fac001_doc.montoDescuento == Decimal("40.00")

        # Check GeInstrumentos
        db_instrs = await session.execute(select(GeInstrumentos).where(GeInstrumentos.idPago == "INSY001"))
        instrs = db_instrs.scalars().all()
        assert len(instrs) == 2
        assert any(i.formaPago == "TRANSFERENCIA" for i in instrs)
        assert any(i.formaPago == "EFECTIVO" for i in instrs)
        
        transfer_instr = next(i for i in instrs if i.formaPago == "TRANSFERENCIA")
        assert transfer_instr.monto == Decimal("960.00")
        assert transfer_instr.moneda == "USD"
        assert transfer_instr.nroPlanilla == "BANKREF123"

@pytest.mark.asyncio
async def test_receive_insytech_payment_client_not_found(client: AsyncClient):
    packet_data = {
        "idPago": "INSY002",
        "codCliente": "NONEXISTENT", # This client should not exist
        "DescripClie": "Non Existent Client",
        "Usuario": "vendedor1",
        "fecha": datetime.now().isoformat(),
        "MontoPago": "100.00",
        "MontoCancelado": "100.00",
        "status": 0,
        "documentos": [
            {
                "numeroDoc": "FAC002", "tipoDoc": "FACT", "emision": datetime.now().isoformat(),
                "vencimiento": datetime.now().isoformat(), "montoDoc": "100.00",
                "porcentajeDescuento": "0.00", "montoDescuento": "0.00",
                "porcentajeRetencion": "0.00", "montoRetencion": "0.00"
            }
        ],
        "instrumentos": [
            {
                "formaPago": "EFECTIVO", "fecha": datetime.now().isoformat(),
                "monto": "100.00", "moneda": "USD"
            }
        ]
    }
    response = await client.post("/api/v1/integration/payments", json=packet_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Cliente con código NONEXISTENT no encontrado." in response.json()["detail"]

@pytest.mark.asyncio
async def test_receive_insytech_payment_integrity_fail(client: AsyncClient):
    packet_data = {
        "idPago": "INSY003",
        "codCliente": "TESTCLIENT", 
        "DescripClie": "Test Client",
        "Usuario": "vendedor1",
        "fecha": datetime.now().isoformat(),
        "MontoPago": "1000.00", # Mismatch with sum of instruments/docs
        "MontoCancelado": "950.00",
        "status": 0,
        "documentos": [
            {
                "numeroDoc": "FAC001", "tipoDoc": "FACT", "emision": datetime.now().isoformat(),
                "vencimiento": datetime.now().isoformat(), "montoDoc": "800.00",
                "porcentajeDescuento": "5.00", "montoDescuento": "40.00",
                "porcentajeRetencion": "0.00", "montoRetencion": "0.00"
            }
        ],
        "instrumentos": [
            {
                "formaPago": "TRANSFERENCIA", "nroPlanilla": "BANKREF123", "fecha": datetime.now().isoformat(),
                "monto": "100.00", # Intentionally wrong monto
                "moneda": "USD", "banco": "Banco XYZ", "bancoCliente": "Cliente Bank"
            }
        ]
    }

    response = await client.post("/api/v1/integration/payments", json=packet_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "La suma de los instrumentos y componentes administrativos no coincide con MontoPago." in response.json()["detail"]