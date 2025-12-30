# Product Guidelines: GeBankSaint

## UI/UX & Visual Identity
- **Modern & Interactive:** The application uses a "Monolito Modular Hexagonal" approach with **FastAPI**, **Jinja2**, and **HTMX**.
- **Responsive Design:** Styled with **Tailwind CSS**, ensuring the dashboard is accessible and functional on both desktop and mobile devices.
- **Dynamic Updates:** Use **HTMX** for partial DOM updates (modals, table filtering, form submissions) to provide a seamless, SPA-like experience without the complexity of a heavy frontend framework.
- **Local Interactivity:** Use **Alpine.js** for minimal client-side state management (e.g., toggling menus, client-side validation).

## Multi-Currency Handling (USD Base -> VES Referential)
- **Base Currency:** The primary currency for all transactions and balances is **U.S. Dollars ($)**.
- **Referential Currency:** Bolívares (VES) are treated as a referential currency. Calculations to VES should be performed using the established `Factor` at the transaction time.
- **Explicit & Distinct Display:** VES and USD must be visually distinguishable (e.g., using different color codes or currency symbols) to prevent user errors in a high-stakes financial environment.
- **Precision:** Financial calculations must maintain a precision of at least two decimal places for both currencies.
- **Data Source for BS:** For accurate Bolívares representation and to avoid rounding errors, queries should rely on the `VW_ADM_FACT_CONBS` and `VW_ADM_ITEMSFACTURABS` SQL views where possible.

## Tone & Communication
- **Professional & Precise:** Error messages and system notifications must be clear, technical, and actionable, especially regarding bank reconciliation failures or database synchronization errors.
- **Multilingual Support:** The primary interface language is Spanish (Venezuela), reflecting the local operational context.

## Design Patterns
- **Hexagonal Architecture:** Maintain a strict separation between the Domain logic (Business Rules) and Infrastructure (Adapters for Saint ERP, Insytech, and Bank Parsers).
- **Anti-Corruption Layer (ACL):** Use adapters to map Saint's legacy table names (`SAACXC`, `SBBANC`) into clean, domain-specific entities (`Invoice`, `Bank`).
