from abc import ABC, abstractmethod
from typing import Optional

class IConfigRepository(ABC):
    @abstractmethod
    async def get_config(self, key: str) -> Optional[str]:
        """Obtiene el valor de una configuración por su clave."""
        pass

    @abstractmethod
    async def set_config(self, key: str, value: str) -> None:
        """Establece o actualiza una configuración."""
        pass
