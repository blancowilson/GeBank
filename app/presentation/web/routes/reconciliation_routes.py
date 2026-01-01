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

from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/reconciliation", tags=["Reconciliation"])
templates = Jinja2Templates(directory="app/presentation/web/templates")

import calendar

@router.get("/inbox", response_class=HTMLResponse)
async def get_reconciliation_inbox(
    request: Request, 
    status: Optional[str] = "1", # Default to PENDIENTE
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Muestra la bandeja de entrada de pagos con filtros de estado y fecha.
    Por defecto muestra el mes actual.
    """
    insytech_repo: InsytechRepository = InsytechRepositoryImpl(db)
    
    now = datetime.now()
    if not start_date:
        start_date = now.replace(day=1).strftime('%Y-%m-%d')
    if not end_date:
        _, last_day = calendar.monthrange(now.year, now.month)
        end_date = now.replace(day=last_day).strftime('%Y-%m-%d')

    # Parse filters for query
    status_int = int(status) if status and status != "all" else None
    dt_start = datetime.fromisoformat(start_date).replace(hour=0, minute=0, second=0)
    dt_end = datetime.fromisoformat(end_date).replace(hour=23, minute=59, second=59)
    
    pagos = await insytech_repo.obtener_pagos_por_status(
        status=status_int,
        start_date=dt_start,
        end_date=dt_end
    )
    
    context = {
        "request": request,
        "title": "Bandeja de Conciliación",
        "pagos": pagos,
        "filters": {
            "status": status,
            "start_date": start_date,
            "end_date": end_date
        }
    }

    if "HX-Request" in request.headers:
        return templates.TemplateResponse("reconciliation/_pagos_table_partial.html", context)
    
    return templates.TemplateResponse("reconciliation/bandeja_entrada.html", context)

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
        import traceback
        traceback.print_exc() # Print full stack trace to terminal
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
