from sqlalchemy import Column, String, DECIMAL, SmallInteger, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.infrastructure.database.session import Base

# ==========================================
# Legacy Saint Tables (dbo schema)
# ==========================================

class SaClie(Base):
    __tablename__ = "SACLIE"
    # implicit schema="dbo"
    
    CodClie = Column(String(15), primary_key=True, nullable=False)
    Descrip = Column(String(100))
    ID3 = Column(String(20)) # RIF/CI
    tipoid3 = Column(String(5))
    Pais = Column(String(30))
    Estado = Column(String(30))
    Ciudad = Column(String(30))
    Municipio = Column(String(50))
    Telef = Column(String(20))
    Email = Column(String(100))
    CodZona = Column(String(10))
    CodVend = Column(String(10))
    CodConv = Column(String(10))
    TipoCli = Column(String(10))
    EsCredito = Column(SmallInteger, default=0)
    LimiteCred = Column(DECIMAL(28, 4))
    DiasCred = Column(Integer)
    Descto = Column(DECIMAL(5, 2))
    Saldo = Column(DECIMAL(28, 4))
    SaldoPtos = Column(DECIMAL(28, 4))
    Activo = Column(SmallInteger, default=1)
    create_at = Column("create", String(100)) 

    # Relationships
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
    
    # Relationships
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
    
    create_at = Column("create", String(100))

    # Relationships
    cliente = relationship("SaClie", back_populates="facturas")
    vendedor = relationship("SaVend", back_populates="facturas")

class SaAcxc(Base):
    __tablename__ = "SAACXC"
    
    CodSucu = Column(String(5), primary_key=True, nullable=False)
    CodClie = Column(String(15), ForeignKey("SACLIE.CodClie"), primary_key=True, nullable=False)
    NroUnico = Column(Integer, primary_key=True, nullable=False)
    
    NumeroD = Column(String(20))
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
    create_at = Column("create", String(100))

    # Relationships
    cliente = relationship("SaClie", back_populates="cxc_documents")


# ==========================================
# Insytech / AppConciliacion Tables
# ==========================================

class GePagos(Base):
    __tablename__ = "GePagos"
    __table_args__ = {"schema": "AppConciliacion"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    idPago = Column(String(10), nullable=False, unique=True)
    codCliente = Column(String(20), nullable=False) # Reference to SACLIE
    DescripClie = Column(String(100), nullable=False)
    Usuario = Column(String(50), nullable=False)
    fecha = Column(DateTime, nullable=False)
    MontoPago = Column(DECIMAL(28, 4), nullable=False)
    MontoCancelado = Column(DECIMAL(28, 4), nullable=False)
    status = Column(SmallInteger, nullable=False) # 1=Pend, 3=Apr, 9=Rech
    UrlImagen = Column(Text)
    fechaCaptura = Column(DateTime, nullable=False)
    create_at = Column("create", String(100))

    # Relationships
    documentos = relationship("GeDocumentos", back_populates="pago")
    instrumentos = relationship("GeInstrumentos", back_populates="pago")

class GeDocumentos(Base):
    __tablename__ = "GeDocumentos"
    __table_args__ = {"schema": "AppConciliacion"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    idPago = Column(String(10), ForeignKey("AppConciliacion.GePagos.idPago"), nullable=False)
    tipoDoc = Column(String(4), nullable=False)
    numeroDoc = Column(String(30), nullable=False)
    emision = Column(DateTime, nullable=False)
    vencimiento = Column(DateTime, nullable=False)
    montoDoc = Column(DECIMAL(28, 4), nullable=False)
    porcentajeDescuento = Column(DECIMAL(5, 2), nullable=False)
    montoDescuento = Column(DECIMAL(28, 4), nullable=False)
    porcentajeRetencion = Column(DECIMAL(5, 2), nullable=False)
    montoRetencion = Column(DECIMAL(28, 4), nullable=False)
    NroRetencion = Column(String(50))
    UrlRetencion = Column(Text)
    create_at = Column("create", String(100))

    # Relationships
    pago = relationship("GePagos", back_populates="documentos")

class GeInstrumentos(Base):
    __tablename__ = "GeInstrumentos"
    __table_args__ = {"schema": "AppConciliacion"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    idPago = Column(String(10), ForeignKey("AppConciliacion.GePagos.idPago"), nullable=False)
    banco = Column(String(50))
    formaPago = Column(String(50), nullable=False)
    nroPlanilla = Column(String(30))
    fecha = Column(DateTime, nullable=False)
    tasa = Column(DECIMAL(28, 4), nullable=False)
    cheque = Column(String(20))
    bancoCliente = Column(String(50))
    monto = Column(DECIMAL(28, 4), nullable=False)
    create_at = Column("create", String(100))

    # Relationships
    pago = relationship("GePagos", back_populates="instrumentos")