from app.domain.repositories.cliente_repository import ClienteRepository
from app.domain.repositories.factura_repository import FacturaRepository
from app.domain.services.cxc_service import CXCService
from app.application.dto.cxc_dto import CXCClienteDTO, FacturaDTO
from typing import Optional

class ConsultarCXCClienteUseCase:
    def __init__(
        self, 
        cliente_repo: ClienteRepository, 
        factura_repo: FacturaRepository,
        cxc_service: CXCService
    ):
        self.cliente_repo = cliente_repo
        self.factura_repo = factura_repo
        self.cxc_service = cxc_service

    async def execute(self, cliente_id: str, sort_by: str = 'antiguedad_dias', order: str = 'desc') -> Optional[CXCClienteDTO]:
        cliente = await self.cliente_repo.obtener_por_id(cliente_id)
        if not cliente:
            return None
            
        facturas = await self.factura_repo.obtener_pendientes_por_cliente(cliente_id)
        
        facturas_dto = [
            FacturaDTO(
                numero=f.numero,
                tipo=f.tipo,
                monto_total=f.monto_total,
                saldo_pendiente=f.saldo_pendiente,
                fecha_emision=f.fecha_emision,
                antiguedad_dias=self.cxc_service.calcular_antiguedad_dias(f.fecha_emision)
            ) for f in facturas
        ]
        
        # Sorting logic with validation
        valid_sort_fields = {'antiguedad_dias', 'saldo_pendiente', 'monto_total', 'fecha_emision'}
        
        if sort_by not in valid_sort_fields:
            # Default to antiguedad_dias if invalid sort_by
            sort_by = 'antiguedad_dias'
        
        reverse = (order == 'desc')
        
        # Sort with proper error handling
        try:
            facturas_dto.sort(key=lambda x: getattr(x, sort_by), reverse=reverse)
        except AttributeError:
            # Fallback to default sorting if attribute doesn't exist
            facturas_dto.sort(key=lambda x: x.antiguedad_dias, reverse=True)
        
        return CXCClienteDTO(
            id=cliente.id,
            descripcion=cliente.descripcion,
            rif=cliente.rif or "",
            saldo_total_ves=cliente.saldo_ves.valor,
            saldo_total_usd=cliente.saldo_usd.valor,
            facturas_pendientes=facturas_dto
        )
