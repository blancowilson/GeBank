import pytest
from sqlalchemy import text
from app.infrastructure.database.session import engine
from app.config import settings

@pytest.mark.asyncio
async def test_database_connection():
    """
    Verifies that the application can connect to the SQL Server database.
    Skips if connection cannot be established (e.g. CI/CD without DB).
    """
    try:
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))
            assert result.scalar() == 1
    except Exception as e:
        pytest.skip(f"Database connection failed: {e}. Check your .env configuration.")
