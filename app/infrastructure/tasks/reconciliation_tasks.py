from app.infrastructure.tasks.celery_app import celery_app
from app.infrastructure.database.session import AsyncSessionLocal
from app.infrastructure.repositories.portal_repository_impl import PortalRepositoryImpl
from app.infrastructure.repositories.staging_banco_repository_impl import StagingBancoRepositoryImpl
from app.infrastructure.repositories.bank_mapping_repository_impl import BankMappingRepositoryImpl
from app.infrastructure.repositories.config_repository_impl import ConfigRepositoryImpl
from app.infrastructure.configuration.tasa_service import TasaService
from app.infrastructure.saint.erp_transaction_repository_impl import ERPTransactionRepositoryImpl
from app.infrastructure.saint.erp_cxc_repository_impl import ERPCxCRepositoryImpl
from app.domain.services.reconciliation_service import ReconciliationEngine
from app.application.use_cases.bancos.conciliar_pago import ConciliarPagoUseCase
import asyncio
from loguru import logger

@celery_app.task(bind=True, max_retries=3)
def conciliar_pago_task(self, pago_id: str, user_id: str):
    """
    Tarea de Celery para ejecutar la conciliación de un pago en segundo plano.
    """
    async def _execute_reconciliation():
        async with AsyncSessionLocal() as session:
            logger.info(f"Iniciando conciliación asíncrona para pago {pago_id} por {user_id}")
            
            # 1. Dependency Injection inside the task context
            portal_repo = PortalRepositoryImpl(session)
            staging_repo = StagingBancoRepositoryImpl(session)
            mapping_repo = BankMappingRepositoryImpl(session)
            tasa_service = TasaService(config_repo=ConfigRepositoryImpl(session), session=session)
            
            erp_txn_repo = ERPTransactionRepositoryImpl(session)
            erp_cxc_repo = ERPCxCRepositoryImpl(session)
            
            engine = ReconciliationEngine(portal_repo, staging_repo, mapping_repo, tasa_service)
            use_case = ConciliarPagoUseCase(engine, portal_repo, erp_txn_repo, erp_cxc_repo, current_user=user_id)
            
            # 2. Execute
            result = await use_case.execute(pago_id)
            
            logger.info(f"Conciliación finalizada para {pago_id}. Match total: {result.is_fully_reconciled}")
            
            # Return serializable result for Celery backend
            return {
                "pago_id": pago_id,
                "is_fully_reconciled": result.is_fully_reconciled,
                "details": [m.details for m in result.instrument_matches]
            }

    try:
        # Check if there is an existing event loop (common in tests or some environments)
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # If loop is running, we might need a different approach or just return the coroutine 
            # but Celery needs a sync result.
            # In 'eager' mode during tests, this is where it fails.
            # Let's use a nested loop or run_until_complete if possible, 
            # or better: use nest_asyncio if available or a custom bridge.
            
            # Simple fix for eager tests: 
            import nest_asyncio
            nest_asyncio.apply()
            return asyncio.run(_execute_reconciliation())
        else:
            return asyncio.run(_execute_reconciliation())
    except Exception as e:
        logger.error(f"Error en tarea de conciliación {pago_id}: {e}")
        raise self.retry(exc=e, countdown=10)
