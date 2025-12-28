# Phase 0: Infrastructure & Base Setup

## Goals
- Establish the hexagonal architecture structure.
- Configure FastAPI, Jinja2, HTMX, and Tailwind CSS.
- Connect to SQL Server (Saint ERP) and Redis.
- Implement the basic Saint Anti-Corruption Layer (ACL).

## Todo List

### Sprint 0.1: Infrastructure Base
- [x] Setup Git repository with hexagonal structure (app/, domain/, infrastructure/, etc.) a25121b
- [x] Configure FastAPI with Jinja2 templates (server-side rendering) [Verified with uv & pytest]
- [x] Configure SQL Server connection (AsyncSQLAlchemy) to Saint DB [Verified with pytest & aioodbc]
- [x] Create separate schema in SQL Server: `AppConciliacion` (via Alembic or raw SQL if needed) [Configured in alembic/env.py]
- [ ] Setup Redis for Celery and configure Celery instance
- [ ] Configure Tailwind CSS (CDN for dev, build script for prod)
- [ ] Setup HTMX (CDN) and create `base.html` template with navbar
- [ ] Verify setup: FastAPI running at http://localhost:8000 with rendered template

### Sprint 0.2: Saint Anti-Corruption Layer (ACL)
- [ ] Create SQLAlchemy models for Saint tables (Read-Only): `SBBANC`, `SBTRAN`, `SAFACT`, `SAACXC`, `SACLIE`
- [ ] Create `SaintAdapter` base class in infrastructure layer
- [ ] Implement `SaintFacturaRepository` (read-only) in infrastructure
- [ ] Create integration test: Read invoices from Saint DB and log results to verify connection
