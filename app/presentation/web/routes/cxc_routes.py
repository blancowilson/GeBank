from fastapi import APIRouter, Request, Depends, Form
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

router = APIRouter()
templates = Jinja2Templates(directory="app/presentation/web/templates")

@router.get("/clientes")
async def listar_clientes(request: Request, db: AsyncSession = Depends(get_db)):
    repo = SaintClienteRepository(db)
    clientes = await repo.obtener_todos()
    return templates.TemplateResponse(
        "cxc/listado_clientes.html", 
        {"request": request, "clientes": clientes, "title": "Listado de Clientes - CXC"}
    )

@router.get("/cliente/{cliente_id}/facturas")
async def detalle_facturas(request: Request, cliente_id: str, db: AsyncSession = Depends(get_db)):
    cliente_repo = SaintClienteRepository(db)
    factura_repo = SaintFacturaRepository(db)
    cxc_service = CXCService()
    use_case = ConsultarCXCClienteUseCase(cliente_repo, factura_repo, cxc_service)
    
    cxc_data = await use_case.execute(cliente_id)
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
