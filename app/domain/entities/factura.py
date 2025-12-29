from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel

class Factura(BaseModel):
    numero: str
    tipo: str
    sucursal: str
    cliente_id: str
    vendedor_id: Optional[str] = None
    monto_total: Decimal
    saldo_pendiente: Decimal
    fecha_emision: datetime
    fecha_vencimiento: Optional[datetime] = None
    descripcion: Optional[str] = None
    
    class Config:
        from_attributes = True
