# Phase 0: Infrastructure & Base Setup [checkpoint: finished]

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
- [x] Setup Redis for Celery and configure Celery instance [Verified with pytest]
- [x] Configure Tailwind CSS (CDN for dev, build script for prod) [Configured in base.html]
- [x] Setup HTMX (CDN) and create `base.html` template with navbar [Verified]
- [x] Verify setup: FastAPI running at http://localhost:8000 with rendered template [Verified]

### Sprint 0.2: Saint Anti-Corruption Layer (ACL)
- [x] Create SQLAlchemy models for Saint tables (Read-Only): `SAFACT`, `SAACXC`, `SACLIE` (Core) [Implemented in models.py]
- [x] Create SQLAlchemy models for Insytech tables (Read-Only): `Gedocumentos`, `GeInstrumentos`, `GePagos` [Implemented in models.py]
- [x] Create `SaintAdapter` base class in infrastructure layer [Implicit in Repository Implementation]
- [x] Implement `SaintFacturaRepository` (read-only) in infrastructure [Implemented & Verified]

---

# Phase 1: Core CXC Module (Accounts Receivable)

## Todo List

### Sprint 1.1: Domain Layer - Entities CXC
- [x] Create `Cliente` domain entity (id, name, rif, total_balance)
- [x] Create `Monto` Value Object (amount, currency VES/USD)
- [x] Create `CXCService` for balance calculations and aging
- [x] Define `ClienteRepository` port
- [x] Unit tests for business logic [Verified with pytest]

### Sprint 1.2: Infrastructure - CXC Adapters
- [x] Implement `SaintClienteRepository` (read-only) [Implemented & Verified]
- [x] Implement `SaintPagoRepository` (write) -> UPDATE `SAACXC` + INSERT `SAPAGCXC` [Implemented & Verified]
- [x] Integration tests with test database [Verified with pytest]

### Sprint 1.3: Application Layer - Use Cases
- [x] `ConsultarCXCClienteUseCase`: Returns list of pending invoices [Implemented]
- [x] `RegistrarPagoManualUseCase`: Orchestrates payment logic and DB update [Implemented]
- [x] Define DTOs for data transfer [Implemented]

### Sprint 1.4: Presentation Layer - UI CXC
- [x] FastAPI Route: `GET /cxc/clientes` -> List clients [Implemented]
- [x] Jinja2 Template: `cxc/listado_clientes.html` (Table + Search) [Implemented]
- [x] FastAPI Route: `GET /cxc/cliente/{id}/facturas` -> Detail modal [Implemented]
- [x] Jinja2 Template: `cxc/detalle_facturas.html` (Aging + Partial) [Implemented]
- [x] FastAPI Route: `POST /cxc/pago/registrar` -> Form submission via HTMX [Implemented]
- [x] Verify UI flows and responsiveness [Verified]

---

# Phase 2: Insytech Integration & Reconciliation Engine

## Todo List

### Sprint 2.1: Infrastructure & Database Expansion
- [ ] Create `Staging_Bancos` table in `AppConciliacion` schema
- [ ] Implement `StagingTransaction` entity and repository

### Sprint 2.2: Ingestion & Parsing
- [ ] Enhance `TasaService` for historical conversion logic
- [ ] Implement `ReceivePaymentPacketUseCase` (GePagos/Docs/Instruments)
- [ ] Implement `BankFileParserService` and `UploadBankStatementUseCase`

### Sprint 2.3: Reconciliation Logic
- [ ] Implement `ReconciliationEngine` domain service (Match Logic)
- [ ] Implement `ConciliarPagoUseCase`

### Sprint 2.4: Persistence (Saint Sync)
- [ ] Implement adapters to write to `SBTRAN` and update `SAACXC` upon approval

### Sprint 2.5: UI
- [ ] Create "Bandeja de Entrada" (Staging) view
- [ ] Create "Conciliación Detallada" view