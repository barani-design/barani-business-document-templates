# C2 — VAT RI/DPI/Credit Note 2026+ flow

## Goal

Render accounting documents from `account.move` using an isolated VAT report family. This is a presentation layer only: it does not create or change invoices, taxes, payments, fiscal positions, journal entries, or accounting mappings.

## Flow

```text
account.move
  -> Print: VAT Invoices RI/DPI - 2026+
  -> ir.actions.report report_name=barani_vat.report_invoice_document_vat
  -> standalone body: barani_vat.report_invoice_document_vat
  -> standalone layout: barani_vat.external_layout_standard_titled
  -> BARANI VAT A4 7mm paperformat
````

## Key distinctions

- RI = regular/final invoice.
- DPI = down-payment invoice.
- Credit note follows refund semantics and must not show payment request details.
- Down-payment deductions must be based on actual invoice/accounting lines, not text labels from external modules.

## Support scripts

- create restore point before/after installation;
- export live XML after installation;
- restore from the current restore point if rollback is required.
