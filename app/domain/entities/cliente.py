from typing import Optional
from pydantic import BaseModel
from app.domain.value_objects.monto import Monto, Moneda
from decimal import Decimal

class Cliente(BaseModel):
    id: str
    descripcion: str
    rif: Optional[str] = None
    saldo_ves: Monto = Monto(valor=Decimal("0.00"), moneda=Moneda.VES)
    saldo_usd: Monto = Monto(valor=Decimal("0.00"), moneda=Moneda.USD)
    activo: bool = True

    class Config:
        from_attributes = True
