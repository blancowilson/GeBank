from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.session import get_db
from app.application.use_cases.insytech.receive_payment_packet import ReceivePaymentPacketUseCase
from app.application.dto.insytech_dto import PaymentPacketDTO
from app.domain.repositories.portal_repository import PortalRepository
from app.infrastructure.repositories.portal_repository_impl import PortalRepositoryImpl
from app.infrastructure.saint.erp_cliente_repository_impl import ERPClienteRepositoryImpl

router = APIRouter()

@router.post("/integration/payments", status_code=status.HTTP_201_CREATED)
async def receive_insytech_payment(packet: PaymentPacketDTO, db: AsyncSession = Depends(get_db)):
    """
    Endpoint para recibir paquetes de pago desde el portal de Insytech.
    """
    portal_repo: PortalRepository = PortalRepositoryImpl(db)
    cliente_repo = ERPClienteRepositoryImpl(db)
    use_case = ReceivePaymentPacketUseCase(portal_repo, cliente_repo)
    
    try:
        # Pydantic validation handles basic schema, use case handles business rules
        ge_pagos = await use_case.execute(packet)
        return {"message": "Payment packet received and persisted successfully", "idPago": ge_pagos.idPago}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")
