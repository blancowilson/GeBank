import asyncio
from sqlalchemy import text
from app.infrastructure.database.session import get_db

async def update_schema():
    print("--- Actualizando esquema de Tasas (Sprint 3.5) ---")
    
    async for session in get_db():
        print("Verificando tabla ExchangeRates...")
        try:
            # Check if column exists
            check_col = text("""
                SELECT 1 
                FROM sys.columns 
                WHERE Name = N'tipo_tasa' 
                AND Object_ID = Object_ID(N'dbo.ExchangeRates')
            """)
            result = await session.execute(check_col)
            exists = result.scalar()
            
            if not exists:
                print("Agregando columna 'tipo_tasa' a ExchangeRates...")
                await session.execute(text("ALTER TABLE dbo.ExchangeRates ADD tipo_tasa VARCHAR(20) DEFAULT 'OFICIAL' NOT NULL"))
                await session.commit()
                print("Columna agregada exitosamente.")
            else:
                print("La columna 'tipo_tasa' ya existe.")
                
        except Exception as e:
            print(f"Error actualizando esquema: {e}")
            await session.rollback()
        
        break

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(update_schema())
