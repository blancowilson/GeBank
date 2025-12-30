import pandas as pd
import io
from typing import List
from .base import BaseStatementParser, TransactionRow

class InsytechExcelParser(BaseStatementParser):
    """
    Parser preliminar para archivos de Excel de Insytech.
    Esperando definición final de columnas.
    """

    def validate_format(self, file_content: bytes, filename: str) -> bool:
        return filename.endswith(('.xls', '.xlsx'))

    def parse(self, file_content: bytes, filename: str) -> List[TransactionRow]:
        try:
            # Leemos el excel en memoria
            df = pd.read_excel(io.BytesIO(file_content))
            
            transactions = []
            
            # TODO: Ajustar nombres de columnas cuando tengamos el formato real
            # Lógica simulada:
            for index, row in df.iterrows():
                # Buscamos columnas probables o usamos placeholders
                fecha = row.get('Fecha', 'N/A')
                desc = row.get('Descripción', 'Sin descripción')
                ref = row.get('Referencia', str(index))
                monto = row.get('Monto', 0.0)
                
                # Determinamos tipo (esto es logica placeholder)
                tipo = 'CREDIT' if monto > 0 else 'DEBIT'

                txn = TransactionRow(
                    raw_date=str(fecha),
                    description=str(desc),
                    reference=str(ref),
                    amount=float(monto),
                    currency='USD', # Asumimos USD por defecto en Insytech
                    transaction_type=tipo,
                    bank_name='INSYTECH_GENERIC',
                    original_row_data=row.to_dict()
                )
                transactions.append(txn)
                
            return transactions

        except Exception as e:
            # En producción, usaríamos el audit_logger aquí
            print(f"Error parseando archivo Insytech: {e}")
            return []
