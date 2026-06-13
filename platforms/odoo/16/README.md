# Odoo 16 BARANI 2026+ business document templates

This folder contains the Odoo 16 public/sanitized template package for the BARANI 2026+ report families.

## Included report families

| Family | Odoo model | Print options / report action names | Status |
|---|---|---|---|
| VAT RI/DPI/Credit Note | `account.move` | `VAT Invoices RI/DPI - 2026+` | Final L21 installer |
| Quotation / Sales Order / Pro-forma | `sale.order` | `Quotation / Order — 2026+`, `PRO-FORMA — 2026+` | Commercial v4 public sanitized = v3 + Tune L1 |
| Delivery Note | `stock.picking` | `Delivery Note (DN) — 2026+` | DN L1 QR-only DDS-free |
| Pick List | TBD, likely `stock.picking` or internal picking flow | TBD | Placeholder |

## Safety model

All write-capable scripts default to `APPLY = False` and require an explicit confirmation token before writing. Export/probe scripts are read-only.

This package is public/sanitized. Replace placeholders such as `__RECEIVING_IBAN_DISPLAY__`, `__RECEIVING_IBAN_COMPACT__`, and `__RECEIVING_BIC__` before use on a real database.

Do not commit customer PDFs, production exports, private restore-point values, real bank accounts, production tax IDs, API keys, or Odoo credentials.

## Recommended install order

1. Read `docs/configuration-placeholders.md`.
2. Run read-only probes under `support/probes/`.
3. Run backup/restore/export support scripts in dry-run mode.
4. Install VAT report family.
5. Install commercial Q/SO/PF report family.
6. Install Delivery Note report family.
7. Export the live templates and create restore points.
8. Add Pick List only after the live format is finalized.
