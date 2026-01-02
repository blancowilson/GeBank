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
- [x] **Workflow:** Cash instruments usually don't have `Staging` records. They go to a "Virtual Verification" queue or Auto-approve based on rules.
- [x] **Action:** "Commit to ERP" button. Triggers the actual `SBTRAN` insert only after manual confirmation.
