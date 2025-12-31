from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

@dataclass
class StagingTransaction:
    id: Optional[int]
    cod_banco: str
    referencia: str
    fecha: datetime
    monto: Decimal
    moneda: str
    tipo_movimiento: str
    descripcion: Optional[str] = None
    estatus: int = 0
    nombre_archivo: Optional[str] = None
    
    # Constants for Status
    PENDIENTE = 0
    CONCILIADO = 1
    ERROR = 2
