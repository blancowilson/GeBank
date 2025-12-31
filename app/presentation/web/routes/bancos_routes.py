from fastapi import APIRouter, Request, UploadFile, File, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.session import get_db

from app.domain.services.parser_service import BankFileParserService
from app.infrastructure.parsers.banesco_excel_parser import BanescoExcelParser
from app.application.use_cases.bancos.upload_bank_statement import UploadBankStatementUseCase
from app.domain.repositories.staging_banco_repository import StagingBancoRepository
from app.infrastructure.repositories.staging_banco_repository_impl import StagingBancoRepositoryImpl
from app.infrastructure.saint.saint_banco_repository import SaintBancoRepository
from app.domain.repositories.banco_repository import BancoRepository

router = APIRouter(prefix="/bancos", tags=["bancos"])
templates = Jinja2Templates(directory="app/presentation/web/templates")

@router.get("/subir", response_class=HTMLResponse)
async def ver_subir_estado_cuenta(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Renderiza la vista de carga de estados de cuenta, incluyendo la lista de bancos.
    """
    banco_repo: BancoRepository = SaintBancoRepository(db)
    bancos = await banco_repo.get_all()
    
    return templates.TemplateResponse(
        "bancos/subir_estado_cuenta.html", 
        {
            "request": request,
            "title": "Cargar Estado de Cuenta",
            "bancos": bancos
        }
    )

@router.post("/upload", response_class=HTMLResponse)
async def procesar_archivo_banco(
    request: Request,
    bank_id: str = Form(...), # e.g., 'banesco'
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Procesa el archivo subido usando el parser correspondiente, lo guarda en
    la tabla de staging y retorna los resultados.
    """
    content = await file.read()
    filename = file.filename
    file_type = os.path.splitext(filename)[1].lower().replace('.', '')
    
    # 1. Setup Services and Repositories
    parser_service = BankFileParserService()
    # Register available parsers
    parser_service.register_parser("banesco_xlsx", BanescoExcelParser)
    # Add other parsers here, e.g., parser_service.register_parser("mercantil_csv", MercantilCSVParser)
    
    staging_repo: StagingBancoRepository = StagingBancoRepositoryImpl(db)
    
    # 2. Execute Use Case
    use_case = UploadBankStatementUseCase(parser_service, staging_repo)
    
    try:
        transactions = await use_case.execute(bank_id, file_type, content, filename)
        
        # 3. Prepare response for the UI
        total_txns = len(transactions)
        stats = {
            "total": total_txns,
            "filename": filename
        }

        return templates.TemplateResponse(
            "bancos/_analisis_resultados.html",
            {
                "request": request, 
                "transacciones": transactions,
                "stats": stats
            }
        )
    except Exception as e:
        # Handle errors gracefully in the UI
        return templates.TemplateResponse(
            "shared/error_toast.html",
            {"request": request, "message": f"Error procesando archivo: {e}"}
        )

import os
