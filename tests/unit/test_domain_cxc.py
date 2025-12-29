import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from app.domain.value_objects.monto import Monto, Moneda
from app.domain.entities.cliente import Cliente
from app.domain.entities.factura import Factura
from app.domain.services.cxc_service import CXCService

def test_monto_suma_misma_moneda():
    m1 = Monto(valor=Decimal("100.00"), moneda=Moneda.USD)
    m2 = Monto(valor=Decimal("50.00"), moneda=Moneda.USD)
    m3 = m1 + m2
    assert m3.valor == Decimal("150.00")
    assert m3.moneda == Moneda.USD

def test_monto_error_diferente_moneda():
    m1 = Monto(valor=Decimal("100.00"), moneda=Moneda.USD)
    m2 = Monto(valor=Decimal("50.00"), moneda=Moneda.VES)
    with pytest.raises(ValueError, match="No se pueden sumar"):
        _ = m1 + m2

def test_cliente_initialization():
    cliente = Cliente(id="CLI001", descripcion="Cliente Test", rif="J-12345678-9")
    assert cliente.id == "CLI001"
    assert cliente.saldo_ves.valor == Decimal("0.00")

def test_cxc_service_antiguedad():
    fecha = datetime.now() - timedelta(days=45)
    dias = CXCService.calcular_antiguedad_dias(fecha)
    assert dias == 45

def test_cxc_service_clasificacion():
    f1 = Factura(
        numero="F1", tipo="FAC", sucursal="01", cliente_id="C1",
        monto_total=Decimal("100"), saldo_pendiente=Decimal("100"),
        fecha_emision=datetime.now() - timedelta(days=10)
    )
    f2 = Factura(
        numero="F2", tipo="FAC", sucursal="01", cliente_id="C1",
        monto_total=Decimal("200"), saldo_pendiente=Decimal("200"),
        fecha_emision=datetime.now() - timedelta(days=40)
    )
    categorias = CXCService.clasificar_por_vencimiento([f1, f2])
    assert len(categorias["0-30"]) == 1
    assert len(categorias["31-60"]) == 1
    assert categorias["0-30"][0].numero == "F1"
