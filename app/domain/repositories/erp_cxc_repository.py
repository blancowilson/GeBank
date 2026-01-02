from abc import ABC, abstractmethod
from typing import List
from app.domain.entities.factura import Factura
from decimal import Decimal

class ERPCxCRepository(ABC):
    @abstractmethod
    async def obtener_facturas_pendientes(self, cod_cliente: str) -> List[Factura]:
        """
        Aplica los montos de pago, descuento y retención a una factura específica
        en la tabla SAACXC, reduciendo su saldo.
        """
        pass
