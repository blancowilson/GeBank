from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.config import settings
from app.shared.utils.logger import logger
from app.presentation.web.routes import cxc_routes, bancos_routes, config_routes, reconciliation_routes, conflict_routes
from app.presentation.api import insytech_routes

logger.info("Starting GeBankSaint application...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Routes
app.include_router(cxc_routes.router, prefix="/cxc", tags=["CXC"])
app.include_router(bancos_routes.router)
app.include_router(config_routes.router)
app.include_router(reconciliation_routes.router)
app.include_router(conflict_routes.router)
app.include_router(insytech_routes.router, prefix="/api/v1", tags=["Insytech API"])

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/presentation/web/templates")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "title": "Dashboard - GeBankSaint"}
    )

@app.get("/health")
async def health_check():
    return {"status": "ok"}

