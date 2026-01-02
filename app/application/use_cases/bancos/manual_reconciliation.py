from app.domain.repositories.portal_repository import PortalRepository
from app.domain.repositories.erp_transaction_repository import ERPTransactionRepository
from app.domain.repositories.bank_mapping_repository import IBankMappingRepository
from app.domain.repositories.staging_banco_repository import StagingBancoRepository
from app.domain.entities.staging_transaction import StagingTransaction
from datetime import datetime

class ManualReconciliationUseCase:
    def __init__(
        self,
        portal_repo: PortalRepository,
        erp_txn_repo: ERPTransactionRepository,
        mapping_repo: IBankMappingRepository,
        staging_repo: StagingBancoRepository,
        current_user: str = "WebUser"
    ):
        self.portal_repo = portal_repo
        self.erp_txn_repo = erp_txn_repo
        self.mapping_repo = mapping_repo
        self.staging_repo = staging_repo
        self.current_user = current_user

    async def reconcile_cash(self, instrument_id: int):
        # 1. Get Instrument
        instr = await self.portal_repo.obtener_instrumento_por_id(instrument_id)
        if not instr:
            raise ValueError("Instrumento no encontrado")
        
        if instr.estatus == 1:
            raise ValueError("Instrumento ya conciliado")

        # 2. Get Bank Mapping
        mapping = await self.mapping_repo.get_by_portal_code(instr.banco)
        if not mapping or not mapping.is_cash:
             raise ValueError("Instrumento no mapeado como efectivo")

        # 3. Create Virtual Staging Transaction (for ERP persistence)
        # Note: In Saint, cash entries are usually just SBTRAN records with specific operation types.
        virtual_txn = StagingTransaction(
            id=None,
            cod_banco=mapping.erp_code,
            referencia=instr.nroPlanilla or instr.cheque or "EFECTIVO",
            fecha=instr.fecha,
            monto=instr.monto,
            moneda=instr.moneda,
            tipo_movimiento="DEBITO", # In Bank Ledger: Debit = Increase Asset (Cash In)
            descripcion=f"Ingreso Caja {instr.nroPlanilla or ''}",
            estatus=1,
            nombre_archivo="MANUAL_CASH"
        )
        
        # 4. Save to Saint (SBTRAN)
        await self.erp_txn_repo.registrar_transaccion(virtual_txn)
        
        # 5. Mark Instrument Reconciled
        instr.estatus = 1
        await self.portal_repo.actualizar_instrumento(instr)
        
        # 6. Check Parent Payment Status
        await self._check_and_update_payment_status(instr.idPago)

    async def match_manual(self, instrument_id: int, staging_id: int):
        # 1. Get Entities
        instr = await self.portal_repo.obtener_instrumento_por_id(instrument_id)
        staging = await self.staging_repo.buscar_por_id(staging_id) # Need to implement this or use existing find
        
        if not instr or not staging:
             raise ValueError("Instrumento o Transacción Bancaria no encontrados")

        if instr.estatus == 1:
            raise ValueError("Instrumento ya conciliado")
            
        if staging.estatus == 1:
            raise ValueError("Transacción bancaria ya conciliada")

        # 2. Link them (Logical Link - In MVP we just mark both as done and create SBTRAN)
        # Actually, if Staging exists, it implies the Bank already knows about it.
        # BUT, does SBTRAN exist? 
        # Scenario A: Staging is just a raw file import. We need to INSERT into SBTRAN.
        # Scenario B: Staging IS SBTRAN. (In this project, Staging is a separate table 'Staging_Bancos')
        # So we MUST insert into SBTRAN to reflect it in the Accounting System.
        
        await self.erp_txn_repo.registrar_transaccion(staging)
        
        # 3. Update Statuses
        instr.estatus = 1
        await self.portal_repo.actualizar_instrumento(instr)
        
        staging.estatus = 1
        await self.staging_repo.actualizar_staging(staging) # Need to implement
        
        # 4. Check Parent Payment
        await self._check_and_update_payment_status(instr.idPago)

    async def _check_and_update_payment_status(self, pago_id: str):
        # Check if all instruments for this payment are reconciled
        instruments = await self.portal_repo.obtener_instrumentos_por_pago(pago_id)
        all_reconciled = all(i.estatus == 1 for i in instruments)
        
        if all_reconciled:
            pago = await self.portal_repo.obtener_pago_por_id(pago_id)
            pago.status = 1 # CONCILIADO / APROBADO
            pago.conciliado_por = self.current_user
            pago.fecha_conciliacion = datetime.now()
            await self.portal_repo.actualizar_pago(pago)
