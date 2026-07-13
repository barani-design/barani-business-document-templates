# BARANI accepted-current business document templates — sanitized export

Date: 2026-06-30
Snapshot code: `accepted_current_d03_6_manual_2026_06_30`

This directory is a sanitized public-repository snapshot derived from the accepted live Odoo templates after the B01 restore point and E02 read-only export.

It includes logical QWeb template XML and sanitized report/paperformat metadata for:

- BARANI VAT RI/DPI/Credit Note reports;
- BARANI commercial Q/SO/PF reports;
- BARANI Delivery Note / Picking Operations reports captured by the accepted-current business-document restore point;
- BARANI test/title helper views captured in the same snapshot.

## E02 acceptance summary

The private E02 export reported:

```text
qweb_views_exported=14
report_actions_exported=5
paperformats_exported=4
accepted_marker_problems=0
warnings=0
writes_performed=0
view_mismatch=0
report_mismatch=0
paperformat_mismatch=0
```

The raw E02 export is private and is not included here.

## Sanitization performed

The public XML files replace tenant-specific values:

```text
confirmed compact receiving-bank IBAN literal -> XX0000000000000000000000
confirmed spaced receiving-bank IBAN literal -> XX00 0000 0000 0000 0000 0000
confirmed receiving-bank BIC literal -> YOURBICXXX
confirmed tenant EXW default-location literal -> YOUR_EXW_DEFAULT_LOCATION
```

No customer PDFs, invoice PDFs, POHODA files, raw live database export, private restore parameters, production logs, or credentials are included.

## Safety boundary

This accepted-current snapshot documents report/template display behavior. It does not intentionally change or define:

- accounting postings;
- tax postings;
- fiscal positions;
- account `324000` behavior;
- bank records;
- journal entries;
- stored `account.move.payment_reference`;
- Odoo invoice totals or VAT math;
- POHODA export behavior.

## Notes

The public files are not a one-click Odoo installer. Treat them as a versioned accepted-current template snapshot and donor source for future sanitized installers.
