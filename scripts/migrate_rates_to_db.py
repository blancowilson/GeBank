import asyncio
import json
import os
from datetime import datetime
from decimal import Decimal
from sqlalchemy import insert
from app.infrastructure.database.session import AsyncSessionLocal
from app.infrastructure.database.models import ExchangeRate

async def migrate_rates():
    json_path = "config/tasas.json"
    if not os.path.exists(json_path):
        print(f"Archivo {json_path} no encontrado. Saltando migración.")
        return

    with open(json_path, 'r') as f:
        data = json.load(f)

    async with AsyncSessionLocal() as session:
        print(f"--- Migrando tasas desde {json_path} a la base de datos ---")
        
        for item in data:
            # Traducir campos del JSON al modelo
            # JSON usa: moneda_origen, moneda_destino, tasa, fecha_vigencia
            
            fecha_vigencia = datetime.fromisoformat(item['fecha_vigencia']) if item.get('fecha_vigencia') else datetime.now()
            
            new_rate = ExchangeRate(
                fecha=fecha_vigencia,
                moneda_origen=item['moneda_origen'],
                moneda_destino=item['moneda_destino'],
                tasa=Decimal(str(item['valor'])),
                created_at=datetime.now()
            )
            session.add(new_rate)
        
        await session.commit()
        print("Migración completada exitosamente.")

if __name__ == "__main__":
    asyncio.run(migrate_rates())
