import asyncio
from sqlalchemy import text
from app.infrastructure.database.session import engine

async def update_mapping_schema():
    async with engine.begin() as conn:
        print("--- Actualizando esquema de BankMapping ---")
        
        # Añadir columna is_cash
        try:
            await conn.execute(text("ALTER TABLE [dbo].[BankMapping] ADD is_cash BIT DEFAULT 0 NOT NULL"))
            print("Columna 'is_cash' añadida correctamente.")
        except Exception as e:
            print(f"Nota: 'is_cash' podría ya existir o hubo un error: {e}")

if __name__ == "__main__":
    asyncio.run(update_mapping_schema())
