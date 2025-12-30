from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.session import get_db
from app.infrastructure.saint.saint_cliente_repository import SaintClienteRepository
from app.infrastructure.saint.saint_factura_repository import SaintFacturaRepository
from app.infrastructure.saint.saint_pago_repository import SaintPagoRepository
from app.domain.services.cxc_service import CXCService
from app.application.use_cases.cxc.consultar_cxc_cliente import ConsultarCXCClienteUseCase
from app.application.use_cases.cxc.registrar_pago_manual import RegistrarPagoManualUseCase
from app.domain.value_objects.monto import Moneda
from decimal import Decimal
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="app/presentation/web/templates")

@router.get("/clientes", name="listar_clientes")
async def listar_clientes(
    request: Request, 
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("deuda"),
    order: Optional[str] = Query("desc")
):
    repo = SaintClienteRepository(db)
    page_size = 20
    skip = (page - 1) * page_size
    
    if search:
        clientes, total_count = await repo.buscar_por_nombre(search, skip=skip, limit=page_size, sort_by=sort_by, order=order)
    else:
        clientes, total_count = await repo.obtener_todos(skip=skip, limit=page_size, sort_by=sort_by, order=order)

    total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1
    
    total_pagina_usd = sum(c.saldo_usd.valor for c in clientes)
    
    context = {
        "request": request,
        "clientes": clientes,
        "total_pagina_usd": total_pagina_usd,
        "pagination": {
            "current_page": page, "total_pages": total_pages, "total_items": total_count,
            "page_size": page_size, "next_page": page + 1 if page < total_pages else None,
            "prev_page": page - 1 if page > 1 else None,
        },
        "title": "Listado de Clientes - CXC"
    }

    if "HX-Request" in request.headers:
        return templates.TemplateResponse("cxc/_clientes_table_partial.html", context)
    
    return templates.TemplateResponse("cxc/listado_clientes.html", context)

@router.get("/cliente/{cliente_id}/facturas")
async def detalle_facturas(
    request: Request, 
    cliente_id: str, 
    db: AsyncSession = Depends(get_db),
    sort_by: str = Query('antiguedad_dias'),
    order: str = Query('desc')
):
    cliente_repo = SaintClienteRepository(db)
    factura_repo = SaintFacturaRepository(db)
    cxc_service = CXCService()
    use_case = ConsultarCXCClienteUseCase(cliente_repo, factura_repo, cxc_service)
    
    cxc_data = await use_case.execute(cliente_id, sort_by=sort_by, order=order)

    # For HTMX sort requests, return only the table body
    if "HX-Request" in request.headers:
        return templates.TemplateResponse(
            "cxc/_facturas_table_rows.html",
            {"request": request, "facturas": cxc_data.facturas_pendientes if cxc_data else []}
        )
        
    return templates.TemplateResponse(
        "cxc/detalle_facturas.html",
        {"request": request, "cxc": cxc_data}
    )

@router.post("/pago/registrar")
async def registrar_pago(
    request: Request,
    cliente_id: str = Form(...),
    factura_numero: str = Form(...),
    monto: Decimal = Form(...),
    moneda: str = Form(...),
    referencia: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    pago_repo = SaintPagoRepository(db)
    factura_repo = SaintFacturaRepository(db)
    use_case = RegistrarPagoManualUseCase(pago_repo, factura_repo)
    
    try:
        await use_case.execute(
            cliente_id=cliente_id,
            factura_numero=factura_numero,
            monto_valor=monto,
            moneda=Moneda(moneda),
            referencia=referencia,
            usuario="Admin" # Hardcoded for now
        )
        return templates.TemplateResponse(
            "shared/success_toast.html",
            {"request": request, "message": "Pago registrado exitosamente"}
        )
    except Exception as e:
        return templates.TemplateResponse(
            "shared/error_toast.html",
            {"request": request, "message": str(e)}
        )