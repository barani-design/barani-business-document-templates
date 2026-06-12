# BARANI DPI/RI VAT Treatment — Option B Handoff for POHODA Export

## Scope
This note documents the current BARANI Odoo 16 treatment for taxable down-payment invoices (DPI) and final regular invoices (RI), including the Odoo fields/variables that matter for POHODA export.

## Business rule
Customer advance payments are treated as **gross amounts paid by the customer**. Odoo must split the gross amount into VAT base + VAT according to the fiscal position:

- Domestic Slovakia: Slovak VAT, currently 23%.
- OSS B2C: destination-country OSS VAT rate, price-included.
- Intra-EU B2B: reverse charge / 0% when valid VAT/customer conditions apply.
- Non-EU export: 0% export treatment when the transaction qualifies.

The down-payment product/accounting path stays on account **324000 Prijaté preddavky**. Do not move the Down payment product out of the `Received Down Payments` category/account path.

## Current confirmed example: OSS France chain SO-EXAMPLE
DPI `INV-EXAMPLE`:

- Fiscal position: `OSS B2C France`
- Entered/gross down-payment amount: `100.00 EUR`
- Line: account 324000 / Down Payment
- VAT rate: `20.0%`
- VAT base: `83.33 EUR`
- VAT: `16.67 EUR`
- Total incl. VAT: `100.00 EUR`

RI `INV-EXAMPLE`:

- Goods line after discount: base `540.00 EUR`
- VAT: `108.00 EUR`
- Total incl. VAT: `648.00 EUR`
- Deduction: `Less: Down Payment Invoice INV-EXAMPLE 100.00 EUR`
- Balance Due shown on PDF: follows Odoo `amount_residual`; if fully reconciled/paid it may show `0.00 EUR` even though the commercial gross supply minus advance is `548.00 EUR` before payments.

## Odoo objects and fields

### Main invoice model
`account.move`

Important fields:

- `name` — legal posted invoice number, e.g. `INV-EXAMPLE`, `INV-EXAMPLE`.
- `move_type` — `out_invoice` for customer invoice/DPI/RI, `out_refund` for credit note.
- `state` — `draft`, `posted`, etc.
- `invoice_origin` — source SO/PF reference, e.g. `SO-EXAMPLE`.
- `payment_reference` — legal invoice payment reference for RI; DPI PDF deliberately displays `invoice_origin` as payment ref.
- `partner_id` — billing customer.
- `partner_shipping_id` — shipping recipient/address.
- `fiscal_position_id` — tax treatment; report prints name + note.
- `invoice_incoterm_id` — standard Incoterms field; report prints `CODE (Full name)` or `Not specified`.
- `intrastat_transport_mode_id` — report prints Intrastat transport code when populated.
- `amount_untaxed` — Odoo official untaxed/base total after tax/fiscal-position treatment.
- `amount_tax` — Odoo official tax total.
- `amount_total` — Odoo official total incl. VAT.
- `amount_residual` — open balance after payments/reconciliation; used by PDF as `Balance Due`.

### Invoice lines
`account.move.invoice_line_ids`

Important fields:

- `display_type` — real product/accounting lines have no section/note display type.
- `account_id.code` — account `324...` identifies down-payment/advance lines.
- `price_subtotal` — line VAT base / subtotal excl. VAT.
- `price_total` — line total incl. VAT.
- `tax_ids` — taxes applied to line.
- `sale_line_ids` — native link back to `sale.order.line`; used to identify down-payment source lines and related invoices.
- `product_id` — product; down-payment product remains the standard down-payment product/category path.

### Tax fields
`account.tax`

Important fields:

- `name` — visible internal tax name, e.g. `SK 23% VAT Included — Down Payments`, `20.0% FR VAT Included — Down Payments`.
- `description` — Label on Invoices; report prints VAT Rate from this field via `line.tax_ids.mapped('description')`.
- `amount` — tax rate.
- `price_include` — critical for gross-paid advances. Must be `True` for the down-payment tax path.
- `type_tax_use` — `sale` for customer invoices.
- `invoice_repartition_line_ids` / `refund_repartition_line_ids` — tax accounts/tags/grids, important for VAT report and POHODA.

### Fiscal positions
`account.fiscal.position`

Important fields:

