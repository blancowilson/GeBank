from abc import ABC, abstractmethod
from typing import List
from app.domain.entities.staging_transaction import StagingTransaction

class SaintTransactionRepository(ABC):
    @abstractmethod
    async def registrar_transaccion(self, transaccion: StagingTransaction) -> None:
        """
        Registra una transacción validada en la tabla SBTRAN de Saint.
        """
        pass
