from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

@dataclass
class GePagos:
    id: Optional[int]
    idPago: str
    codCliente: str
    DescripClie: str
    Usuario: str
    fecha: datetime
    MontoPago: Decimal
    MontoCancelado: Decimal
    status: int # 1=Pendiente, 3=Aprobado, 9=Rechazado
    UrlImagen: Optional[str]
    fechaCaptura: datetime
    conciliado_por: Optional[str] = None
    fecha_conciliacion: Optional[datetime] = None
    
    # Relations (populated at runtime)
    documentos: Optional[List['GeDocumentos']] = None
    instrumentos: Optional[List['GeInstrumentos']] = None
    
    # Constants for Status
    PENDIENTE = 1
    APROBADO = 3
    RECHAZADO = 9

@dataclass
class GeDocumentos:
    id: Optional[int]
    idPago: str
    tipoDoc: str
    numeroDoc: str
    emision: datetime
    vencimiento: datetime
    montoDoc: Decimal
    porcentajeDescuento: Decimal
    montoDescuento: Decimal
    porcentajeRetencion: Decimal
    montoRetencion: Decimal
    NroRetencion: Optional[str]
    UrlRetencion: Optional[str]

@dataclass
class GeInstrumentos:
    id: Optional[int]
    idPago: str
    banco: Optional[str]
    formaPago: str
    nroPlanilla: Optional[str]
    fecha: datetime
    tasa: Optional[Decimal]
    cheque: Optional[str]
    bancoCliente: Optional[str]
    monto: Decimal
    moneda: str
