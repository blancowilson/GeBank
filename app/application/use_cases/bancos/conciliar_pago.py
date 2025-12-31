from app.domain.services.reconciliation_service import ReconciliationEngine
from app.domain.entities.reconciliation import ReconciliationResult
from app.domain.repositories.insytech_repository import InsytechRepository
from app.domain.repositories.saint_transaction_repository import SaintTransactionRepository
from app.domain.repositories.saint_cxc_repository import SaintCxCRepository
from datetime import datetime

class ConciliarPagoUseCase:
    def __init__(
        self,
        reconciliation_engine: ReconciliationEngine,
        insytech_repo: InsytechRepository,
        saint_txn_repo: SaintTransactionRepository,
        saint_cxc_repo: SaintCxCRepository,
        current_user: str = "System" # Placeholder for user management
    ):
        self.reconciliation_engine = reconciliation_engine
        self.insytech_repo = insytech_repo
        self.saint_txn_repo = saint_txn_repo
        self.saint_cxc_repo = saint_cxc_repo
        self.current_user = current_user

    async def execute(self, pago_id: str) -> ReconciliationResult:
        """
        Orchestrates the reconciliation of a payment packet and persists the results to Saint.
        """
        reconciliation_result = await self.reconciliation_engine.attempt_reconciliation(pago_id)
        
        if reconciliation_result.is_fully_reconciled:
            pago = reconciliation_result.pago
            
            # 1. Update GePago audit fields and status
            pago.status = pago.APROBADO
            pago.conciliado_por = self.current_user
            pago.fecha_conciliacion = datetime.now()
            await self.insytech_repo.actualizar_pago(pago)
            
            # 2. For each matched financial instrument, create a transaction in SBTRAN
            for match in reconciliation_result.instrument_matches:
                if match.match_found and match.staging_txn:
                    await self.saint_txn_repo.registrar_transaccion(match.staging_txn)

            # 3. Apply payments, discounts, and retentions to SAACXC
            documentos = await self.insytech_repo.obtener_documentos_por_pago(pago_id)
            for doc in documentos:
                monto_pago_a_aplicar = doc.montoDoc - doc.montoDescuento - doc.montoRetencion
                
                await self.saint_cxc_repo.aplicar_pago_documento(
                    numero_documento=doc.numeroDoc,
                    cod_cliente=pago.codCliente,
                    monto_pago=monto_pago_a_aplicar,
                    monto_descuento=doc.montoDescuento,
                    monto_retencion=doc.montoRetencion
                )

            print(f"Pago {pago_id} reconciliado, APROBADO y persistido en Saint por {self.current_user}.")
        
        return reconciliation_result
