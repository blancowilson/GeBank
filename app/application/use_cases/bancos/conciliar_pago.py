from app.domain.services.reconciliation_service import ReconciliationEngine
from app.domain.entities.reconciliation import ReconciliationResult
from app.domain.repositories.insytech_repository import InsytechRepository
from app.domain.repositories.saint_transaction_repository import SaintTransactionRepository
from app.domain.repositories.saint_cxc_repository import SaintCxCRepository

class ConciliarPagoUseCase:
    def __init__(
        self,
        reconciliation_engine: ReconciliationEngine,
        insytech_repo: InsytechRepository,
        saint_txn_repo: SaintTransactionRepository,
        saint_cxc_repo: SaintCxCRepository
    ):
        self.reconciliation_engine = reconciliation_engine
        self.insytech_repo = insytech_repo
        self.saint_txn_repo = saint_txn_repo
        self.saint_cxc_repo = saint_cxc_repo

    async def execute(self, pago_id: str) -> ReconciliationResult:
        """
        Orchestrates the reconciliation of a payment packet and persists the results to Saint.
        """
        # 1. Run the reconciliation engine to get match results
        reconciliation_result = await self.reconciliation_engine.attempt_reconciliation(pago_id)
        
        # 2. If reconciliation is complete, proceed with persistence
        if reconciliation_result.is_fully_reconciled:
            # Note: This should be an atomic transaction
            
            # 2.1 Update GePago status
            # await self.insytech_repo.actualizar_status_pago(pago_id, reconciliation_result.pago.APROBADO)
            
            # 2.2 For each matched financial instrument, create a transaction in SBTRAN
            for match in reconciliation_result.instrument_matches:
                if match.match_found and match.staging_txn:
                    await self.saint_txn_repo.registrar_transaccion(match.staging_txn)

            # 2.3 Apply payments, discounts, and retentions to SAACXC
            # This requires getting the documents associated with the payment
            documentos = await self.insytech_repo.obtener_documentos_por_pago(pago_id)
            for doc in documentos:
                # Calculate the net payment applied to this document
                # This logic is simplified; a real scenario might distribute the payment amount
                # across multiple documents based on some rule.
                monto_pago_a_aplicar = doc.montoDoc - doc.montoDescuento - doc.montoRetencion
                
                await self.saint_cxc_repo.aplicar_pago_documento(
                    numero_documento=doc.numeroDoc,
                    cod_cliente=reconciliation_result.pago.codCliente,
                    monto_pago=monto_pago_a_aplicar,
                    monto_descuento=doc.montoDescuento,
                    monto_retencion=doc.montoRetencion
                )

            reconciliation_result.pago.status = reconciliation_result.pago.APROBADO
            print(f"Pago {pago_id} reconciliado, APROBADO y persistido en Saint.")
        
        return reconciliation_result
