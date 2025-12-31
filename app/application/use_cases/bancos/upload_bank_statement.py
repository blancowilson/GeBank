from typing import List
from datetime import datetime
from app.domain.services.parser_service import BankFileParserService
from app.domain.repositories.staging_banco_repository import StagingBancoRepository
from app.domain.entities.staging_transaction import StagingTransaction

class UploadBankStatementUseCase:
    def __init__(self, parser_service: BankFileParserService, staging_repo: StagingBancoRepository):
        self.parser_service = parser_service
        self.staging_repo = staging_repo

    async def execute(self, bank_id: str, file_type: str, file_content: bytes, filename: str) -> List[StagingTransaction]:
        # 1. Parse the file to get normalized transaction rows
        transaction_rows = self.parser_service.parse_file(bank_id, file_type, file_content, filename)
        
        # 2. Convert TransactionRow objects to StagingTransaction domain entities
        staging_transactions = []
        for row in transaction_rows:
            # Attempt to parse date, assuming YYYY-MM-DD format for now.
            try:
                # Handle cases where raw_date might be a datetime object from pandas already
                if isinstance(row.raw_date, datetime):
                    parsed_date = row.raw_date
                else:
                    # Try parsing from a common string format
                    parsed_date = datetime.strptime(str(row.raw_date).split(" ")[0], '%Y-%m-%d')
            except ValueError:
                # If parsing fails, use a default or handle the error
                parsed_date = datetime.now() # Fallback, should be logged

            staging_transactions.append(StagingTransaction(
                id=None,
                cod_banco=row.bank_name, # Or a mapped bank_id
                referencia=row.reference,
                fecha=parsed_date,
                monto=row.amount,
                moneda=row.currency,
                tipo_movimiento=row.transaction_type,
                descripcion=row.description,
                estatus=StagingTransaction.PENDIENTE,
                nombre_archivo=filename
            ))
        
        # 3. Persist the batch of transactions to the staging table
        await self.staging_repo.guardar_lote(staging_transactions)
        
        return staging_transactions
