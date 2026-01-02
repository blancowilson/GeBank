import asyncio
from sqlalchemy import text
from app.infrastructure.database.session import engine

async def check_all_columns():
    async with engine.connect() as conn:
        for table in ['GePagos', 'GeDocumentos', 'GeInstrumentos', 'Staging_Bancos']:
            print(f"--- Columnas en dbo.{table} ---")
            sql = f"""
            SELECT COLUMN_NAME, DATA_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = '{table}' AND TABLE_SCHEMA = 'dbo'
            """
            result = await conn.execute(text(sql))
            for row in result:
                print(f"Columna: {row.COLUMN_NAME} ({row.DATA_TYPE})")
            print()

if __name__ == "__main__":
    asyncio.run(check_all_columns())
