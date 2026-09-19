# BARANI Business Document Templates

Reusable business-document templates for ERP systems, with a production-verified Odoo 16 baseline, an Odoo 19 Purchase Order candidate, and a planned Odoo 20 port.

This repository is **not tied to a single Odoo version**. Version-specific code lives under `platforms/odoo/<version>/`. Shared business-process documentation lives under `docs/`.

## Current implementations

| Platform | Status | Location |
|---|---:|---|
| Odoo 16 | Production-verified baseline | `platforms/odoo/16/` |
| Odoo 19 | Purchase Order candidate; runtime validation pending | `platforms/odoo/19/` |
| Odoo 20 | Planned migration target; no deployable implementation yet | `platforms/odoo/20/` |

The locked migration baseline is the [26 August 2026 production template closeout](platforms/odoo/16/accepted-current/2026-08-26-production-template-closeout/). It records accepted Odoo 16 behavior and is not an Odoo 20 installer.

## Included document families

The current Odoo 16 implementation includes baseline installers and support tools for:

- VAT invoices / regular invoices / down-payment invoices / credit notes
- Quotations / sales orders / pro-forma invoices
- Delivery notes with product QR codes
- Picking Operations / pick lists

## Why one repository?

Use one repository because the document families, process flows, and accounting decisions are shared across versions. Keeping the accepted Odoo 16 baseline beside later version-specific implementations makes behavior comparison and controlled porting easier.

Split into separate repositories only if a later-version implementation becomes a separate product with different maintainers, release cadence, or licensing.

## Source ownership and deployment

Commercial and business-document templates are maintained in this repository. POHODA, Intrastat and import applications are maintained separately in `barani-odoo-addons`.

Keep version-specific document modules under `platforms/odoo/<version>/addons/`. An Odoo.sh deployment must include the applicable repository revision and make its module directory available to Odoo. Check the parent project configuration before changing deployment references.

## Safety model

The Odoo 16 installers are Server Actions written to be dry-run first. Write-capable scripts must be run with `APPLY = False` first, reviewed, then run with the expected confirmation token.

The maintained reusable templates are sanitized. Replace placeholder bank values, company identity, fiscal-position names, tax names, and report labels before using them in a real database. A reviewed immutable accepted-current snapshot may retain public BARANI payment/delivery instructions when its publication notice says so; it must never contain login credentials or customer data.

Do not publish customer PDFs, live database exports, invoices, bank statements, private backup parameters, API keys, or production credentials.

Never copy or run an Odoo 16 Server Action on Odoo 19 or Odoo 20. Revalidate QWeb inheritance, report APIs, model fields, report actions, bindings, filename expressions, and rendering on the target version.

The Odoo 19 Purchase Order candidate is an installable addon with an installation guard and a saved report-action configuration for uninstall. Validate it in staging before production use.

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
