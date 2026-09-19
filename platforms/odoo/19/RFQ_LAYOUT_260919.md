# BARANI PO and RFQ layout extension - 2026-09-19

## Scope and cause

Odoo's native Print RFQ button uses `purchase.report_purchase_quotation`.
The confirmed PO uses `purchase.action_report_purchase_order`. Version
19.0.1.0.0 changed only the PO action, so the RFQ retained its previous layout.

Version 19.0.1.0.1 gives both actions the BARANI header, structured company
address, supplier and delivery blocks, footer and paper format. RFQs keep the
title Request for Quotation and remain unpriced. They show description,
expected date, quantity and unit, including the native alternate-unit quantity.
Sections, subsections, public notes and the native supplier portal/EDI link are
retained. The existing priced PO template and its external layout are unchanged.

## Baseline evidence

- Templates base: `2986cdecf2fba208f104e2482194741c72723b8a`.
- Parent build commit: `812cfb63` (short identifier supplied by Odoo.sh).
- Development build 38311243: 10 tests, 0 failures, 0 errors, 11.64 seconds.
- Staging build 38311724: module installed; one-page and two-page PO PDFs
  reviewed for price precision, repeated headers, row continuation and totals.
- The existing RFQ PDF confirmed the separate native route and showed duplicated
  company VAT plus header/body overlap on continuation pages.

These checks apply to 19.0.1.0.0. The RFQ extension has NOT yet run on Odoo.sh.
Customer documents and live database data are not included in this source patch.

## Installation and upgrade

Fresh installation backs up both report actions before routing either report.
Upgrading 19.0.1.0.0 runs `migrations/19.0.1.0.1/pre-10-backup-rfq-action.py` before
the new action XML: it saves the existing RFQ configuration and leaves the PO
backup untouched. Native action IDs and email-template bindings are retained.
Uninstall restores each action only while its BARANI route is still active.
Foreign report routes and cached attachments are rejected before takeover.

Publish the templates commit first using GitHub Desktop, then pin that exact
commit in the isolated parent test branch. Keep the barani-odoo-addons gitlink
unchanged. Run the /barani_purchase suite on a development build with the module
installed; the suite now has 13 methods and renders four PDFs (short and long
PO/RFQ). This includes a simulated upgrade from the previous action configuration.

After the development tests pass, update the existing PO staging branch and
verify that barani_purchase upgrades to 19.0.1.0.1. Print a draft RFQ and a
confirmed PO, inspect a multipage RFQ, and check email attachment previews without
sending. Production publication remains a separate step after staging acceptance.
