from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.domain.value_objects.monto import Monto

class Pago(BaseModel):
    id: Optional[int] = None
    factura_numero: str
    cliente_id: str
    monto: Monto
    fecha: datetime
    referencia: str
    banco_id: Optional[str] = None
    usuario: str
    
    class Config:
        from_attributes = True
