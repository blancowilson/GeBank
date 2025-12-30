from fastapi import APIRouter, Request, UploadFile, File, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

from app.infrastructure.parsers.insytech_parser import InsytechExcelParser

router = APIRouter(prefix="/bancos", tags=["bancos"])
templates = Jinja2Templates(directory="app/presentation/web/templates")

@router.get("/subir", response_class=HTMLResponse)
async def ver_subir_estado_cuenta(request: Request):
    """
    Renderiza la vista de carga de estados de cuenta.
    """
    return templates.TemplateResponse(
        "bancos/subir_estado_cuenta.html", 
        {"request": request, "title": "Cargar Estado de Cuenta"}
    )

@router.post("/upload", response_class=HTMLResponse)
async def procesar_archivo_banco(
    request: Request,
    file: UploadFile = File(...),
    format: str = Form(...),
    simulate: Optional[bool] = Form(False)
):
    """
    Procesa el archivo subido usando el parser correspondiente y retorna
    los resultados del análisis simulado.
    """
    content = await file.read()
    filename = file.filename
    
    # Selección simple de parser (por ahora solo Insytech/Excel simulado)
    # En el futuro usaríamos una Factory
    parser = InsytechExcelParser()
    
    transactions = parser.parse(content, filename)
    
    # Calcular estadísticas simples para la vista
    total_txns = len(transactions)
    # Simulamos que el 60% hace match automático
    conciliados = int(total_txns * 0.6) 
    pendientes = int(total_txns * 0.3)
    sin_match = total_txns - conciliados - pendientes
    
    stats = {
        "total": total_txns,
        "conciliados": conciliados,
        "porcentaje_conciliado": int((conciliados / total_txns * 100)) if total_txns > 0 else 0,
        "pendientes": pendientes,
        "sin_match": sin_match
    }

    return templates.TemplateResponse(
        "bancos/_analisis_resultados.html",
        {
            "request": request, 
            "transacciones": transactions,
            "stats": stats
        }
    )
