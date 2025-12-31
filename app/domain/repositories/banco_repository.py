from abc import ABC, abstractmethod
from typing import List
from app.domain.entities.banco import Banco

class BancoRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[Banco]:
        """Obtiene todos los bancos registrados."""
        pass
