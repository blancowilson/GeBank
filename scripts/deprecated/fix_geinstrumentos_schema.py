import asyncio
from sqlalchemy import text
from app.infrastructure.database.session import engine

async def fix_geinstrumentos_schema():
    async with engine.begin() as conn:
        print("--- Añadiendo columna 'moneda' a GeInstrumentos ---")
        try:
            await conn.execute(text("ALTER TABLE [dbo].[GeInstrumentos] ADD moneda VARCHAR(5) DEFAULT 'USD' NOT NULL"))
            print("Columna 'moneda' añadida correctamente.")
        except Exception as e:
            print(f"Nota: 'moneda' podría ya existir: {e}")

if __name__ == "__main__":
    asyncio.run(fix_geinstrumentos_schema())
