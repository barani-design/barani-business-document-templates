# Validation summary

## Static and live checks

```text
S00 marker: PASS
S01 marker: PASS
S01A marker: PASS
S01B marker: PASS
S02 marker: PASS

Commercial — Source field: PASS
Commercial — Document Date: PASS
Commercial — 10pt metadata: PASS
Commercial — Customer Ref wrap: PASS
Commercial — Customer Ref padding: PASS
Commercial — Payment Method: PASS
Commercial — old preferred label removed: PASS
Commercial — Wire transfer retained: PASS
Commercial — SO-normalized Source: PASS
Commercial — historical Payment Reference fallback: PASS
Commercial — 10-column product table: PASS
Commercial — no DDS dependency: PASS
VAT — normalized Source: PASS
VAT — linked Sales Order source: PASS
VAT — single-source guard: PASS
VAT — Payment Method: PASS
VAT — old preferred label removed: PASS
VAT — Wire transfer retained: PASS
VAT — historical Payment Reference fallback: PASS
VAT — credit-note metadata: PASS
VAT — down-payment logic: PASS
VAT — 10-column invoice table: PASS
VAT — no DDS dependency: PASS

Report routing / Preview no-drift: PASS
Final verifier: problems=0 warnings=0
Final verifier writes: NONE
```

## Rendered-document acceptance

The following classes were printed and visually reviewed:

```text
Quotation without Customer Ref.
Quotation with Valid Until and long Customer Ref.
Confirmed Sales Order
Old and new Pro-Forma
Historical regular invoice
New regular invoice
Historical DPI
Final invoice with down-payment reconciliation
Credit Note using slash numbering
Credit Note using legacy numbering
Near-page-break / multi-page commercial document
```

Accepted observations:

```text
metadata typography matches the standard 10 pt document text
Customer Ref. wraps only inside its own column
no metadata collision or inter-column flow
Source displays the SO chain
Payment Reference remains correct
Payment Method displays Wire transfer
product and invoice tables retain their accepted geometry
bank band, credit-note metadata and down-payment reconciliation remain intact
```

Customer PDFs are intentionally not included in this repository package.
