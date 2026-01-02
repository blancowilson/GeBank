import asyncio
from sqlalchemy import text
from app.infrastructure.database.session import engine

async def add_currency_to_mapping():
    async with engine.begin() as conn:
        print("--- Añadiendo columna 'currency' a BankMapping ---")
        try:
            await conn.execute(text("ALTER TABLE [dbo].[BankMapping] ADD currency VARCHAR(5) DEFAULT 'USD' NOT NULL"))
            print("Columna 'currency' añadida correctamente.")
        except Exception as e:
            print(f"Nota: 'currency' podría ya existir o hubo un error: {e}")

if __name__ == "__main__":
    asyncio.run(add_currency_to_mapping())
