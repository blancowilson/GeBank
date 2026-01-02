from sqlalchemy import Column, String, DECIMAL, SmallInteger, Integer, DateTime, ForeignKey, Text, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from app.infrastructure.database.session import Base
from decimal import Decimal

# ==========================================
# Legacy Saint Tables (dbo schema)
# ==========================================

class SaClie(Base):
    __tablename__ = "SACLIE"
    
    CodClie = Column(String(15), primary_key=True, nullable=False)
    Descrip = Column(String(100))
    ID3 = Column(String(20))
    tipoid3 = Column(SmallInteger, nullable=False) # Corrected type and added constraint
    Pais = Column(Integer, nullable=False)
    Estado = Column(Integer, nullable=False)
    Ciudad = Column(Integer, nullable=False)
    Municipio = Column(Integer, nullable=False)
    Telef = Column(String(20))
    Email = Column(String(100))
    CodZona = Column(String(10))
    CodVend = Column(String(10))
    CodConv = Column(String(10))
    TipoCli = Column(SmallInteger, nullable=False) # Corrected type and added constraint
    EsCredito = Column(SmallInteger, default=0)
    LimiteCred = Column(DECIMAL(28, 4), nullable=False, default=Decimal("0.00"))
    DiasCred = Column(Integer, nullable=False, default=0)
    Descto = Column(DECIMAL(5, 2), nullable=False, default=Decimal("0.00"))
    Saldo = Column(DECIMAL(28, 4), nullable=False, default=Decimal("0.00"))
    SaldoPtos = Column(DECIMAL(28, 4), nullable=False, default=Decimal("0.00"))
    Activo = Column(SmallInteger, nullable=False, default=1)

    facturas = relationship("SaFact", back_populates="cliente")
    cxc_documents = relationship("SaAcxc", back_populates="cliente")

class SaVend(Base):
    __tablename__ = "SAVEND"
    
    CodVend = Column(String(10), primary_key=True, nullable=False)
    Descrip = Column(String(100))
    CodSucu = Column(String(5))
    ID3 = Column(String(20))
    Telef = Column(String(20))
    Email = Column(String(100))
    Activo = Column(SmallInteger, default=1)
    
    facturas = relationship("SaFact", back_populates="vendedor")

class SaFact(Base):
    __tablename__ = "SAFACT"
    
    TipoFac = Column(String(5), primary_key=True, nullable=False)
    NumeroD = Column(String(20), primary_key=True, nullable=False)
    CodSucu = Column(String(5), primary_key=True, nullable=False)
    
    CodClie = Column(String(15), ForeignKey("SACLIE.CodClie"))
    CodVend = Column(String(10), ForeignKey("SAVEND.CodVend"))
    CodUbic = Column(String(10))
    
    Signo = Column(String(1))
    Moneda = Column(String(5))
    Factor = Column(DECIMAL(28, 4))
    Monto = Column(DECIMAL(28, 4))
    MtoTax = Column(DECIMAL(28, 4))
    Fletes = Column(DECIMAL(28, 4))
    TGravable = Column(DECIMAL(28, 4))
    TExento = Column(DECIMAL(28, 4))
    CostoPrd = Column(DECIMAL(28, 4))
    
    FechaE = Column(DateTime)
    FechaV = Column(DateTime)
    FechaI = Column(DateTime)
    
    CancelA = Column(DECIMAL(28, 4))
    CancelE = Column(DECIMAL(28, 4))
    CancelC = Column(DECIMAL(28, 4))
    CancelG = Column(DECIMAL(28, 4))

    cliente = relationship("SaClie", back_populates="facturas")
    vendedor = relationship("SaVend", back_populates="facturas")

class SaAcxc(Base):
    __tablename__ = "SAACXC"
    
    CodSucu = Column(String(5), primary_key=True, nullable=False)
    CodClie = Column(String(15), ForeignKey("SACLIE.CodClie"), primary_key=True, nullable=False)
    NroUnico = Column(Integer, primary_key=True, nullable=False)
    
    NumeroD = Column(String(20))
    TipoCXC = Column(String(5))
    TipoCXC = Column(String(5))
    FechaE = Column(DateTime)
    FechaV = Column(DateTime)
    FechaI = Column(DateTime)
    
    Monto = Column(DECIMAL(28, 4))
    MontoNeto = Column(DECIMAL(28, 4))
    MtoTax = Column(DECIMAL(28, 4))
    RetenIVA = Column(DECIMAL(28, 4))
    Saldo = Column(DECIMAL(28, 4))
    SaldoOrg = Column(DECIMAL(28, 4))
    
    CancelI = Column(DECIMAL(28, 4))
    CancelA = Column(DECIMAL(28, 4))
    CancelE = Column(DECIMAL(28, 4))
    CancelC = Column(DECIMAL(28, 4))
    CancelG = Column(DECIMAL(28, 4))
    
    EsChqDev = Column(SmallInteger)

    cliente = relationship("SaClie", back_populates="cxc_documents")
    pagos = relationship("SaPagcxc", back_populates="cxc_document")

