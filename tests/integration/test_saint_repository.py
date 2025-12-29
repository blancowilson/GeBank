import pytest
from app.infrastructure.saint.saint_factura_repository import SaintFacturaRepository
from app.infrastructure.database.session import engine, AsyncSessionLocal

@pytest.mark.asyncio
async def test_factura_repository_instantiation():
    """
    Verifica que el repositorio se puede instanciar y que el código es válido.
    No intenta conectar a BD si no hay entorno real.
    """
    async with AsyncSessionLocal() as session:
        repo = SaintFacturaRepository(session)
        assert repo is not None
        assert repo.session is session
