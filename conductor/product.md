# Initial Concept
Integración Automatizada de Cobranzas entre Saint y Insytech con Soporte Multimoneda y Reportes de Comisiones.

# Product Guide: GeBankSaint

## Vision
GeBankSaint is an integrated platform designed to bridge the gap between the legacy Saint ERP system and the Insytech sales portal. In the complex financial landscape of Venezuela, it automates multi-currency (VES/USD) collection management, bank reconciliation, and accounting updates, transforming manual hours into automated minutes.

## Target Users
- **Accounting Administrators:** To validate payments, perform bank reconciliations, and update Saint ERP records.
- **Sales Supervisors:** To oversee collection flows and approve commission reports.
- **Sales Vendors:** To report payments in real-time through the integration with Insytech.

## Core Features
1. **Multi-currency Integration (VES/USD):** Real-time synchronization of accounts receivable (SAACXC) and bank transactions (SBTRAN) with support for mixed payments and updated exchange rates.
2. **Automated Bank Reconciliation:** A parsing engine for bank statements (PDF, Excel, TXT) with fuzzy matching logic to pair bank movements with reported payments.
3. **Seller Commission Engine:** Automatic calculation of commissions based on the specific currency of payment, preventing currency mixing and ensuring financial accuracy.
4. **Administrative Interface:** A modern web dashboard for payment validation, reconciliation approval, and exportable reporting (PDF/Excel).
5. **Saint ERP Anti-Corruption Layer:** A modular hexagonal architecture that protects business logic from the complexities of the legacy database schema.

## Goals
- **Operational Efficiency:** Eliminate manual reconciliation errors and reduce processing time.
- **Financial Precision:** Ensure 99%+ accuracy in customer balances and multi-currency accounting.
- **Global Accessibility:** Secure cloud deployment (VPS) with JWT authentication for remote access.
