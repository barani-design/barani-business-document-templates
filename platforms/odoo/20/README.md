# Odoo 20 migration target (planned)

This folder is reserved for a tested Odoo 20 implementation of the BARANI business-document families. It does not yet contain deployable Odoo 20 code.

## Source baseline

Use both Odoo 16 sources as migration inputs:

- `../16/templates/` — maintained, portable Odoo 16 QWeb sources.
- `../16/accepted-current/2026-08-26-production-template-closeout/` — locked evidence of production-verified behavior, hashes, routes, labels, filenames, bindings, and paper formats.

Preserve the accepted-current snapshot unchanged.

## Compatibility boundary

The Odoo 16 QWeb templates and Server Actions are not drop-in compatible with Odoo 20. Do not copy or run them on Odoo 20 without revalidating template inheritance, report APIs, model fields, filename expressions, report-action bindings, Preview routing, and rendering behavior. Do not carry database record IDs or private restore data into the port.

## Port acceptance

An Odoo 20 port is not working until:

- every view installs, compiles, and renders in a disposable Odoo 20 database;
- invoices and credit notes, quotations and sales orders, pro-formas, Delivery Notes, and Picking Operations pass;
- billing-versus-shipping behavior passes for same-partner, same-location/different-contact, and different-company/address scenarios;
- Delivery Note unique-source, multiple-source, Incoterms, sale-less, kit, lot, and serial branches pass;
- report labels, numeric-first filenames, Print bindings, Preview routing, translations, and paper formats match the accepted contract;
- tests use synthetic records and no production or customer data is committed;
- a dry run, rollback strategy, fresh backup, confirmed apply, and independent read-only verifier exist for the target environment.

Keep Odoo 20 implementation code and migration evidence in this folder.
