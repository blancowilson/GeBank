import pandas as pd
import io
from typing import List
from decimal import Decimal
from app.infrastructure.parsers.base import BaseStatementParser, TransactionRow

class BanescoExcelParser(BaseStatementParser):
    """
    Parser para el formato de estado de cuenta de Banesco en Excel.
    Asume una estructura de columnas específica que debe ser validada y ajustada.
    """
    supported_file_types = ['.xls', '.xlsx']

    def parse(self, file_content: bytes, filename: str) -> List[TransactionRow]:
        try:
            # Lectura del archivo Excel, asumiendo que los datos empiezan en la fila 10 (header=9)
            df = pd.read_excel(io.BytesIO(file_content), header=9)
            
            transactions = []
            
            # Columnas esperadas (ajustar según el formato real)
            # Esto es una suposición y la parte más frágil del parser.
            # En un caso real, esto sería mucho más robusto.
            FECHA_COL = 'Fecha'
            DESC_COL = 'Descripción'
            REF_COL = 'Referencia'
            DEBITO_COL = 'Monto Débito'
            CREDITO_COL = 'Monto Crédito'
            
            for index, row in df.iterrows():
                # Determinar si es un débito o un crédito y obtener el monto
                monto = Decimal("0.00")
                tipo_movimiento = None
                
                credito = row.get(CREDITO_COL, 0)
                debito = row.get(DEBITO_COL, 0)

                if pd.notna(credito) and Decimal(str(credito)) > 0:
                    monto = Decimal(str(credito))
                    tipo_movimiento = 'CREDITO'
                elif pd.notna(debito) and Decimal(str(debito)) > 0:
                    monto = Decimal(str(debito))
                    tipo_movimiento = 'DEBITO'
                else:
                    continue # Fila no válida o sin monto

                fecha_raw = row.get(FECHA_COL, '')
                descripcion = row.get(DESC_COL, '')
                referencia = str(row.get(REF_COL, ''))
                
                # Crear la fila de transacción normalizada
                txn = TransactionRow(
                    raw_date=str(fecha_raw),
                    description=descripcion,
                    reference=referencia,
                    amount=monto,
                    currency='VES', # Asumir VES para Banesco, podría ser configurable
                    transaction_type=tipo_movimiento,
                    bank_name='Banesco', # Hardcoded for this parser
                    original_row_data=row.to_dict()
                )
                transactions.append(txn)
            
            print(f"Parsed {len(transactions)} transactions.")
            return transactions

        except Exception as e:
            # Loggear el error en un sistema de logging real
            print(f"Error parseando archivo de Banesco: {e}")
            # Retornar una lista vacía o lanzar una excepción específica
            return []
