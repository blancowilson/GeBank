from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.pago_insytech import GePagos, GeDocumentos, GeInstrumentos

class InsytechRepository(ABC):
    
    @abstractmethod
    async def guardar_pago_completo(self, pago: GePagos, documentos: List[GeDocumentos], instrumentos: List[GeInstrumentos]) -> GePagos:
        """Guarda un pago completo de Insytech (cabecera, documentos e instrumentos)."""
        pass

    @abstractmethod
    async def obtener_pago_por_id(self, pago_id: str) -> Optional[GePagos]:
        """Obtiene un pago por su idPago de Insytech."""
        pass

    @abstractmethod
    async def obtener_documentos_por_pago(self, pago_id: str) -> List[GeDocumentos]:
        """Obtiene los documentos asociados a un pago."""
        pass

    @abstractmethod
    async def obtener_instrumentos_por_pago(self, pago_id: str) -> List[GeInstrumentos]:
        """Obtiene los instrumentos asociados a un pago."""
        pass