class SaPagcxc(Base):
    __tablename__ = "SAPAGCXC"
    
    NroPpal = Column(Integer, ForeignKey("SAACXC.NroUnico"), primary_key=True, nullable=False)
    NroUnico = Column(Integer, primary_key=True, nullable=False)
    
    CodClie = Column(String(15), nullable=False)
    FechaE = Column(DateTime, nullable=False)
    Monto = Column(DECIMAL(28, 4), nullable=False)
    NumeroD = Column(String(20), nullable=False)
    Referen = Column(String(20))
    
    cxc_document = relationship("SaAcxc", back_populates="pagos")

class SaBanc(Base):
    __tablename__ = "SBBANC"
    
    CodBanc = Column(String(30), primary_key=True, nullable=False)
    descripcion = Column(String(60), nullable=False)  # Mapped from descripcion
    Ciudad = Column(Integer)
    Estado = Column(Integer)
    Pais = Column(Integer)
    SaldoAct = Column(DECIMAL(28, 4))
    SaldoC1 = Column(DECIMAL(28, 4))
    SaldoC2 = Column(DECIMAL(28, 4))
    FechaC1 = Column(DateTime)
    FechaC2 = Column(DateTime)
    CtaContab = Column(String(25))
    
    transacciones = relationship("SbTran", back_populates="banco")

class SbCtas(Base):
    __tablename__ = "SBCTAS"

    CodCta = Column(String(30), primary_key=True, nullable=False)
    Descrip = Column(String(60), nullable=False, name="descripcion")
    SaldoAct = Column(DECIMAL(28, 4))
    EsBanco = Column(Integer)
    CtaBase = Column(Integer)

class SbTran(Base):
    __tablename__ = "SBTRAN"
    
    CodBanc = Column(String(30), ForeignKey("SBBANC.CodBanc"), primary_key=True, nullable=False)
    Fecha = Column(DateTime, primary_key=True, nullable=False)
    NOpe = Column(Integer, primary_key=True, nullable=False, name="nope")
    
    TipoOpe = Column(Integer, nullable=False) # YAML tipoope
    CodOper = Column(String(10)) # YAML codoper
    Monto = Column(DECIMAL(28, 4), nullable=False)
    MtoCr = Column(DECIMAL(28, 4))
    MtoDb = Column(DECIMAL(28, 4))
    
    Descrip = Column(String(60), name="descripcion")
    Beneficiario = Column(String(50), name="beneori")
    Estado = Column(Integer, nullable=False) # 0:tránsito; 1:pre conciliado; 2:conciliado
    Consolidado = Column(Integer, nullable=False)
    
    banco = relationship("SaBanc", back_populates="transacciones")
    detalles = relationship("SbDtrn", back_populates="transaccion")

class SbDtrn(Base):
    __tablename__ = "SBDTRN"
    
    CodBanc = Column(String(30), primary_key=True, nullable=False)
    NOpe = Column(Integer, primary_key=True, nullable=False, name="nope")
    NLinea = Column(Integer, primary_key=True, nullable=False, name="nlinea")
    
    CodCta = Column(String(30))
    Monto = Column(DECIMAL(28, 4), nullable=False)
    MtoCr = Column(DECIMAL(28, 4))
    MtoDb = Column(DECIMAL(28, 4))
    Descrip = Column(String(60), name="descripcion")
    CdCd = Column(Integer, nullable=False) # Cheque, Depósito, Crédito, Débito

    # ForeignKeyComposite for relationship
    __table_args__ = (
        ForeignKeyConstraint(['CodBanc', 'nope'], ['SBTRAN.CodBanc', 'SBTRAN.nope']),
    )

    transaccion = relationship("SbTran", back_populates="detalles")

class SsUsrs(Base):
    __tablename__ = "SSUSRS"
    
    CodUsua = Column(String(20), primary_key=True, nullable=False)
    Usuario = Column(String(50), nullable=False, unique=True)
    Password = Column(String(255), nullable=False)
    Nombre = Column(String(100))
    Email = Column(String(100))
    Estado = Column(SmallInteger, default=1)
    FechaCreacion = Column(DateTime)
    UltimoAcceso = Column(DateTime)

# ==========================================
# Insytech / AppConciliacion Tables
# ==========================================

