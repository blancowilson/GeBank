from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

@dataclass
class TransactionRow:
    """Representación normalizada de una fila de un estado de cuenta o reporte."""
    raw_date: str
    description: str
    reference: str
    amount: Decimal # Use Decimal for financial precision
    currency: str  # 'USD', 'VES'
    transaction_type: str  # 'DEBIT', 'CREDIT'
    bank_name: str
    original_row_data: Dict[str, Any] # Para depuración

class BaseStatementParser(ABC):
    """
    Clase base abstracta para todos los parsers de archivos (Bancos, Insytech, etc).
    """
    supported_file_types: List[str] = []

    @abstractmethod
    def parse(self, file_content: bytes, filename: str) -> List[TransactionRow]:
        """
        Recibe el contenido binario del archivo y retorna una lista de transacciones normalizadas.
        """
        pass

    def validate_format(self, file_content: bytes, filename: str) -> bool:
        """
        Verifica si el archivo tiene una extensión de archivo soportada.
        Los parsers específicos pueden sobreescribir esto para validaciones más complejas (ej. revisar cabeceras).
        """
        if not self.supported_file_types:
            # If not defined, parser must implement its own validation logic
            raise NotImplementedError("El parser debe definir 'supported_file_types' o implementar 'validate_format'.")
        
        file_extension = os.path.splitext(filename)[1].lower()
        return file_extension in self.supported_file_types
import os
