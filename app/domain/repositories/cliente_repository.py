from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.cliente import Cliente

class ClienteRepository(ABC):
    @abstractmethod
    async def obtener_todos(self, skip: int = 0, limit: int = 100) -> List[Cliente]:
        """Obtiene una lista de clientes"""
        pass

    @abstractmethod
    async def obtener_por_id(self, cliente_id: str) -> Optional[Cliente]:
        """Obtiene un cliente por su ID"""
        pass

    @abstractmethod
    async def buscar_por_nombre(self, query: str) -> List[Cliente]:
        """Busca clientes por nombre o RIF"""
        pass
