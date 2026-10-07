# Odoo 19 report addons

This directory contains the three report addons deployed in BARANI production
on 7 October 2026. The module files are published unchanged from the recorded
addons commit, including their existing tests and image assets.

| Module | Version | Documents |
|---|---|---|
| `barani_commercial` | `19.0.1.0.2` | Quotations, sales orders, pro-forma invoices |
| `barani_delivery` | `19.0.1.0.6` | Delivery Notes and Picking Operations |
| `barani_vat` | `19.0.1.0.3` | Customer invoices and credit notes |

## Source identity

- Addons commit: `3d0b241d0b35d7619b87bdf4b0a57238150a0df8`.
- Production parent commit: `a9cdaae5aeffac68f6b1fd70734fd29936e41ba8`.
- Source directories: `barani_commercial/`, `barani_delivery/`, and `barani_vat/`.
- Published directories: `addons/<module>/` below this README.

## Prepared Date correction

Delivery Note version `19.0.1.0.6` labels the date cell **Prepared Date** and
uses the transfer's Effective Date, `stock.picking.date_done`. The date stays
blank until that field is populated. Odoo's existing date/time formatting is
retained. The cell's technical name remains `barani_dn_scheduled_date_cell`
for compatibility with inherited templates.

The correction changed only the Delivery Note XML and its manifest version.
Commercial, VAT, and Picking Operations source files were not changed by it.

## Verification scope

The owner supplied a successful production build result for the parent commit
above. A fresh production shell confirmed the parent and addon identities,
`barani_delivery` installed as `19.0.1.0.6`, and the completed transfer's
Effective Date. Its newly rendered Delivery Note was visually checked: it
displayed Prepared Date with the expected effective date and a clean one-page
layout.

The existing automated report tests are included. A full Odoo report regression
suite was not rerun during this publication step. Publishing these source files
does not install or upgrade an Odoo database.

## Publication notice and reuse

This is an immutable source snapshot of BARANI's deployed implementation. It
retains BARANI branding and the public BARANI bank-identification constants
already used in the accepted public Odoo 16 snapshot. No customer PDFs,
database exports, or credentials are included. Review company-specific choices
before reuse. Each addon's manifest declares `LGPL-3`; those declarations are
preserved.

These addons depend on `sale_stock` and override report layouts, actions, and
metadata. Use the addon versions appropriate to the target Odoo environment;
do not replay Odoo 16 Server Actions to install them.

## Other version work

The separate Purchase Order/RFQ source remains on branch
`p19-po-layout-templates-v1`; this publication does not merge that branch.
Odoo 16 snapshots and the Odoo 20 directory are unchanged. The Odoo 20 worktree
requires its own review and publication, including carrying forward the
Prepared Date correction where applicable.
