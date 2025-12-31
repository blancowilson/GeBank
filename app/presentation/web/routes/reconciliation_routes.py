from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.session import get_db
from app.infrastructure.repositories.insytech_repository_impl import InsytechRepositoryImpl
from app.infrastructure.configuration.tasa_service import TasaService
from app.domain.repositories.staging_banco_repository import StagingBancoRepository
from app.infrastructure.repositories.staging_banco_repository_impl import StagingBancoRepositoryImpl
from app.domain.services.reconciliation_service import ReconciliationEngine
from app.application.use_cases.bancos.conciliar_pago import ConciliarPagoUseCase
from app.domain.repositories.saint_transaction_repository import SaintTransactionRepository
from app.infrastructure.saint.saint_transaction_repository_impl import SaintTransactionRepositoryImpl
from app.domain.repositories.saint_cxc_repository import SaintCxCRepository
from app.infrastructure.saint.saint_cxc_repository_impl import SaintCxCRepositoryImpl
from app.infrastructure.saint.saint_banco_repository import SaintBancoRepository
from app.domain.repositories.insytech_repository import InsytechRepository
from app.infrastructure.repositories.insytech_repository_impl import InsytechRepositoryImpl

router = APIRouter(prefix="/reconciliation", tags=["Reconciliation"])
templates = Jinja2Templates(directory="app/presentation/web/templates")

@router.get("/inbox", response_class=HTMLResponse)
async def get_reconciliation_inbox(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Muestra la bandeja de entrada de pagos pendientes de conciliar.
    """
    insytech_repo: InsytechRepository = InsytechRepositoryImpl(db)
    
    pagos_pendientes = await insytech_repo.obtener_pagos_por_status(1) # Status 1 = PENDIENTE
    
    return templates.TemplateResponse(
        "reconciliation/bandeja_entrada.html",
        {
            "request": request,
            "title": "Bandeja de Conciliación",
            "pagos": pagos_pendientes
        }
    )

@router.post("/attempt/{pago_id}", response_class=HTMLResponse)
async def attempt_reconciliation(request: Request, pago_id: str, db: AsyncSession = Depends(get_db)):
    """
    Ejecuta el motor de conciliación para un pago específico y devuelve el resultado.
    """
    try:
        # Dependency Injection
        insytech_repo = InsytechRepositoryImpl(db)
        staging_repo = StagingBancoRepositoryImpl(db)
        tasa_service = TasaService()
        saint_txn_repo = SaintTransactionRepositoryImpl(db)
        saint_cxc_repo = SaintCxCRepositoryImpl(db)
        engine = ReconciliationEngine(insytech_repo, staging_repo, tasa_service)
        use_case = ConciliarPagoUseCase(engine, insytech_repo, saint_txn_repo, saint_cxc_repo)

        # Execution
        result = await use_case.execute(pago_id)

        return templates.TemplateResponse(
            "reconciliation/_reconciliation_result.html",
            {"request": request, "result": result}
        )
    except Exception as e:
        return templates.TemplateResponse(
            "shared/error_toast.html",
            {"request": request, "message": f"Error de conciliación: {e}"}
        )

@router.get("/image-viewer", response_class=HTMLResponse)
async def get_image_viewer(request: Request, url: str):
    """
    Muestra una imagen en un modal a partir de una URL.
    """
    return templates.TemplateResponse(
        "reconciliation/image-viewer.html",
        {"request": request, "url": url}
    )
