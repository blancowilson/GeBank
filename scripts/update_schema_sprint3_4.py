import asyncio
from sqlalchemy import text
from app.infrastructure.database.session import get_db

async def update_schema():
    print("--- Actualizando esquema para Sprint 3.4 ---")
    
    async for session in get_db():
        print("Verificando tabla GeInstrumentos...")
        try:
            # Check if column exists
            # SQL Server specific syntax
            check_col = text("""
                SELECT 1 
                FROM sys.columns 
                WHERE Name = N'estatus' 
                AND Object_ID = Object_ID(N'dbo.GeInstrumentos')
            """)
            result = await session.execute(check_col)
            exists = result.scalar()
            
            if not exists:
                print("Agregando columna 'estatus' a GeInstrumentos...")
                await session.execute(text("ALTER TABLE dbo.GeInstrumentos ADD estatus SMALLINT DEFAULT 0 NOT NULL"))
                await session.commit()
                print("Columna agregada exitosamente.")
            else:
                print("La columna 'estatus' ya existe.")
                
        except Exception as e:
            print(f"Error actualizando esquema: {e}")
            await session.rollback()
        
        break # Run once

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(update_schema())
