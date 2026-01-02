from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.session import get_db
from app.infrastructure.repositories.config_repository_impl import ConfigRepositoryImpl
from typing import Optional

router = APIRouter(prefix="/configuracion", tags=["Configuración"])
templates = Jinja2Templates(directory="app/presentation/web/templates")

from app.infrastructure.database.models import ExchangeRate
from sqlalchemy import select

from app.infrastructure.repositories.bank_mapping_repository_impl import BankMappingRepositoryImpl
from app.domain.repositories.bank_mapping_repository import BankMappingDTO
from app.infrastructure.saint.erp_banco_repository_impl import ERPBancoRepositoryImpl
from app.infrastructure.configuration.tasa_service import TasaService
from decimal import Decimal

@router.get("/tasas", response_class=HTMLResponse)
async def get_rates_config(request: Request, db: AsyncSession = Depends(get_db)):
    repo = ConfigRepositoryImpl(db)
    service = TasaService(repo, db)
    
    # Access internal list directly for config view
    # In a perfect world, we'd have a specific DTO or getter
    tasas = service._tasas 
    
    return templates.TemplateResponse(
        "configuracion/tasas.html",
        {
            "request": request,
            "title": "Configuración de Tasas",
            "tasas": tasas
        }
    )

@router.post("/tasas/actualizar", response_class=HTMLResponse)
async def update_rate_config(
    request: Request,
    key: str = Form(...),
    valor: str = Form(...),
    es_referencia_divisa: bool = Form(False),
    db: AsyncSession = Depends(get_db)
):
    repo = ConfigRepositoryImpl(db)
    service = TasaService(repo, db)
    
    try:
        service.update_tasa(
            key=key,
            nuevo_valor=Decimal(valor),
            es_referencia_divisa=es_referencia_divisa
        )
        return templates.TemplateResponse(
            "shared/success_toast.html",
            {"request": request, "message": "Tasa actualizada correctamente."}
        )
    except Exception as e:
        return templates.TemplateResponse(
            "shared/error_toast.html",
            {"request": request, "message": f"Error actualizando tasa: {str(e)}"}
        )

@router.get("/bancos/mapeo", response_class=HTMLResponse)
async def get_bank_mappings(request: Request, db: AsyncSession = Depends(get_db)):
    mapping_repo = BankMappingRepositoryImpl(db)
    erp_banco_repo = ERPBancoRepositoryImpl(db)
    
    mappings = await mapping_repo.get_all()
    erp_bancos = await erp_banco_repo.get_all()
    
    return templates.TemplateResponse(
        "config/bank_mapping.html",
        {
            "request": request,
            "title": "Mapeo de Bancos",
            "mappings": mappings,
            "erp_bancos": erp_bancos
        }
    )

@router.post("/bancos/mapeo", response_class=HTMLResponse)
async def save_bank_mapping(
    request: Request,
    portal_code: str = Form(...),
    erp_code: str = Form(...),
    description: Optional[str] = Form(None),
    is_cash: bool = Form(False),
    currency: str = Form('USD'),
    mapping_id: Optional[int] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    repo = BankMappingRepositoryImpl(db)
    mapping = BankMappingDTO(
        id=mapping_id,
        portal_code=portal_code,
        erp_code=erp_code,
        description=description,
        is_cash=is_cash,
        currency=currency
    )
    await repo.save(mapping)
    
    # Redirigir o devolver la tabla actualizada
    return RedirectResponse(url="/configuracion/bancos/mapeo", status_code=303)

@router.delete("/bancos/mapeo/{mapping_id}", response_class=HTMLResponse)
async def delete_bank_mapping(mapping_id: int, db: AsyncSession = Depends(get_db)):
    repo = BankMappingRepositoryImpl(db)
    await repo.delete(mapping_id)
    return HTMLResponse(content="") # HTMX eliminará la fila

@router.get("/tasas/historial", response_class=HTMLResponse)
async def get_rate_history(request: Request, db: AsyncSession = Depends(get_db)):
    # Consultar todas las tasas de la base de datos ordenadas por fecha descendente
    stmt = select(ExchangeRate).order_by(ExchangeRate.fecha.desc())
    result = await db.execute(stmt)
    rates = result.scalars().all()
    
    return templates.TemplateResponse(
        "config/rate_history.html",
        {
            "request": request,
            "title": "Historial de Tasas de Cambio",
            "rates": rates
        }
    )

@router.get("/ajustes", response_class=HTMLResponse)
async def get_settings(request: Request, db: AsyncSession = Depends(get_db)):
    repo = ConfigRepositoryImpl(db)
    
    # Obtener valores actuales o usar por defecto
    base_currency = await repo.get_config("BASE_CURRENCY") or "USD"
    ref_currency = await repo.get_config("REF_CURRENCY") or "VES"
    rate_operator = await repo.get_config("RATE_OPERATOR") or "MULTIPLY"
    tolerance = await repo.get_config("RECONCILIATION_TOLERANCE") or "0.01"
    
    return templates.TemplateResponse(
        "config/settings.html",
        {
            "request": request,
            "title": "Configuración del Sistema",
            "config": {
                "base_currency": base_currency,
                "ref_currency": ref_currency,
                "rate_operator": rate_operator,
                "tolerance": tolerance
            }
        }
    )

@router.post("/ajustes", response_class=HTMLResponse)
async def save_settings(
    request: Request,
    base_currency: str = Form(...),
    ref_currency: str = Form(...),
    rate_operator: str = Form(...),
    tolerance: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    repo = ConfigRepositoryImpl(db)
    
    await repo.set_config("BASE_CURRENCY", base_currency)
    await repo.set_config("REF_CURRENCY", ref_currency)
    await repo.set_config("RATE_OPERATOR", rate_operator)
    await repo.set_config("RECONCILIATION_TOLERANCE", tolerance)
    
    # Devolver un aviso de éxito (podría ser un toast con HTMX)
    return templates.TemplateResponse(
        "shared/success_toast.html",
        {"request": request, "message": "Configuración guardada exitosamente."}
    )