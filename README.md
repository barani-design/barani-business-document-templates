# BARANI Business Document Templates

Reusable business-document template kit for ERP systems, starting with Odoo 16 and designed to also host future Odoo 19 implementations.

This repository is **not tied to a single Odoo version**. Version-specific code lives under `platforms/odoo/<version>/`. Shared business-process documentation lives under `docs/`.

## Current implementations

| Platform | Status | Location |
|---|---:|---|
| Odoo 16 | Working baseline | `platforms/odoo/16/` |
| Odoo 19 | Planned | `platforms/odoo/19/` |

## Included document families

The current Odoo 16 implementation includes baseline installers and support tools for:

- VAT invoices / regular invoices / down-payment invoices / credit notes
- Quotations / sales orders / pro-forma invoices
- Delivery notes with product QR codes
- Pick lists (placeholder/TODO)

## Why one repository?

Use one repository because the document families, process flows, and accounting decisions are shared across versions. Keeping Odoo 16 and Odoo 19 in one repo makes it easier to compare behavior and port improvements forward.

Split into separate repositories only if the Odoo 19 implementation becomes a separate product with different maintainers, release cadence, or licensing.

## Safety model

The Odoo installers are Server Actions written to be dry-run first. Write-capable scripts must be run with `APPLY = False` first, reviewed, then run with the expected confirmation token.

The public repository is sanitized. Replace placeholder bank values, company identity, fiscal-position names, tax names, and report labels before using in a real database.

Do not publish customer PDFs, live database exports, invoices, bank statements, private backup parameters, API keys, or production credentials.

## Main Odoo 16 setup order

1. Review `platforms/odoo/16/docs/odoo-configuration/`.
2. Configure company identity, logo, fiscal country, VAT, and EORI.
3. Configure the receiving bank account.
4. Configure taxes, fiscal positions, and the down-payment product/accounting path.
5. Run read-only probes.
6. Install commercial reports.
7. Install VAT RI/DPI reports.
8. Install delivery-note report.
9. Export live templates and create restore points.

## License

A draft MIT license file is included. Review and approve before publishing publicly.
