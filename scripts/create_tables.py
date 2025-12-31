import asyncio
from sqlalchemy import text
from app.infrastructure.database.session import engine
from app.infrastructure.database.models import Base

async def create_tables():
    async with engine.begin() as conn:
        # 1. Create Schema 'AppConciliacion' if not exists
        # MSSQL syntax: IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'AppConciliacion') EXEC('CREATE SCHEMA [AppConciliacion]')
        try:
            await conn.execute(text("IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'AppConciliacion') EXEC('CREATE SCHEMA [AppConciliacion]')"))
            print("Schema 'AppConciliacion' ensured.")
        except Exception as e:
            print(f"Warning creating schema: {e}")

        # 2. Create all tables defined in Base.metadata
        await conn.run_sync(Base.metadata.create_all)
        
    print("Tables created successfully.")

if __name__ == "__main__":
    asyncio.run(create_tables())