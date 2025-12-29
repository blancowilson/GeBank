from typing import List
from datetime import datetime
from app.domain.entities.factura import Factura
from app.domain.value_objects.monto import Monto, Moneda
from decimal import Decimal

class CXCService:
    @staticmethod
    def calcular_saldo_total(facturas: List[Factura], moneda: Moneda) -> Monto:
        total = Decimal("0.00")
        # Nota: En Saint, las facturas pueden tener moneda propia. 
        # Por ahora filtramos por la moneda solicitada.
        for f in facturas:
            # Si la factura no tiene moneda especificada o coincide con la solicitada
            if hasattr(f, 'moneda') and f.moneda == moneda:
                total += f.saldo_pendiente
            elif moneda == Moneda.VES: # Default
                total += f.saldo_pendiente
        return Monto(valor=total, moneda=moneda)

    @staticmethod
    def calcular_antiguedad_dias(fecha_emision: datetime) -> int:
        delta = datetime.now() - fecha_emision
        return max(0, delta.days)

    @staticmethod
    def clasificar_por_vencimiento(facturas: List[Factura]):
        categorias = {
            "0-30": [],
            "31-60": [],
            "61-90": [],
            "90+": []
        }
        for f in facturas:
            dias = CXCService.calcular_antiguedad_dias(f.fecha_emision)
            if dias <= 30:
                categorias["0-30"].append(f)
            elif dias <= 60:
                categorias["31-60"].append(f)
            elif dias <= 90:
                categorias["61-90"].append(f)
            else:
                categorias["90+"].append(f)
        return categorias