class GePagos(Base):
    __tablename__ = "GePagos"
    __table_args__ = {"schema": "dbo"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    idPago = Column(String(20), nullable=False, unique=True)
    codCliente = Column(String(20), nullable=False)
    DescripClie = Column(String(100), nullable=False)
    Usuario = Column(String(50), nullable=False)
    fecha = Column(DateTime, nullable=False)
    MontoPago = Column(DECIMAL(28, 4), nullable=False, name="montoPago")
    MontoCancelado = Column(DECIMAL(28, 4), nullable=False, name="montoCancelado")
    status = Column(SmallInteger, nullable=False)
    UrlImagen = Column(Text, name="urlImagen")
    fechaCaptura = Column(DateTime, nullable=False)
    
    # Audit fields
    conciliado_por = Column(String(50), nullable=True)
    fecha_conciliacion = Column(DateTime, nullable=True)

    documentos = relationship("GeDocumentos", back_populates="pago")
    instrumentos = relationship("GeInstrumentos", back_populates="pago")

class GeDocumentos(Base):
    __tablename__ = "GeDocumentos"
    __table_args__ = {"schema": "dbo"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    idPago = Column(String(20), ForeignKey("dbo.GePagos.idPago"), nullable=False)
    tipoDoc = Column(String(4), nullable=False)
    numeroDoc = Column(String(30), nullable=False)
    emision = Column(DateTime, nullable=False)
    vencimiento = Column(DateTime, nullable=False)
    montoDoc = Column(DECIMAL(28, 4), nullable=False, name="montoDoc")
    porcentajeDescuento = Column(DECIMAL(5, 2), nullable=False, name="porcentajeDescuento")
    montoDescuento = Column(DECIMAL(28, 4), nullable=False, name="montoDescuento")
    porcentajeRetencion = Column(DECIMAL(5, 2), nullable=False, name="porcentajeRetencion")
    montoRetencion = Column(DECIMAL(28, 4), nullable=False, name="montoRetencion")
    NroRetencion = Column(String(50), name="NroRetencion")
    UrlRetencion = Column(Text, name="UrlRetencion")

    pago = relationship("GePagos", back_populates="documentos")

class GeInstrumentos(Base):
    __tablename__ = "GeInstrumentos"
    __table_args__ = {"schema": "dbo"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    idPago = Column(String(20), ForeignKey("dbo.GePagos.idPago"), nullable=False)
    banco = Column(String(50), name="banco")
    formaPago = Column(String(50), nullable=False, name="formaPago")
    nroPlanilla = Column(String(30), name="nroPlanilla")
    fecha = Column(DateTime, nullable=False)
    tasa = Column(DECIMAL(28, 4), nullable=True, name="tasa")
    cheque = Column(String(20), name="cheque")
    bancoCliente = Column(String(50), name="bancoCliente")
    monto = Column(DECIMAL(28, 4), nullable=False, name="monto")
    moneda = Column(String(5), nullable=False, name="moneda")
    estatus = Column(SmallInteger, default=0) # 0=Pending, 1=Reconciled

    pago = relationship("GePagos", back_populates="instrumentos")

class StagingBancos(Base):
    __tablename__ = "Staging_Bancos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Matching fields
    cod_banco = Column(String(30), nullable=False) # Maps to SBBANC.CodBanc
    referencia = Column(String(50), nullable=False)
    fecha = Column(DateTime, nullable=False)
    
    # Amounts and Currency
    monto = Column(DECIMAL(28, 4), nullable=False)
    moneda = Column(String(5), nullable=False) # 'VES', 'USD'
    
    # Transaction Type (Debito/Credito)
    tipo_movimiento = Column(String(10), nullable=False) # 'DEBITO', 'CREDITO'
    
    # Raw Data
    descripcion = Column(String(255))
    
    # Status
    estatus = Column(SmallInteger, default=0) # 0=Pendiente, 1=Conciliado, 2=Error
    
    # Metadata
    nombre_archivo = Column(String(100))

# ==========================================
# SQL Views as Mapped Classes
# ==========================================

class VwAdmFactConBs(Base):
    __tablename__ = 'VW_ADM_FACT_CONBS'
    # This view is read-only
    
    TipoFac = Column(String, primary_key=True)
    NumeroD = Column(String, primary_key=True)
    SUBTOTAL_BS = Column(DECIMAL)
    IMPUESTO_BS = Column(DECIMAL)
    FACTOR = Column(DECIMAL)

    @property
    def TOTAL_BS(self):
        return (self.SUBTOTAL_BS or 0) + (self.IMPUESTO_BS or 0)

# ==========================================
# System Configuration
# ==========================================

class SystemConfig(Base):
    __tablename__ = "SystemConfig"
    __table_args__ = {"schema": "dbo"}

    key = Column(String(50), primary_key=True, nullable=False)
    value = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    updated_at = Column(DateTime, nullable=True)

class BankMapping(Base):
    __tablename__ = "BankMapping"
    __table_args__ = {"schema": "dbo"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    portal_code = Column(String(50), nullable=False, unique=True) # e.g. "04"
    erp_code = Column(String(30), nullable=False) # e.g. "110103" (FK to SBBANC theoretically)
    description = Column(String(100), nullable=True)
    is_cash = Column(SmallInteger, default=0, nullable=False) # 0=Bank, 1=Cash
    currency = Column(String(5), default='USD', nullable=False)
    updated_at = Column(DateTime, nullable=True)

class ExchangeRate(Base):
    __tablename__ = "ExchangeRates"
    __table_args__ = {"schema": "dbo"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(DateTime, nullable=False)
    moneda_origen = Column(String(5), nullable=False)
    moneda_destino = Column(String(5), nullable=False)
    tasa = Column(DECIMAL(28, 8), nullable=False)
    tipo_tasa = Column(String(20), default='OFICIAL', nullable=False) # OFICIAL, PARALELO, ETC
    created_at = Column(DateTime, nullable=False)
