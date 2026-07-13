# Milestone: RI/DPI/Credit Note D03.6 + manual accepted-current state

Date: 2026-06-30

Repository scope: public sanitized milestone note only. No customer PDFs, live XML exports, bank credentials, Odoo database dumps, POHODA files, or private restore parameters are included in this repository.

## Summary

The BARANI business-document production templates reached an accepted-current state for the VAT RI/DPI/Credit Note family, aligned with the already-fixed commercial Q/SO/PF family.

Accepted live state:

```text
D03.6 display-only RI/DPI/Credit Note alignment
+ manual finishing edits
+ current live Q/SO/PF commercial baseline
```

The in-database restore point was created under snapshot code:

```text
accepted_current_d03_6_manual_2026_06_30
```

## Accepted behavior

RI/DPI/Credit Note visual behavior accepted in production:

- RI/DPI customer-facing Payment Reference prints a numeric source-derived value.
- Stored `account.move.payment_reference` is not rewritten by the accepted template work.
- Down Payment Invoices use the same source-derived numeric Payment Reference as the sales chain.
- Credit Notes show separate `Original Invoice` and `Original Payment Reference` metadata fields.
- Credit Notes keep payment/bank-request band suppression.
- Paid Regular Invoices show `Payment received` with date and amount.
- Paid Down Payment Invoices show `Payment received` date only.
- Unpaid Down Payment Invoices show no false payment-received note.
- Final invoices with down-payment reconciliation show source-DPI payment received dates only when payment evidence exists.
- Dates on RI/DPI/Credit Notes use `DD MON YYYY`, for example `23 JUN 2026`.
- Percent formatting is compact, for example `0 %`, `20 %`, `23 %`, `50 %`, `100 %`.
- VAT Rate columns print numeric rates rather than tax labels.
- `Preferred Payment Method` terminology is used.
- Down-payment reconciliation totals and Odoo official totals remain intact.

Commercial Q/SO/PF baseline accepted before this milestone:

- `Payment Terms`
- `Immediate upon receipt`
- `Payment Reference`
- `Preferred Payment Method`
- `Disc.` column
- compact percent values
- stable table geometry

## Safety boundary

This milestone is report/template display work only. It does not intentionally change:

- accounting postings;
- tax postings;
- fiscal positions;
- account `324000` down-payment liability behavior;
- bank records;
- journal entries;
- stored `account.move.payment_reference`;
- Odoo invoice totals or VAT math;
- POHODA export behavior.

The accepted restore-point action wrote only `ir.config_parameter` snapshot rows and did not write `ir.ui.view`, `ir.actions.report`, `report.paperformat`, `account.move`, `sale.order`, or stored payment-reference fields.

## Restore-point contents

The accepted-current restore point captured the live BARANI business-document state in Odoo configuration parameters, including:

- BARANI VAT RI/DPI/Credit Note QWeb views;
- BARANI commercial Q/SO/PF QWeb views;
- related delivery-note and picking-operation BARANI report views included in the broader business-document snapshot;
- related report actions;
- related paperformats;
- accepted-state marker checks.

Use any restore script only after reviewing its dry-run plan. The restore point is a broad accepted-current snapshot, not a surgical one-line patch.

## Do not re-run historical installers

After this milestone, the following historical scripts are no longer the source of truth for production:

```text
D02
D03
D03.1
D03.2
D03.3
D03.4
D03.5
D03.6
original L24.1 01A
original L24.1 01B
```

The live accepted state includes manual finishing edits and must be preserved by exporting current live templates, not by replaying old scripts.

## Remaining optional follow-up

RI/DPI/Credit Notes now use `DD MON YYYY` dates. Q/SO/PF still use their current commercial baseline date format unless a separate date-only commercial alignment patch is created and accepted.

## Next repository step

The next safe repository artifact should be a sanitized export/handoff of the accepted live templates after running a read-only export from Odoo production and removing private tenant values.
