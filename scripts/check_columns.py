import asyncio
from sqlalchemy import text
from app.infrastructure.database.session import engine

async def check_columns():
    async with engine.connect() as conn:
        print("--- Columnas en dbo.GePagos ---")
        sql = """
        SELECT COLUMN_NAME, DATA_TYPE 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'GePagos' AND TABLE_SCHEMA = 'dbo'
        """
        result = await conn.execute(text(sql))
        for row in result:
            print(f"Columna: {row.COLUMN_NAME} ({row.DATA_TYPE})")

if __name__ == "__main__":
    asyncio.run(check_columns())
