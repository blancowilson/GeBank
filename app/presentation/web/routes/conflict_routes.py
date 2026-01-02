from app.presentation.web.routes.reconciliation_routes import router, templates
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.session import get_db
from app.infrastructure.repositories.portal_repository_impl import PortalRepositoryImpl
from app.infrastructure.repositories.config_repository_impl import ConfigRepositoryImpl
from app.infrastructure.configuration.tasa_service import TasaService
from app.domain.entities.pago_insytech import GePagos

@router.get("/resolve/{pago_id}")
async def resolve_conflict_view(request: Request, pago_id: str, db: AsyncSession = Depends(get_db)):
    """
    Pantalla para resolver conflictos de conciliación (referencias erradas, tasas incorrectas).
    """
    portal_repo = PortalRepositoryImpl(db)
    tasa_service = TasaService(config_repo=ConfigRepositoryImpl(db), session=db)
    
    # 1. Obtener Pago e Instrumentos
    pago = await portal_repo.obtener_pago_por_id(pago_id)
    if not pago:
        return templates.TemplateResponse("shared/error_toast.html", {"request": request, "message": "Pago no encontrado"})
        
    instrumentos = await portal_repo.obtener_instrumentos_por_pago(pago_id)
    documentos = await portal_repo.obtener_documentos_por_pago(pago_id)
    
    pago.instrumentos = instrumentos
    pago.documentos = documentos
    
    # 2. Análisis de Tasas por Instrumento
    analisis_instrumentos = []
    for instr in instrumentos:
        item = {
            "instr": instr,
            "tasa_sistema": None,
            "sugerencia": None
        }
        
        # Si es moneda extranjera (o diferente a base), buscar tasa del sistema
        if instr.moneda != 'USD': # Asumiendo USD como base por ahora, debería usar config
             tasa_sis = await tasa_service.get_tasa(instr.fecha, instr.moneda, 'USD')
             if tasa_sis:
                 item["tasa_sistema"] = tasa_sis.tasa
                 
                 # Comparar tasa reportada vs sistema
                 tasa_reportada = instr.tasa or 0
                 if abs(tasa_reportada - tasa_sis.tasa) > 0.01:
                     item["sugerencia"] = "Diferencia de tasa detectada"
        
        analisis_instrumentos.append(item)

    return templates.TemplateResponse(
        "reconciliation/resolucion_conflicto.html",
        {
            "request": request,
            "pago": pago,
            "instrumentos": analisis_instrumentos,
            "title": f"Resolver Conflicto - {pago_id}"
        }
    )
