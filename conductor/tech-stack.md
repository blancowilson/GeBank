# Tech Stack: GeBankSaint

## Backend Core
- **Framework:** FastAPI 0.104+ (Async/await, Pydantic v2, OpenAPI)
- **Database Architecture:** Monolito Modular Hexagonal
- **ORM/Query Builder:** SQLAlchemy 2.0+ (Async) with Alembic for migrations
- **Task Queue:** Celery 5.3+ with Redis 7+ as broker
- **File Processing:** 
  - `openpyxl` (Excel)
  - `pdfplumber` (PDF)
  - `pandas` (Data Analysis)

## Frontend (SSR + Progressive Enhancement)
- **Templating:** Jinja2 3.1+
- **Interactivity:** HTMX 1.9+ (Partial updates, AJAX)
- **Styling:** Tailwind CSS 3.3+
- **Minimal JS:** Alpine.js 3.13+ (Local UI state)
- **Icons:** Material Symbols (Google)

## Database
- **Primary DB:** Microsoft SQL Server 2019+ (Shared with Saint ERP)
- **Connection:** `pyodbc` or `asyncpg`
- **Caching/Queue:** Redis 7+

## Infrastructure & Deployment
- **Web Server:** Nginx 1.24+ (Reverse Proxy, SSL)
- **ASGI Server:** Uvicorn 0.24+ (4 workers)
- **Containerization:** Docker & Docker Compose
- **OS:** Linux (Production), Windows/Linux (Development)

## Monitoring & Quality
- **Error Tracking:** Sentry
- **Metrics:** Prometheus + Grafana
- **Testing:** Pytest (Unit & Integration), Playwright (E2E)
- **Logs:** `structlog`
