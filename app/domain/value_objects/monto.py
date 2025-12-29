from enum import Enum
from decimal import Decimal
from pydantic import BaseModel, field_validator

class Moneda(str, Enum):
    VES = "VES"
    USD = "USD"

class Monto(BaseModel):
    valor: Decimal
    moneda: Moneda

    @field_validator('valor')
    @classmethod
    def valor_positivo(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("El monto no puede ser negativo")
        return v

    def __add__(self, other: 'Monto') -> 'Monto':
        if self.moneda != other.moneda:
            raise ValueError("No se pueden sumar montos de diferentes monedas directamente")
        return Monto(valor=self.valor + other.valor, moneda=self.moneda)

    def __sub__(self, other: 'Monto') -> 'Monto':
        if self.moneda != other.moneda:
            raise ValueError("No se pueden restar montos de diferentes monedas directamente")
        return Monto(valor=self.valor - other.valor, moneda=self.moneda)
