from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

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
