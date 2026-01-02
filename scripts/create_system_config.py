import asyncio
from sqlalchemy import text
from app.infrastructure.database.session import engine

async def create_config_table():
    async with engine.begin() as conn:
        print("--- Creando tabla SystemConfig ---")
        sql = """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'SystemConfig' AND schema_id = SCHEMA_ID('dbo'))
        BEGIN
            CREATE TABLE [dbo].[SystemConfig] (
                [key] VARCHAR(50) NOT NULL PRIMARY KEY,
                [value] VARCHAR(255) NULL,
                [description] VARCHAR(255) NULL,
                [updated_at] DATETIME NULL
            );
            PRINT 'Tabla SystemConfig creada.';
            
            -- Insertar valores por defecto
            INSERT INTO [dbo].[SystemConfig] ([key], [value], [description], [updated_at]) VALUES
            ('BASE_CURRENCY', 'USD', 'Moneda base del sistema', GETDATE()),
            ('REF_CURRENCY', 'VES', 'Moneda referencial', GETDATE()),
            ('RATE_OPERATOR', 'MULTIPLY', 'Operador para convertir Base -> Ref (MULTIPLY/DIVIDE)', GETDATE()),
            ('RECONCILIATION_TOLERANCE', '0.01', 'Tolerancia permitida en diferencias de céntimos', GETDATE());
            PRINT 'Valores por defecto insertados.';
        END
        ELSE
        BEGIN
            PRINT 'La tabla SystemConfig ya existe.';
        END
        """
        await conn.execute(text(sql))

if __name__ == "__main__":
    asyncio.run(create_config_table())
