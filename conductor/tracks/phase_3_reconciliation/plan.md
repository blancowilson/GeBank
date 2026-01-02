# Phase 3: Advanced Reconciliation Engine, Configuration & Agnosticism

## Goals
- **ERP/Portal Agnosticism:** Refactor interfaces to be generic (not hardcoded to Saint/Insytech).
- **Currency Configuration:** Support dynamic Base/Reference currencies and conversion logic (multiply/divide).
- **Entity Mapping:** Configurable mapping between Portal Bank Codes and ERP Account Codes.
- **Detailed Reconciliation:** Manual matching of individual Instruments vs Staging Transactions.
- **Virtual Cash:** Handling non-bank instruments.

## Todo List

### Sprint 3.1: Agnostic Architecture & Global Config
- [x] **Config Entity:** Create `SystemConfiguration` table (Singleton pattern or Key-Value).
    - `base_currency` (e.g., USD), `base_symbol` ($).
    - `ref_currency` (e.g., VES), `ref_symbol` (Bs).
    - `rate_operator`: MULTIPLY or DIVIDE (How to convert Ref -> Base).
- [x] **Refactor:** Rename repositories to generic names (`IERPTransactionRepository`, `IPortalPaymentRepository`).
- [x] **Service:** Update `TasaService` to respect the `rate_operator` config.

### Sprint 3.2: Bank & Instrument Mapping
- [x] **Entity:** Create `BankMapping` table.
    - Fields: `portal_bank_code` (e.g., "04"), `erp_bank_code` (e.g., "110103"), `description`.
- [x] **UI:** Configuration screen to CRUD these mappings.
    - Dropdown of available ERP Banks (from `SBBANC`).
    - Input for Portal Code.
- [x] **Logic:** Update `ReconciliationEngine` to use this mapping to look up the correct `Staging` records (since Staging uses ERP codes or needs translation).

### Sprint 3.3: The "Manual Match" Workspace
- [x] **View:** Detailed Reconciliation Workspace.
    - **Context:** A single `GePago` (Header).
    - **Left Column:** List of `GeInstrumentos`.
        - Show converted amount in Base Currency (using Sprint 3.1 logic).
        - Show mapped ERP Bank Name (using Sprint 3.2 logic).
    - **Right Column:** List of potential `Staging_Bancos` matches.
        - Filtered by mapped bank code and approximate amount.
- [x] **Action:** "Link & Approve" button for individual instrument pairs.

### Sprint 3.4: Virtual Cash & Final Persistence
- [x] **Logic:** Identify "Cash" instruments via the Mapping (e.g., mapped to a "Caja" type account).
- [ ] **Workflow:** Refine the "Virtual Verification" queue.
    - [ ] Asegurar que los instrumentos marcados como `is_cash` no busquen en staging y se presenten para aprobación directa.
    - [ ] Implementar log de auditoría específico para aprobaciones manuales de efectivo.
- [ ] **Action:** "Commit to ERP" Final.
    - [ ] Validar que la persistencia en `SBTRAN` y `SAPAGCXC` sea atómica (preparación para Fase 4).
    - [ ] Pruebas de rendimiento con "grandes transacciones" (múltiples instrumentos y documentos en un solo pago).

## Próximos Pasos (Preview)

### Fase 4: Integridad Transaccional y Resiliencia
- [ ] Implementar patrón **Unit of Work** para asegurar operaciones atómicas entre Portal y ERP.
- [ ] Sistema de Reintentos para fallos en la persistencia del ERP.
- [ ] Alertas de inconsistencia de datos.
