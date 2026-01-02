from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime
import calendar
from app.infrastructure.database.session import get_db
from app.infrastructure.repositories.portal_repository_impl import PortalRepositoryImpl
from app.infrastructure.repositories.bank_mapping_repository_impl import BankMappingRepositoryImpl
from app.infrastructure.repositories.config_repository_impl import ConfigRepositoryImpl
from app.infrastructure.configuration.tasa_service import TasaService
from app.domain.repositories.staging_banco_repository import StagingBancoRepository
from app.infrastructure.repositories.staging_banco_repository_impl import StagingBancoRepositoryImpl
from app.domain.services.reconciliation_service import ReconciliationEngine
from app.application.use_cases.bancos.conciliar_pago import ConciliarPagoUseCase
from app.domain.repositories.erp_transaction_repository import ERPTransactionRepository
from app.infrastructure.saint.erp_transaction_repository_impl import ERPTransactionRepositoryImpl
from app.domain.repositories.erp_cxc_repository import ERPCxCRepository
from app.infrastructure.saint.erp_cxc_repository_impl import ERPCxCRepositoryImpl
from app.domain.repositories.portal_repository import PortalRepository
from app.config import settings

router = APIRouter(prefix="/reconciliation", tags=["Reconciliation"])
templates = Jinja2Templates(directory="app/presentation/web/templates")

@router.get("/inbox", response_class=HTMLResponse)
async def get_reconciliation_inbox(
    request: Request, 
    status: Optional[str] = "1", # Default to PENDIENTE
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    vendedor: Optional[str] = "all",
    db: AsyncSession = Depends(get_db)
):
    """
    Muestra la bandeja de entrada de pagos con filtros de estado, fecha y vendedor.
    Por defecto muestra desde el mes pasado hasta hoy para asegurar visibilidad.
    """
    portal_repo: PortalRepository = PortalRepositoryImpl(db)
    
    now = datetime.now()
    if not start_date:
        # Por defecto, desde hace 3 meses para asegurar visibilidad
        target_month = now.month - 3
        target_year = now.year
        if target_month <= 0:
            target_month += 12
            target_year -= 1
        start_date = datetime(target_year, target_month, 1).strftime('%Y-%m-%d')
    if not end_date:
        # Hasta el último día del mes actual
        _, last_day = calendar.monthrange(now.year, now.month)
        end_date = now.replace(day=last_day).strftime('%Y-%m-%d')

    # Parse filters for query
    try:
        dt_start = datetime.fromisoformat(start_date).replace(hour=0, minute=0, second=0)
        dt_end = datetime.fromisoformat(end_date).replace(hour=23, minute=59, second=59)
    except ValueError:
        dt_start = datetime(now.year, now.month, 1)
        dt_end = now

    status_int = int(status) if status and status != "all" else None
    
    # Get payments and seller list
    pagos = await portal_repo.obtener_pagos_por_status(
        status=status_int,
        start_date=dt_start,
        end_date=dt_end,
        vendedor=vendedor
    )
    
    # DEBUG LOG
    from app.shared.utils.logger import logger
    logger.debug(f"Inbox Route: status_param={status}, status_int={status_int}, count={len(pagos)}")
    if pagos:
        logger.debug(f"Primer pago: ID={pagos[0].idPago}, Status={pagos[0].status} (Type: {type(pagos[0].status)})")
    
    vendedores = await portal_repo.obtener_vendedores_activos()
    
    context = {
        "request": request,
        "title": "Bandeja de Conciliación",
        "pagos": pagos,
        "vendedores": vendedores,
        "filters": {
            "status": str(status),
            "start_date": start_date,
            "end_date": end_date,
            "vendedor": vendedor
        }
    }

    if "HX-Request" in request.headers:
        return templates.TemplateResponse("reconciliation/_pagos_table_partial.html", context)
    
    return templates.TemplateResponse("reconciliation/bandeja_entrada.html", context)

