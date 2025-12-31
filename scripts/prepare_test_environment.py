import asyncio
import pandas as pd
import io
from sqlalchemy import select
from app.infrastructure.database.session import engine, AsyncSessionLocal
from app.infrastructure.database.models import SaBanc
from decimal import Decimal

async def seed_saint_bank():
    """Crea el banco Banesco en SBBANC si no existe"""
    async with AsyncSessionLocal() as session:
        # Verificar si existe
        stmt = select(SaBanc).where(SaBanc.CodBanc == "BANESCO")
        result = await session.execute(stmt)
        bank = result.scalar_one_or_none()

        if not bank:
            print("Creating 'BANESCO' in SBBANC table...")
            new_bank = SaBanc(
                CodBanc="BANESCO",
                descripcion="Banesco Banco Universal",
                Ciudad=1,
                Estado=1,
                Pais=1,
                SaldoAct=Decimal("0.00"),
                SaldoC1=Decimal("0.00"),
                SaldoC2=Decimal("0.00")
            )
            session.add(new_bank)
            await session.commit()
            print("Bank 'BANESCO' created successfully.")
        else:
            print("Bank 'BANESCO' already exists in SBBANC.")

def create_excel_file():
    """Genera un archivo Excel físico para probar la carga"""
    filename = "test_banesco_real.xlsx"
    
    # Datos simulados
    data = {
        'Fecha': ['2023-12-01', '2023-12-02', '2023-12-03'],
        'Descripción': ['TRANSFERENCIA DE CLIENTE A', 'PAGO NOMINA', 'DEPOSITO EFECTIVO'],
        'Referencia': ['123456', '999888', '777111'],
        'Monto Débito': [0, 500.00, 0],
        'Monto Crédito': [1200.50, 0, 50.00],
        'Saldo': [1200.50, 700.50, 750.50]
    }
    df = pd.DataFrame(data)

    # Crear el Excel con el formato esperado (Header en fila 10 -> index 9)
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', startrow=9, index=False)
    
    print(f"Test file created: {filename}")

if __name__ == "__main__":
    # 1. Seed DB
    loop = asyncio.get_event_loop()
    loop.run_until_complete(seed_saint_bank())
    
    # 2. Create File
    create_excel_file()
