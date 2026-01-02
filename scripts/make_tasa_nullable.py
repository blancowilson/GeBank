import asyncio
from sqlalchemy import text
from app.infrastructure.database.session import engine

async def make_tasa_nullable():
    async with engine.begin() as conn:
        print("--- Haciendo 'tasa' nullable en GeInstrumentos ---")
        try:
            # SQL Server syntax to alter column
            await conn.execute(text("ALTER TABLE [dbo].[GeInstrumentos] ALTER COLUMN tasa DECIMAL(28, 4) NULL"))
            print("Columna 'tasa' ahora es nullable.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(make_tasa_nullable())
