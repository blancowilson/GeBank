from pydantic import BaseModel
from typing import List
from datetime import datetime
from decimal import Decimal

class FacturaDTO(BaseModel):
    numero: str
    tipo: str
    monto_total: Decimal
    saldo_pendiente: Decimal
    fecha_emision: datetime
    antiguedad_dias: int

class CXCClienteDTO(BaseModel):
    id: str
    descripcion: str
    rif: str
    saldo_total_ves: Decimal
    saldo_total_usd: Decimal
    facturas_pendientes: List[FacturaDTO]
