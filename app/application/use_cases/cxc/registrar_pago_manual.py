from app.domain.repositories.pago_repository import PagoRepository
from app.domain.repositories.factura_repository import FacturaRepository
from app.domain.entities.pago import Pago
from app.domain.value_objects.monto import Monto, Moneda
from app.shared.utils.audit_logger import audit
from datetime import datetime
from decimal import Decimal

class RegistrarPagoManualUseCase:
    def __init__(
        self, 
        pago_repo: PagoRepository,
        factura_repo: FacturaRepository
    ):
        self.pago_repo = pago_repo
        self.factura_repo = factura_repo

    @audit(action="REGISTRAR_PAGO_MANUAL", target_entity="PAGO")
    async def execute(
        self, 
        cliente_id: str, 
        factura_numero: str, 
        monto_valor: Decimal,
        moneda: Moneda,
        referencia: str,
        usuario: str,
        banco_id: str = None
    ) -> Pago:
        # 1. Validate invoice exists
        factura = await self.factura_repo.obtener_por_id(factura_numero, "FAC")
        if not factura:
            raise ValueError(f"Factura {factura_numero} no encontrada")
            
        if monto_valor > factura.saldo_pendiente:
            raise ValueError(f"El monto ({monto_valor}) excede el saldo pendiente ({factura.saldo_pendiente})")

        # 2. Create Pago entity
        pago = Pago(
            cliente_id=cliente_id,
            factura_numero=factura_numero,
            monto=Monto(valor=monto_valor, moneda=moneda),
            fecha=datetime.now(),
            referencia=referencia,
            usuario=usuario,
            banco_id=banco_id
        )

        # 3. Persist and update Saint
        return await self.pago_repo.registrar(pago)
