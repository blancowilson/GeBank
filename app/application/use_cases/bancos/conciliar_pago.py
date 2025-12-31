from app.domain.services.reconciliation_service import ReconciliationEngine
from app.domain.entities.reconciliation import ReconciliationResult
from app.domain.repositories.insytech_repository import InsytechRepository

class ConciliarPagoUseCase:
    def __init__(
        self,
        reconciliation_engine: ReconciliationEngine,
        insytech_repo: InsytechRepository
    ):
        self.reconciliation_engine = reconciliation_engine
        self.insytech_repo = insytech_repo

    async def execute(self, pago_id: str) -> ReconciliationResult:
        """
        Orchestrates the reconciliation of a payment packet.
        1. Runs the reconciliation engine.
        2. Updates the status of the GePago based on the result.
        3. Returns the detailed reconciliation result for the UI.
        """
        reconciliation_result = await self.reconciliation_engine.attempt_reconciliation(pago_id)
        
        # Update GePago status if reconciliation is complete
        if reconciliation_result.is_fully_reconciled:
            # Here we would update the status in the DB
            # await self.insytech_repo.actualizar_status_pago(pago_id, GePagos.APROBADO)
            # This method needs to be added to the repository interface and implementation
            reconciliation_result.pago.status = reconciliation_result.pago.APROBADO
            print(f"Pago {pago_id} reconciliado y APROBADO.")
        
        return reconciliation_result