from app.infrastructure.tasks.reconciliation_tasks import conciliar_pago_task
from celery.result import AsyncResult

@router.post("/attempt/{pago_id}", response_class=HTMLResponse)
async def attempt_reconciliation(
    request: Request, 
    pago_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Dispara la tarea de conciliación.
    Si settings.USE_CELERY es True, usa background task. Si no, ejecución síncrona.
    """
    try:
        if settings.USE_CELERY:
            # Trigger Celery Task
            task = conciliar_pago_task.delay(pago_id, "WebUser")
            
            # Return a polling UI (spinner that checks status every 2 seconds)
            return templates.TemplateResponse(
                "reconciliation/_processing_partial.html",
                {"request": request, "task_id": task.id, "pago_id": pago_id}
            )
        else:
            # Synchronous Execution (Fallback)
            # 1. Init Repos
            portal_repo = PortalRepositoryImpl(db)
            staging_repo = StagingBancoRepositoryImpl(db)
            mapping_repo = BankMappingRepositoryImpl(db)
            config_repo = ConfigRepositoryImpl(db)
            tasa_service = TasaService(config_repo, db)
            
            erp_txn_repo = ERPTransactionRepositoryImpl(db)
            erp_cxc_repo = ERPCxCRepositoryImpl(db)
            
            # 2. Init Service & Use Case
            engine = ReconciliationEngine(portal_repo, staging_repo, mapping_repo, tasa_service)
            use_case = ConciliarPagoUseCase(engine, portal_repo, erp_txn_repo, erp_cxc_repo, current_user="WebUser")
            
            # 3. Execute
            await use_case.execute(pago_id)
            
            # 4. Fetch Updated Pago for View
            pago = await portal_repo.obtener_pago_por_id(pago_id)
            
            # 5. Return Updated Row
            return templates.TemplateResponse(
                "reconciliation/_pagos_table_row.html", 
                {"request": request, "pago": pago}
            )

    except Exception as e:
        return templates.TemplateResponse(
            "shared/error_toast.html",
            {"request": request, "message": f"Error al iniciar conciliación: {e}"}
        )

@router.get("/status/{task_id}", response_class=HTMLResponse)
async def check_reconciliation_status(request: Request, task_id: str, db: AsyncSession = Depends(get_db)):
    """
    Endpoint de polling para verificar el estado de la tarea de Celery.
    """
    task_result = AsyncResult(task_id)
    
    if task_result.ready():
        if task_result.successful():
            # Si terminó, buscamos el resultado actualizado en la DB para mostrarlo
            # Reusamos la lógica de instanciar el caso de uso para obtener el resultado limpio
            # o simplemente consultamos el pago.
            # Por simplicidad y consistencia visual, re-ejecutamos la lógica de "ver resultado"
            # que ya teníamos, o reconstruimos el objeto ReconciliationResult.
            
            # Opción rápida: Reconstruir el objeto para la vista
            # Nota: Esto es un poco redundante (leer DB 2 veces), pero asegura que la vista sea consistente.
            
            portal_repo = PortalRepositoryImpl(db)
            # ... (Rest of dependency injection logic if needed to re-render the result view)
            # Actually, the best way is to redirect to a "view result" logic or re-render the row.
            
            # Let's verify the updated status directly from DB
            pago = await portal_repo.obtener_pago_por_id(task_result.result.get("pago_id"))
            
            # Render the updated row
            return templates.TemplateResponse(
                "reconciliation/_pagos_table_row.html", # New partial for a single row
                {"request": request, "pago": pago}
            )
        else:
             return templates.TemplateResponse(
                "shared/error_toast.html",
                {"request": request, "message": f"Fallo en la tarea: {task_result.result}"}
            )
    
    # Si sigue procesando, devolvemos el mismo spinner (o nada, para que HTMX siga esperando)
    # Con HTMX polling, devolvemos el mismo contenido para que siga el ciclo hasta que cambie.
    return templates.TemplateResponse(
        "reconciliation/_processing_partial.html",
        {"request": request, "task_id": task_id}
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

# ==========================================
# Manual Match Workspace Routes (Sprint 3.3)
# ==========================================

@router.get("/match/{pago_id}", response_class=HTMLResponse)
async def get_match_workspace(
    request: Request, 
    pago_id: str, 
    db: AsyncSession = Depends(get_db)
):
    """
    Carga el espacio de trabajo para conciliación manual (Split View).
    """
    portal_repo = PortalRepositoryImpl(db)
    config_repo = ConfigRepositoryImpl(db)
    mapping_repo = BankMappingRepositoryImpl(db)
    tasa_service = TasaService(config_repo, db)
    
    # 1. Fetch Header Info
    pago = await portal_repo.obtener_pago_por_id(pago_id)
    if not pago:
        return templates.TemplateResponse("shared/error_toast.html", {"request": request, "message": "Pago no encontrado"})

    # Fetch Instruments explicitly (since repo returns Domain Entity without relations)
    pago.instrumentos = await portal_repo.obtener_instrumentos_por_pago(pago_id)
    
    # Fetch Documents explicitly (Sprint 3.5 request)
    pago.documentos = await portal_repo.obtener_documentos_por_pago(pago_id)

    # 2. Get System Config
    base_currency = await config_repo.get_config("BASE_CURRENCY") or "USD"
    
    # 3. Process Instruments (View Model)
    instruments_view = []
    for instr in pago.instrumentos:
        # Conversion Logic
        amount_base = instr.monto
        if instr.moneda != base_currency:
            # Try to get rate for instrument date
            rate_config = await tasa_service.get_tasa(instr.fecha, instr.moneda, base_currency)
            if rate_config:
                amount_base = await tasa_service.convertir_a_base(instr.monto, rate_config.tasa)
        
        # Mapping Logic
        mapping = await mapping_repo.get_by_portal_code(instr.banco) # Assuming instr.banco holds the portal code/name
        
        instruments_view.append({
            "id": instr.id,
            "forma_pago": instr.formaPago,
            "fecha": instr.fecha,
            "banco_origen": instr.banco,
            "referencia": instr.nroPlanilla or instr.cheque,
            "amount_orig": instr.monto,
            "currency_orig": instr.moneda,
            "amount_base": amount_base,
            "erp_bank_code": mapping.erp_code if mapping else None,
            "erp_bank_desc": mapping.description if mapping else None,
            "is_cash": mapping.is_cash if mapping else 0
        })

    return templates.TemplateResponse(
        "reconciliation/match_workspace.html",
        {
            "request": request,
            "pago": pago,
            "instruments_view": instruments_view,
            "system_base_currency": base_currency
        }
    )

@router.get("/search-matches", response_class=HTMLResponse)
async def search_staging_matches(
    request: Request,
    instrument_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Busca coincidencias en Staging_Bancos para un instrumento dado.
    Retorna el partial _staging_matches_partial.html
    """
    from app.infrastructure.database.models import GeInstrumentos
    from sqlalchemy import select
    
    # 1. Get Instrument Details
    stmt = select(GeInstrumentos).where(GeInstrumentos.id == instrument_id)
    result = await db.execute(stmt)
    instr = result.scalar_one_or_none()
    
    if not instr:
        return "<div class='p-4 text-red-400'>Instrumento no encontrado</div>"

    # 2. Prepare Services
    staging_repo = StagingBancoRepositoryImpl(db)
    mapping_repo = BankMappingRepositoryImpl(db)
    config_repo = ConfigRepositoryImpl(db)
    tasa_service = TasaService(config_repo, db)
    
    # 3. Determine Search Criteria
    # Map Portal Bank -> ERP Bank
    mapping = await mapping_repo.get_by_portal_code(instr.banco)
    target_bank_code = mapping.erp_code if mapping else None
    
    # CASH HANDLING (Sprint 3.4)
    if mapping and mapping.is_cash:
        return templates.TemplateResponse(
            "reconciliation/_cash_verification_partial.html",
            {
                "request": request, 
                "instrument": instr,
                "mapping": mapping
            }
        )
    
    # Calculate Base Amount for search
    base_currency = await config_repo.get_config("BASE_CURRENCY") or "USD"
    search_amount = instr.monto
    if instr.moneda != base_currency:
         rate_config = await tasa_service.get_tasa(instr.fecha, instr.moneda, base_currency)
         if rate_config:
             search_amount = await tasa_service.convertir_a_base(instr.monto, rate_config.tasa)

    # 4. Execute Search (Using Repo)
    # Note: We need a flexible search method in StagingRepo.
    # For now, we'll implement a basic search here or reuse a repo method if available.
    # Ideally, StagingBancoRepository should have find_candidates(amount, date, bank_code)
    
    candidates = await staging_repo.find_candidates(
        amount=search_amount,
        date_ref=instr.fecha,
        bank_code=target_bank_code,
        tolerance_days=5, # Configurable?
        tolerance_amount=Decimal("0.50") # Configurable?
    )
    
    # 5. Simple Scoring (Presentation Layer Logic or Helper)
    scored_matches = []
    for cand in candidates:
        score = 0
        # Exact Amount
        if abs(cand.monto - search_amount) < Decimal("0.01"):
            score += 50
        elif abs(cand.monto - search_amount) < Decimal("1.00"):
            score += 30
            
        # Exact Date
        days_diff = abs((cand.fecha - instr.fecha).days)
        if days_diff == 0:
            score += 30
        elif days_diff <= 2:
            score += 15
            
        # Ref Match
        ref_instr = (instr.nroPlanilla or instr.cheque or "").strip()[-4:]
        ref_cand = cand.referencia.strip()[-4:]
        if ref_instr and ref_instr in cand.referencia:
             score += 20
        
        cand.score = min(score, 100) # Monkey patch for view
        scored_matches.append(cand)

    # Sort by score
    scored_matches.sort(key=lambda x: x.score, reverse=True)

    return templates.TemplateResponse(
        "reconciliation/_staging_matches_partial.html",
        {"request": request, "matches": scored_matches}
    )

from app.application.use_cases.bancos.manual_reconciliation import ManualReconciliationUseCase

@router.post("/match-manual", response_class=HTMLResponse)
async def manual_match_submit(
    request: Request,
    instrument_id: int,
    staging_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Initialize Use Case
        use_case = ManualReconciliationUseCase(
            portal_repo=PortalRepositoryImpl(db),
            erp_txn_repo=ERPTransactionRepositoryImpl(db),
            mapping_repo=BankMappingRepositoryImpl(db),
            staging_repo=StagingBancoRepositoryImpl(db)
        )
        
        await use_case.match_manual(instrument_id, staging_id)
        
        return templates.TemplateResponse(
            "shared/success_toast.html",
            {"request": request, "message": "Conciliación manual exitosa."}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return templates.TemplateResponse(
            "shared/error_toast.html",
            {"request": request, "message": f"Error: {str(e)}"}
        )

@router.post("/approve-cash", response_class=HTMLResponse)
async def approve_cash_submit(
    request: Request,
    instrument_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Initialize Use Case
        use_case = ManualReconciliationUseCase(
            portal_repo=PortalRepositoryImpl(db),
            erp_txn_repo=ERPTransactionRepositoryImpl(db),
            mapping_repo=BankMappingRepositoryImpl(db),
            staging_repo=StagingBancoRepositoryImpl(db)
        )
        
        await use_case.reconcile_cash(instrument_id)
        
        return templates.TemplateResponse(
            "shared/success_toast.html",
            {"request": request, "message": "Pago en efectivo aprobado y registrado."}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return templates.TemplateResponse(
            "shared/error_toast.html",
            {"request": request, "message": f"Error: {str(e)}"}
        )
