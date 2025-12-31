from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

# --- DocumentDetail (Corresponds to GeDocumentos) ---
class DocumentDetail(BaseModel):
    numeroDoc: str = Field(..., description="Número de factura o documento afectado.")
    tipoDoc: str = Field(..., description="Tipo de documento (FACT, N/E).", pattern="^(FACT|N/E)$")
    emision: datetime = Field(..., description="Fecha de emisión del documento.")
    vencimiento: datetime = Field(..., description="Fecha de vencimiento del documento.")
    montoDoc: Decimal = Field(..., gt=0, description="Monto total del documento afectado.")
    
    # Administrative components
    porcentajeDescuento: Decimal = Field(Decimal("0.00"), ge=0, le=100, description="% de descuento aplicado.")
    montoDescuento: Decimal = Field(Decimal("0.00"), ge=0, description="Monto en BS del descuento.")
    porcentajeRetencion: Decimal = Field(Decimal("0.00"), ge=0, le=100, description="% de retención fiscal aplicada.")
    montoRetencion: Decimal = Field(Decimal("0.00"), ge=0, description="Monto retenido en BS.")
    NroRetencion: Optional[str] = Field(None, description="Número de comprobante de retención.")
    UrlRetencion: Optional[str] = Field(None, description="URL del documento de retención.")

# --- InstrumentDetail (Corresponds to GeInstrumentos) ---
class InstrumentDetail(BaseModel):
    formaPago: str = Field(..., description="Forma de pago utilizada (CHEQUE, TRANSFERENCIA, EFECTIVO, TARJETA, ZELLE, OTROS).")
    nroPlanilla: Optional[str] = Field(None, description="Número de planilla o referencia bancaria.")
    fecha: datetime = Field(..., description="Fecha del pago del instrumento.")
    monto: Decimal = Field(..., gt=0, description="Monto en este instrumento.")
    moneda: str = Field(..., description="Moneda del monto (VES, USD).", pattern="^(VES|USD)$")
    
    # Optional fields for transfers/checks
    banco: Optional[str] = Field(None, description="Banco de la empresa receptora (nuestro banco).")
    bancoCliente: Optional[str] = Field(None, description="Banco del cliente emisor.")
    cheque: Optional[str] = Field(None, description="Número de cheque (si aplica).")
    
    # For VES payments, if client reports a specific rate used
    tasa: Optional[Decimal] = Field(None, description="Tasa de cambio aplicada si el pago es en VES y se reporta equivalente USD.")

# --- PaymentPacketDTO (Corresponds to GePagos header) ---
class PaymentPacketDTO(BaseModel):
    idPago: str = Field(..., description="ID único del pago en la plataforma de pagos (Insytech).")
    codCliente: str = Field(..., description="Código del cliente SAINT asociado al pago.")
    DescripClie: str = Field(..., description="Nombre del cliente para referencia.")
    Usuario: str = Field(..., description="Usuario que registró el pago en Insytech.")
    fecha: datetime = Field(..., description="Fecha del pago reportado por el vendedor.")
    MontoPago: Decimal = Field(..., gt=0, description="Monto total reportado en el paquete de pago (suma de instrumentos + admin).")
    MontoCancelado: Decimal = Field(..., ge=0, description="Monto que se espera cancelar en el sistema (puede ser menor a MontoPago si hay retenciones).")
    status: Optional[int] = Field(1, description="Estado del pago (1=Pendiente, 3=Aprobado, 9=Rechazado).") # Default to PENDIENTE
    UrlImagen: Optional[str] = Field(None, description="URL del comprobante/recibo general del pago.")
    fechaCaptura: Optional[datetime] = Field(default_factory=datetime.now, description="Fecha de captura de datos en el sistema.")
    
    documentos: List[DocumentDetail] = Field(..., min_items=1, description="Detalle de documentos (facturas, retenciones, NC) afectados por este pago.")
    instrumentos: List[InstrumentDetail] = Field(..., min_items=1, description="Detalle de los instrumentos financieros (transferencias, efectivo) de este pago.")
