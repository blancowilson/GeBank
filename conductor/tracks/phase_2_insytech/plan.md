# Phase 2: Insytech Integration & Reconciliation Engine

## Goals
- **Ingest:** Receive complex payment packets (Header + Documents + Instruments) from the Insytech Portal.
- **Staging:** Create and populate `Staging_Bancos` with raw bank transaction data (Excel/CSV parsers).
- **Engine:** Implement the "Composite & Multi-currency Reconciliation Engine" to match reported payments against staging data.
- **Persist:** Update Saint ERP tables (`SBTRAN`, `SAACXC`) only upon successful reconciliation.

## Conceptual Model (Based on Schema of Validations)
- **GePagos:** The "Header" of the payment packet.
- **GeDocumentos:** The "Administrative" component (Invoices, Credit Notes, Retentions). These do *not* hit the bank.
- **GeInstrumentos:** The "Financial" component (The actual money: Transfers, Cash, Zelle). These *must* match `Staging_Bancos`.
- **Staging_Bancos:** New table for raw bank statement lines (before they are official `SBTRAN` records).

## Todo List

### Sprint 2.1: Infrastructure & Database Expansion
- [x] **DB Migration:** Create `Staging_Bancos` table in `AppConciliacion` schema.
    - Fields: `id`, `banco`, `referencia`, `monto_credito`, `monto_debito`, `moneda`, `fecha_banco`, `descripcion_raw`.
- [x] **DB Migration:** Ensure `GePagos`, `GeDocumentos`, `GeInstrumentos` match the latest schema (Status: Verified).
- [x] **Domain Entity:** Create `StagingTransaction` entity.
- [x] **Repository:** Implement `StagingBancoRepository` (Insert raw, Find by Ref+Amount).

### Sprint 2.2: TasaService & Valuation
- [ ] **Domain Service:** Enhance `TasaService`.
    - Implement `get_tasa(fecha, moneda_origen, moneda_destino)`.
    - Implement `validar_conversion(monto_origen, monto_destino, tasa_reportada, tolerancia=0.05)`.
    - Logic: Validate if `Monto Bs (Banco) / Tasa ≈ Monto USD (Deuda)`.

### Sprint 2.3: Ingestion API (The "Packet" Receiver)
- [ ] **DTOs:** Define strict Pydantic models for the payment packet:
    - `PaymentPacketDTO` (contains `PagoHeader`, `List[DocumentDetail]`, `List[InstrumentDetail]`).
- [ ] **Use Case:** `ReceivePaymentPacketUseCase`.
    - Receives the DTO.
    - Validates integrity (Sum(Docs) ≈ Sum(Instruments) - NC/Ret?). *To be defined.*
    - Persists to `GePagos`, `GeDocumentos`, `GeInstrumentos` with `status=1` (Pendiente).
- [ ] **API Route:** `POST /api/v1/integration/payments` (Endpoint for Insytech Portal).

### Sprint 2.4: Bank Statement Parsers (The "Bank Input")
- [ ] **Service:** `BankFileParserService`.
    - Factory pattern to select parser based on Bank ID.
- [ ] **Parsers:** Implement specific parsers (e.g., `BanescoExcelParser`, `MercantilCSVParser`).
    - Must normalize data into `StagingTransaction` format.
- [ ] **Use Case:** `UploadBankStatementUseCase`.
    - Accepts file.
    - Parses content.
    - Bulk inserts into `Staging_Bancos`.
- [ ] **UI:** `bancos/subir_estado_cuenta.html` (Update mock to use real backend).

### Sprint 2.5: The Reconciliation Engine (The "Brain")
- [ ] **Domain Service:** `ReconciliationEngine`.
    - **Input:** A `GePago` (with its instruments).
    - **Logic:** Iterate over `GeInstrumentos`.
        - **If Cash:** Route to "Virtual Cash" logic (Auto-approve or Manual Review queue).
        - **If Transfer (USD):** Query `Staging_Bancos` for exact match (Ref + Amount).
        - **If Transfer (VES):** Query `Staging_Bancos` for Ref + (Amount in Bs). Use `TasaService` to validate equivalence.
- [ ] **Use Case:** `ConciliarPagoUseCase`.
    - Triggered manually (button) or automatically (cron/event).
    - Updates `GePagos.status` (3=Approved, 9=Rejected).

### Sprint 2.6: Persistence & Saint Sync (The "Result")
- [ ] **Adapter:** `SaintTransactionRepository` (Write to `SBTRAN`).
- [ ] **Adapter:** `SaintCxCRepository` (Update `SAACXC`).
- [ ] **Use Case Extension:** Upon `GePagos` approval (Status 3):
    1. **Insert into SBTRAN:** Create the official bank record from the `Staging_Bancos` data (or `GeInstrumentos` data verified).
    2. **Update SAACXC:**
        - Apply Payment (Net Money).
        - Apply Retentions (from `GeDocumentos`).
        - Apply Credit Notes/Discounts (from `GeDocumentos`).
        - *Goal:* Reduce invoice balance.

### Sprint 2.7: UI & Dashboard
- [ ] **View:** "Bandeja de Entrada de Pagos" (Staging View).
    - List `GePagos` with Status=1.
    - Visual indicators for "Matched", "Diff Tasa", "No Match".
- [ ] **View:** "Conciliación Detallada".
    - Show side-by-side: Reported Instrument vs. Found Staging Transaction.
- [ ] **Security:** Implement Basic RBAC (Admin vs Viewer) for these views.
