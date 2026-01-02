from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel

class BankMappingDTO(BaseModel):
    id: Optional[int] = None
    portal_code: str
    erp_code: str
    description: Optional[str] = None
    is_cash: bool = False
    currency: str = 'USD'

class IBankMappingRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[BankMappingDTO]:
        """Obtiene todos los mapeos configurados."""
        pass

    @abstractmethod
    async def get_by_portal_code(self, portal_code: str) -> Optional[BankMappingDTO]:
        """Busca un mapeo por el código del portal."""
        pass

    @abstractmethod
    async def save(self, mapping: BankMappingDTO) -> BankMappingDTO:
        """Guarda o actualiza un mapeo."""
        pass

    @abstractmethod
    async def delete(self, mapping_id: int) -> None:
        """Elimina un mapeo."""
        pass
