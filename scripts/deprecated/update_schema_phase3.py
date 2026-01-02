import asyncio
from sqlalchemy import text
from app.infrastructure.database.session import engine

async def update_schema_phase3():
    async with engine.begin() as conn:
        print("--- Creando nuevas tablas para la Fase 3 ---")
        
        # 1. Tabla BankMapping
        sql_mapping = """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'BankMapping' AND schema_id = SCHEMA_ID('dbo'))
        BEGIN
            CREATE TABLE [dbo].[BankMapping] (
                [id] INT IDENTITY(1,1) PRIMARY KEY,
                [portal_code] VARCHAR(50) NOT NULL UNIQUE,
                [erp_code] VARCHAR(30) NOT NULL,
                [description] VARCHAR(100) NULL,
                [updated_at] DATETIME NULL
            );
            PRINT 'Tabla BankMapping creada.';
        END
        """
        await conn.execute(text(sql_mapping))

        # 2. Tabla ExchangeRates
        sql_rates = """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ExchangeRates' AND schema_id = SCHEMA_ID('dbo'))
        BEGIN
            CREATE TABLE [dbo].[ExchangeRates] (
                [id] INT IDENTITY(1,1) PRIMARY KEY,
                [fecha] DATETIME NOT NULL,
                [moneda_origen] VARCHAR(5) NOT NULL,
                [moneda_destino] VARCHAR(5) NOT NULL,
                [tasa] DECIMAL(28, 8) NOT NULL,
                [created_at] DATETIME NOT NULL
            );
            PRINT 'Tabla ExchangeRates creada.';
        END
        """
        await conn.execute(text(sql_rates))

        # 3. Configuración TASA_SOURCE
        sql_config = """
        IF NOT EXISTS (SELECT * FROM [dbo].[SystemConfig] WHERE [key] = 'TASA_SOURCE')
        BEGIN
            INSERT INTO [dbo].[SystemConfig] ([key], [value], [description], [updated_at])
            VALUES ('TASA_SOURCE', 'JSON', 'Fuente de las tasas: JSON o DATABASE', GETDATE());
            PRINT 'Configuración TASA_SOURCE añadida.';
        END
        """
        await conn.execute(text(sql_config))

if __name__ == "__main__":
    asyncio.run(update_schema_phase3())
