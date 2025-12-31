from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.repositories.saint_transaction_repository import SaintTransactionRepository
from app.domain.entities.staging_transaction import StagingTransaction
from app.infrastructure.database.models import SbTran

class SaintTransactionRepositoryImpl(SaintTransactionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def registrar_transaccion(self, transaccion: StagingTransaction) -> None:
        """
        Convierte una StagingTransaction a un registro de SBTRAN y lo inserta.
        Nota: Esta es una implementación simplificada. La lógica para campos
        como 'NOpe', 'TipoOpe', 'CodOper' puede ser más compleja y requerir
        secuencias o configuraciones de Saint.
        """
        
        # Mapeo de Staging a SBTRAN
        # La lógica para generar NOpe (número de operación) es crucial en Saint
        # Aquí se usa un placeholder simple.
        # En un caso real, podría venir de una tabla de correlativos (SACORRELSIS).
        
        # Asumimos que el 'tipo_movimiento' DEBITO/CREDITO debe mapearse
        # a los valores numéricos de 'TipoOpe' de Saint.
        # Placeholder: 1=Credito(Deposito), 2=Debito(Cheque/ND)
        tipo_ope_saint = 1 if transaccion.tipo_movimiento == 'CREDITO' else 2

        db_tran = SbTran(
            CodBanc=transaccion.cod_banco,
            Fecha=transaccion.fecha,
            NOpe=0,  # Placeholder - DEBE ser un número único de operación
            TipoOpe=tipo_ope_saint,
            CodOper="CON", # Placeholder para "Conciliacion"
            Monto=transaccion.monto,
            MtoCr=transaccion.monto if transaccion.tipo_movimiento == 'CREDITO' else 0,
            MtoDb=transaccion.monto if transaccion.tipo_movimiento == 'DEBITO' else 0,
            Descrip=(transaccion.descripcion or "")[:60], # Handle None
            Beneficiario=(transaccion.descripcion or "").split(' ')[0][:50], # Handle None
            Estado=2, # 2 = conciliado
            Consolidado=0 # 0 = no consolidado
        )
        
        self.session.add(db_tran)
        # El commit se manejará en el use case para asegurar la atomicidad de la operación
