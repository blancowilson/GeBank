from typing import List, Optional
from decimal import Decimal
from app.domain.entities.pago_insytech import GePagos, GeInstrumentos
from app.domain.repositories.portal_repository import PortalRepository
from app.domain.repositories.staging_banco_repository import StagingBancoRepository
from app.domain.repositories.bank_mapping_repository import IBankMappingRepository
from app.infrastructure.configuration.tasa_service import TasaService
from app.domain.entities.reconciliation import ReconciliationResult, MatchResult

class ReconciliationEngine:
    def __init__(
        self,
        portal_repo: PortalRepository,
        staging_repo: StagingBancoRepository,
        mapping_repo: IBankMappingRepository,
        tasa_service: TasaService
    ):
        self.portal_repo = portal_repo
        self.staging_repo = staging_repo
        self.mapping_repo = mapping_repo
        self.tasa_service = tasa_service

    async def attempt_reconciliation(self, pago_id: str) -> ReconciliationResult:
        """
        Orchestrates the matching of all instruments in a payment packet.
        """
        # 1. Fetch the payment packet from Portal tables
        pago = await self.portal_repo.obtener_pago_por_id(pago_id)
        if not pago:
            raise ValueError(f"Payment with ID {pago_id} not found.")

        instrumentos = await self.portal_repo.obtener_instrumentos_por_pago(pago_id)

        match_results: List[MatchResult] = []

        # 2. Iterate through each financial instrument of the payment
        for instr in instrumentos:
            match_result = MatchResult(instrumento=instr)
            
            # Map Portal Bank -> ERP Bank (Sprint 3.1)
            mapping = await self.mapping_repo.get_by_portal_code(instr.banco)
            erp_bank_code = mapping.erp_code if mapping else instr.banco

            # Handle different payment methods
            if instr.formaPago in ['TRANSFERENCIA', 'DEPOSITO', 'CHEQUE']:
                # Logic for bank transactions
                if instr.moneda == 'USD':
                    # Direct match for USD
                    staging_txn = await self.staging_repo.buscar_por_referencia_y_monto(
                        referencia=instr.nroPlanilla,
                        monto=instr.monto,
                        cod_banco=erp_bank_code
                    )
                    if staging_txn:
                        match_result.match_found = True
                        match_result.staging_txn = staging_txn
                        match_result.details = "Match directo en USD por referencia y monto."
                        match_result.converted_amount_usd = instr.monto # Already in USD
                    else:
                        match_result.details = "No se encontró transacción en Staging para referencia y monto en USD."

                elif instr.moneda == 'VES':
                    # Complex match for VES
                    # First, find the rate to convert
                    tasa_obj = self.tasa_service.get_tasa(instr.fecha, 'VES', 'USD')
                    if not tasa_obj:
                        match_result.details = "No se encontró tasa de cambio para la fecha."
                        match_results.append(match_result)
                        continue

                    # Converted amount for reference
                    tasa_valor = tasa_obj.valor
                    converted_usd = instr.monto / tasa_valor if tasa_valor > 0 else Decimal("0")
                    match_result.converted_amount_usd = converted_usd

                    # Find a matching transaction in staging (logic could be more complex, e.g., amount ranges)
                    staging_txn = await self.staging_repo.buscar_por_referencia_y_monto(
                        referencia=instr.nroPlanilla,
                        monto=instr.monto,
                        cod_banco=erp_bank_code
                    )

                    if staging_txn:
                        match_result.match_found = True
                        match_result.staging_txn = staging_txn
                        match_result.details = f"Match en VES. Monto Bs. {instr.monto:,.2f} equivale a aprox. ${converted_usd:,.2f} (Tasa: {tasa_valor})."
                    else:
                        match_result.details = f"No se encontró transacción en Staging para Bs. {instr.monto:,.2f} con referencia {instr.nroPlanilla}."
                
            elif instr.formaPago == 'EFECTIVO':
                # Logic for cash payments ("Caja Virtual")
                match_result.match_found = True # Or requires manual approval
                match_result.details = "Pago en efectivo, requiere validación manual de caja."
                match_result.converted_amount_usd = instr.monto if instr.moneda == 'USD' else None # Add conversion if needed

            else:
                match_result.details = f"Forma de pago '{instr.formaPago}' no manejada por el motor de conciliación."

            match_results.append(match_result)

        return ReconciliationResult(pago=pago, instrument_matches=match_results)
