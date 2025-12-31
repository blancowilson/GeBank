import pytest
from datetime import datetime
from decimal import Decimal
from app.infrastructure.repositories.staging_banco_repository_impl import StagingBancoRepositoryImpl
from app.domain.entities.staging_transaction import StagingTransaction
from app.infrastructure.database.session import AsyncSessionLocal
from app.infrastructure.database.models import StagingBancos
from sqlalchemy import delete

@pytest.mark.asyncio
async def test_staging_repository_flow():
    async with AsyncSessionLocal() as session:
        repo = StagingBancoRepositoryImpl(session)
        
        # 1. Prepare Data
        txn = StagingTransaction(
            id=None,
            cod_banco="0102",
            referencia="REF123456",
            fecha=datetime.now(),
            monto=Decimal("100.50"),
            moneda="USD",
            tipo_movimiento="CREDITO",
            descripcion="Test Payment",
            nombre_archivo="test.csv"
        )
        
        # 2. Save
        await repo.guardar_lote([txn])
        
        # 3. Retrieve
        found = await repo.buscar_por_referencia_y_monto("REF123456", Decimal("100.50"), "0102")
        
        assert found is not None
        assert found.referencia == "REF123456"
        assert found.monto == Decimal("100.50")
        assert found.moneda == "USD"
        
        # 4. Clean up (Optional, but good practice for integration tests on real DB if not using transactional rollback)
        # Note: If running against a real DB, better to delete created data.
        await session.execute(delete(StagingBancos).where(StagingBancos.referencia == "REF123456"))
        await session.commit()