- `name` — printed on report.
- `note` — printed legal VAT note on report.
- `auto_apply`, `vat_required`, `country_id`, `country_group_id`, `sequence` — determine automatic fiscal-position selection.
- `tax_ids` — tax mappings from product/source tax to destination tax.

Required mapping pattern for gross-paid advances:

- Down-payment product source tax: `SK 23% VAT Included — Down Payments` (`price_include=True`).
- Domestic Slovakia: no mapping required if the product default tax is already the included SK tax.
- OSS B2C France: `SK 23% VAT Included — Down Payments` → `20.0% FR VAT Included — Down Payments`.
- OSS B2C Finland: `SK 23% VAT Included — Down Payments` → `25.5% FI VAT Included — Down Payments`.
- Intra-EU: `SK 23% VAT Included — Down Payments` → `0% EU B2B`.
- Non-EU: `SK 23% VAT Included — Down Payments` → `0% non-EU export`.

## Report/QWeb classification variables
The BARANI VAT report uses account 324 classification only for display; it does not change accounting:

- `barani_dp_lines` — real invoice lines where `account_id.code[:3] == '324'` and `price_subtotal >= -0.005`. These are positive down-payment lines on DPI.
- `barani_ded_lines` — real invoice lines where `account_id.code[:3] == '324'` and `price_subtotal < -0.005`. These are negative down-payment deduction lines on RI.
- `barani_goods_lines` — real invoice lines not on 324.
- `barani_is_dp_invoice` — positive 324 lines exist and there are no goods lines and no negative deduction lines.
- `barani_has_advance_deduction` — `bool(barani_ded_lines)`; identifies final RI/settlement invoices involving prior DPIs.
- `barani_advance_applied` — `-sum(barani_ded_lines.mapped('price_total'))`; gross total of advances deducted.
- `barani_total_base` — sum of visible table lines' `price_subtotal`.
- `barani_official_goods_total` — on RI with deductions, `o.amount_total + barani_advance_applied`; used for commercial goods total before advance deduction.
- `barani_official_goods_vat` — `barani_official_goods_total - barani_total_base`.

## Why VAT is not double-counted
For taxable advances, the DPI posts VAT immediately on the received/gross advance. The final RI must contain a negative 324 deduction line carrying the same tax treatment. That line reverses both base and VAT already invoiced.

Example:

- DPI: gross advance `100.00`, base `83.33`, VAT `16.67`.
- RI goods: base `540.00`, VAT `108.00`, gross `648.00`.
- RI deduction line: gross `-100.00`, base `-83.33`, VAT `-16.67`.
- Net RI tax still due from the invoice tax recap: goods VAT `108.00` minus advance VAT `16.67` = `91.33`, subject to Odoo rounding and actual invoice line structure.

POHODA export must export the negative advance deduction as a real VAT-bearing negative line, not as a flat note/discount. Otherwise VAT will be double counted or incorrectly omitted.

## POHODA export requirements
POHODA must distinguish valid cases from invalid mismatches.

Allow:

- Domestic VAT-bearing DPI on 324000 using the included SK advance tax.
- Domestic RI with VAT-bearing negative 324000 advance deduction.
- OSS B2C VAT-bearing DPI using destination-country included OSS advance tax.
- OSS B2C RI with matching VAT-bearing negative 324000 advance deduction.
- Intra-EU and Non-EU advance flows only when fiscal position/tax treatment is truly 0% and legally correct.

Block/review:

- Domestic fiscal position + 0% down-payment tax.
- OSS B2C fiscal position + price-excluded OSS advance tax that makes customer gross advance become net + VAT.
- OSS B2C fiscal position + Slovak domestic VAT instead of destination-country OSS VAT.
- Non-EU/export fiscal position + positive domestic/OSS VAT lines.
- Slovak billing/domestic treatment accidentally using Non-EU/export fiscal position because of shipping address.

## Report patch requests after current state
Planned report-only changes:

1. Show customer phone/mobile below billing address when available.
2. Show shipping phone/mobile below shipping address when available.
3. On RI with down-payment deductions, print a note: "Advance VAT reconciliation: Down-payment deduction lines carry negative VAT base and negative VAT. VAT already invoiced on advances is deducted on this final invoice, so VAT is not charged twice."

These are presentation changes only. They do not affect taxes, journal items, POHODA export values, or invoice posting.
