from abc import ABC, abstractmethod
from typing import List, Optional
from decimal import Decimal
from app.domain.entities.staging_transaction import StagingTransaction

class StagingBancoRepository(ABC):
    
    @abstractmethod
    async def guardar_lote(self, transacciones: List[StagingTransaction]) -> None:
        """Guarda un lote de transacciones en la tabla de staging."""
        pass
    
    @abstractmethod
    async def buscar_por_referencia_y_monto(self, referencia: str, monto: Decimal, cod_banco: str) -> Optional[StagingTransaction]:
        """Busca una transacción específica para conciliación."""
        pass
    
    @abstractmethod
    async def obtener_pendientes(self, limit: int = 100) -> List[StagingTransaction]:
        """Obtiene transacciones pendientes de procesar."""
        pass
