import asyncio
from sqlalchemy import text
from app.infrastructure.database.session import engine

async def add_tolerance_config():
    async with engine.begin() as conn:
        sql = """
        IF NOT EXISTS (SELECT * FROM [dbo].[SystemConfig] WHERE [key] = 'RECONCILIATION_TOLERANCE')
        BEGIN
            INSERT INTO [dbo].[SystemConfig] ([key], [value], [description], [updated_at])
            VALUES ('RECONCILIATION_TOLERANCE', '0.01', 'Tolerancia permitida en diferencias de céntimos', GETDATE());
            PRINT 'Configuración de tolerancia añadida.';
        END
        """
        await conn.execute(text(sql))

if __name__ == "__main__":
    asyncio.run(add_tolerance_config())
