from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.factura import Factura

class FacturaRepository(ABC):
    
    @abstractmethod
    async def obtener_por_id(self, numero: str, tipo: str) -> Optional[Factura]:
        """Obtiene una factura por su número y tipo"""
        pass

    @abstractmethod
    async def obtener_pendientes_por_cliente(self, cliente_id: str) -> List[Factura]:
        """Obtiene todas las facturas con saldo pendiente de un cliente"""
        pass
