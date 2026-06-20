# C1 — Approved commercial policy decisions for the next release

This document records the next implementation baseline. It does not describe
the current L3 template.

## Address sources

Use standard Odoo fields without silent report fallbacks:

```text
Customer block      = sale.order.partner_invoice_id
Shipping block      = sale.order.partner_shipping_id
Commercial customer = sale.order.partner_id
```

Legal ID/VAT values come from the selected address record's commercial parent.
Missing required address/contact data must be corrected in Odoo; the report
must not silently substitute `partner_id`.

A customer may have multiple child records of type **Delivery Address**. The
salesperson selects the intended `partner_shipping_id` on each quotation/order.
Routine ship-to locations should not be stored as ambiguous `Other Address`
records.

## Incoterm location

Print Incoterm and Incoterm location. For EXW, a blank location may use a
company-configured default:

```text
__DEFAULT_EXW_LOCATION__
```

An explicitly entered location always wins. The EXW default must never be
applied to a different Incoterm.

## Visible and downloaded numbers

The displayed Q/SO/PF number and downloaded filename must use one shared
transformation. The underlying `sale.order.name` and accounting/payment
references remain unchanged. Unsafe filename separators are normalized.

## Stable line-table geometry

Always display all ten columns:

```text
Description | HS Code | COO | Qty | Unit | Unit Price |
Disc. % | VAT Rate | VAT | VAT Base
```

Use one fixed width map totalling exactly 100%. Empty data produces empty cells,
not disappearing columns. Section/note rows always span ten columns.

## Pagination

Repeat table headers and test multi-page output. Keep the totals, PF payment
band, and Prepared-by block together where practical without clipping long
notes.

## Language

Commercial and accounting PDFs are English-only in the current policy.
Rendering must not switch to the customer's configured language.

## Public configuration

Public source must not contain live bank details or tenant-specific EORI,
numbering, or EXW location values. These settings must be company-specific and
configured through standard/typed Odoo fields or settings.
