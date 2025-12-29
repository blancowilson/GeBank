# Phase 1: Core CXC Module (Accounts Receivable)

## Goals
- Implementation of the Client List view.
- Implementation of the Client Invoices Detail view.
- Multi-currency balance display (VES/USD).
- Manual payment registration with Saint ERP update.

## Todo List

### Sprint 1.1: Domain Layer - Entities CXC
- [x] Create `Cliente` domain entity (id, name, rif, total_balance).
- [x] Create `Monto` Value Object (amount, currency VES/USD).
- [x] Create `CXCService` for balance calculations and aging.
- [x] Define `ClienteRepository` port.
- [x] Unit tests for business logic [Verified with pytest].

### Sprint 1.2: Infrastructure - CXC Adapters
- [x] Implement `SaintClienteRepository` (read-only) [Implemented & Verified].
- [x] Implement `SaintPagoRepository` (write) -> UPDATE `SAACXC` + INSERT `SAPAGCXC` [Implemented & Verified].
- [x] Integration tests with test database [Verified with pytest].

### Sprint 1.3: Application Layer - Use Cases
- [x] `ConsultarCXCClienteUseCase`: Returns list of pending invoices [Implemented].
- [x] `RegistrarPagoManualUseCase`: Orchestrates payment logic and DB update [Implemented].
- [x] Define DTOs for data transfer [Implemented].

### Sprint 1.4: Presentation Layer - UI CXC
- [ ] FastAPI Route: `GET /cxc/clientes` -> List clients.
- [ ] Jinja2 Template: `cxc/listado_clientes.html` (Table + Search).
- [ ] FastAPI Route: `GET /cxc/cliente/{id}/facturas` -> Detail modal.
- [ ] Jinja2 Template: `cxc/detalle_facturas.html` (Aging + Partial).
- [ ] FastAPI Route: `POST /cxc/pago/registrar` -> Form submission via HTMX.
- [ ] Verify UI flows and responsiveness.
