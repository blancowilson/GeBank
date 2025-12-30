from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.infrastructure.configuration.tasa_service import TasaService

router = APIRouter(prefix="/configuracion", tags=["configuracion"])
templates = Jinja2Templates(directory="app/presentation/web/templates")
tasa_service = TasaService()

@router.get("/tasas", response_class=HTMLResponse)
async def ver_tasas(request: Request):
    tasas = tasa_service.get_all()
    return templates.TemplateResponse(
        "configuracion/tasas.html",
        {"request": request, "tasas": tasas}
    )

@router.post("/tasas/actualizar")
async def actualizar_tasa(
    request: Request,
    key: str = Form(...),
    valor: float = Form(...)
):
    tasa_service.update_tasa(key, valor)
    # Retornamos un header HTMX para que muestre un toast o simplemente recargamos
    # Por simplicidad ahora, redirigimos a la misma página
    return RedirectResponse(url="/configuracion/tasas", status_code=303)
