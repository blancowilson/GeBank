from abc import ABC, abstractmethod
from decimal import Decimal

class SaintCxCRepository(ABC):
    @abstractmethod
    async def aplicar_pago_documento(
        self,
        numero_documento: str,
        cod_cliente: str,
        monto_pago: Decimal,
        monto_descuento: Decimal,
        monto_retencion: Decimal
    ) -> None:
        """
        Aplica los montos de pago, descuento y retención a una factura específica
        en la tabla SAACXC, reduciendo su saldo.
        """
        pass
