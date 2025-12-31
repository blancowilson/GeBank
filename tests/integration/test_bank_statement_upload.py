import pytest
import os
from httpx import AsyncClient
from app.main import app
from app.infrastructure.database.session import AsyncSessionLocal
from app.infrastructure.database.models import StagingBancos
from sqlalchemy import select, delete
from decimal import Decimal
import pandas as pd
import io

@pytest.fixture(scope="module")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c

@pytest.fixture(autouse=True)
async def cleanup_db():
    async with AsyncSessionLocal() as session:
        await session.execute(delete(StagingBancos))
        await session.commit()
    yield

def create_banesco_excel_file() -> bytes:
    """Creates an in-memory Excel file that mimics the Banesco format with header at row 10."""
    df = pd.DataFrame({
        'Fecha': ['2023-10-01', '2023-10-02'],
        'Descripción': ['Pago a proveedor', 'Abono de nómina'],
        'Referencia': ['REF001', 'REF002'],
        'Monto Débito': [Decimal("150.75"), Decimal("0")],
        'Monto Crédito': [Decimal("0"), Decimal("5000.00")],
        'Saldo': [Decimal("1000.00"), Decimal("6000.00")]
    })
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write 9 empty rows first (optional, as read_excel header=9 handles it)
        # Or, just write the dataframe starting at row 9 (index 9)
        # This makes the df_data's header appear at the 10th row of the Excel file.
        df.to_excel(writer, sheet_name='Sheet1', startrow=9, index=False, header=True)
    return output.getvalue()

@pytest.mark.asyncio
async def test_upload_banesco_statement(client: AsyncClient):
    # 1. Create the fake Excel file content
    file_content = create_banesco_excel_file()
    
    # 2. Prepare the multipart form data
    files = {'file': ('test_banesco.xlsx', file_content, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
    data = {'bank_id': 'banesco'}

    # 3. Make the request
    response = await client.post("/bancos/upload", data=data, files=files)
    
    # 4. Assert the response
    assert response.status_code == 200
    assert "Vista Previa de Resultados" in response.text
    assert "test_banesco.xlsx" in response.text

    # 5. Verify the data was written to the staging table
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(StagingBancos))
        staging_txns = result.scalars().all()
        assert len(staging_txns) == 2
        
        debit_txn = next((t for t in staging_txns if t.tipo_movimiento == 'DEBITO'), None)
        assert debit_txn is not None
        assert debit_txn.referencia == 'REF001'
        assert debit_txn.monto == Decimal("150.75")
        
        credit_txn = next((t for t in staging_txns if t.tipo_movimiento == 'CREDITO'), None)
        assert credit_txn is not None
        assert credit_txn.referencia == 'REF002'
        assert credit_txn.monto == Decimal("5000.00")
