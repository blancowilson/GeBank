from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TransactionRow:
    """Representación normalizada de una fila de un estado de cuenta o reporte."""
    raw_date: str
    description: str
    reference: str
    amount: float
    currency: str  # 'USD', 'VES'
    transaction_type: str  # 'DEBIT', 'CREDIT'
    bank_name: str
    original_row_data: Dict[str, Any] # Para depuración

class BaseStatementParser(ABC):
    """
    Clase base abstracta para todos los parsers de archivos (Bancos, Insytech, etc).
    """

    @abstractmethod
    def parse(self, file_content: bytes, filename: str) -> List[TransactionRow]:
        """
        Recibe el contenido binario del archivo y retorna una lista de transacciones normalizadas.
        """
        pass

    @abstractmethod
    def validate_format(self, file_content: bytes, filename: str) -> bool:
        """
        Verifica si el archivo tiene el formato correcto para este parser.
        """
        pass
