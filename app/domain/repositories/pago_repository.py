from abc import ABC, abstractmethod
from app.domain.entities.pago import Pago

class PagoRepository(ABC):
    @abstractmethod
    async def registrar(self, pago: Pago) -> Pago:
        """Registra un pago y actualiza el saldo de la factura en Saint"""
        pass
