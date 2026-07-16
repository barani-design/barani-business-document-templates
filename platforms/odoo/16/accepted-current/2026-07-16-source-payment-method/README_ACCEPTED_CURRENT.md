# BARANI Source / Payment Method — accepted-current

**Accepted on live Odoo 16:** 2026-07-16  
**Scope:** Q/SO/PF plus RI/DPI/Credit Note document templates  
**Final technical audit:** `problems=0`, `warnings=0`, no writes by the final verifier

## Accepted visible result

Commercial Q/SO/PF metadata remains one horizontal row of columns:

```text
Document Date | Valid Until | Customer Ref. | Payment Terms | Source | Payment Reference | Payment Method
```

Fields appear only when applicable. The normal 5/6-field layouts and the
densest 7-field layout use the standard 10 pt document typography.

Example:

```text
Source             SO/126/00161
Payment Reference  12600161
Payment Method     Wire transfer
```

For RI/DPI/Credit Notes, the visible Source is normalized to the linked
`SO/...` chain when exactly one Sales Order is available. Multiple-source
origins are not forced to an arbitrary Sales Order.

## Customer Reference

Odoo does not impose a practical display-length limit on Customer Ref.
The accepted template therefore allows only that value to wrap inside its
own column and adds 14 px right padding before Payment Terms. All other
metadata labels and values remain no-wrap.

## Historical compatibility

- Historical stored Sales Order and invoice Payment References are unchanged.
- The existing source-derived BARANI PDF Payment Reference fallback remains.
- Legacy Sales Order numbering such as `SO2026357` is preserved as-is.
- Credit Note Original Invoice and Original Payment Reference remain intact.
- DPI and final-invoice down-payment reconciliation remains intact.

## Exact live snapshots

The QWeb XML files in `qweb/` are exact live `arch_db` bytes exported after
acceptance. Their SHA-1 values match the Odoo attachment checksums in
`LIVE_EXPORT_METADATA.txt`.

## No-touch boundary

This milestone does not alter:

```text
business records
stored Payment References
taxes or totals
down-payment accounting
report actions
Print menus
Invoice Preview routing
paperformats
Delivery Note
product-table widths
DDS fields
```
