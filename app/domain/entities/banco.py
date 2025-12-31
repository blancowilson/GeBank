from dataclasses import dataclass
from typing import Optional

@dataclass
class Banco:
    id: str
    descripcion: str
    activo: bool
