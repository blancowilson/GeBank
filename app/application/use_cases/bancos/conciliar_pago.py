from app.domain.services.reconciliation_service import ReconciliationEngine
from app.domain.entities.reconciliation import ReconciliationResult
from app.domain.repositories.portal_repository import PortalRepository
from app.domain.repositories.erp_transaction_repository import ERPTransactionRepository
from app.domain.repositories.erp_cxc_repository import ERPCxCRepository
from datetime import datetime

class ConciliarPagoUseCase:
    def __init__(
        self,
        reconciliation_engine: ReconciliationEngine,
        portal_repo: PortalRepository,
        erp_txn_repo: ERPTransactionRepository,
        erp_cxc_repo: ERPCxCRepository,
        current_user: str = "System" # Placeholder for user management
    ):
        self.reconciliation_engine = reconciliation_engine
        self.portal_repo = portal_repo
        self.erp_txn_repo = erp_txn_repo
        self.erp_cxc_repo = erp_cxc_repo
        self.current_user = current_user

    async def execute(self, pago_id: str) -> ReconciliationResult:
        """
        Orchestrates the reconciliation of a payment packet and persists the results to ERP.
        """
        reconciliation_result = await self.reconciliation_engine.attempt_reconciliation(pago_id)
        
        if reconciliation_result.is_fully_reconciled:
            pago = reconciliation_result.pago
            
            # 1. Update Portal Pago audit fields and status
            pago.status = pago.APROBADO
            pago.conciliado_por = self.current_user
            pago.fecha_conciliacion = datetime.now()
            await self.portal_repo.actualizar_pago(pago)
            
            # 2. For each matched financial instrument, create a transaction in ERP bank ledger
            for match in reconciliation_result.instrument_matches:
                if match.match_found and match.staging_txn:
                    await self.erp_txn_repo.registrar_transaccion(match.staging_txn)

            # 3. Apply payments, discounts, and retentions to ERP CxC
            documentos = await self.portal_repo.obtener_documentos_por_pago(pago_id)
            for doc in documentos:
                monto_pago_a_aplicar = doc.montoDoc - doc.montoDescuento - doc.montoRetencion
                
                await self.erp_cxc_repo.aplicar_pago_documento(
                    numero_documento=doc.numeroDoc,
                    cod_cliente=pago.codCliente,
                    monto_pago=monto_pago_a_aplicar,
                    monto_descuento=doc.montoDescuento,
                    monto_retencion=doc.montoRetencion
                )

            print(f"Pago {pago_id} reconciliado, APROBADO y persistido en ERP por {self.current_user}.")
        
        return reconciliation_result
