# BARANI Delivery Note 2026 DN L1 QR-only DDS-free Kit

This package updates the original baseline to the latest BARANI plan:

- **DN** is the English shorthand used here for **Delivery Note**. Slovak operational shorthand is usually **DL** for *Dodací list*, but the Odoo/server-action/report-family naming in this package uses **DN**.
- QR codes are used **only on the Delivery Note**, generated from native `product_id.barcode`.
- No QR code change is made to Quotation, Sales Order, Pro-forma, or invoice reports.
- No replacement is built for DDS **Update Delivered Quantity** because production confirmed that function is not used.
- DN L1 is a flat native `stock.picking` / `stock.move` line table. Kit parent/indented component grouping is deferred to DN L2 after testing real kit pickings.
- No `dds_` fields/functions and no `brn_` fields are used.
- EORI is **not** printed from VAT. Add EORI later only after a real verified field/source exists.

## Active installer

`installer/barani_delivery_note_report_installer_DN_L1_QR_ONLY_DDS_FREE_SAFE.py`

Creates/updates:

- QWeb body view: `barani_delivery.report_delivery_note_2026`
- custom layout view: `barani_delivery.external_layout_delivery_2026`
- report action on `stock.picking`: `Delivery Note (DN) — 2026+`
- paperformat: `BARANI Delivery A4 7mm`

It is additive and does **not** modify the stock Odoo Delivery Slip report.

## Core design

- Same BARANI invoice-style header/footer family as RI/DPI 2026+.
- Right-side title only: `Delivery Note: <picking.name>`.
- Company registration block: ID, Tax ID, VAT. No EORI unless separately confirmed.
- Customer and Shipping Address blocks with phone and wrap/gutter logic.
- Product QR codes generated from `product_id.barcode` using Odoo `/report/barcode` QR route.
- Delivery line table: QR, Description, HS Code, COO, Lot/Serial, Ordered, Delivered, Unit.
- Bottom receipt band: Received by / Date / Signature.

## Run order

1. Run `support/barani_delivery_note_probe_READONLY_v2.py` to verify fields/modules.
2. Run the installer with `APPLY=False`.
3. If clean, set `APPLY=True` and `CONFIRM='INSTALL_DELIVERY_NOTE_2026'`.
4. Print a delivery order with `Delivery Note (DN) — 2026+`.
5. If accepted, run `support/barani_delivery_note_create_CURRENT_RESTORE_POINT_SAFE.py`.
6. Export live XML with `support/barani_delivery_note_export_READONLY_v2.py`.

## Important assumptions

- Odoo 16 / current BARANI stock flow.
- Inventory/Stock is installed.
- Sales integration is installed, because the template uses `stock.picking.sale_id` to derive the commercial customer where possible.
- Intrastat/product fields `product_id.hs_code` and `product_id.country_of_origin` are available, matching the current BARANI invoice report environment.
- Product QR uses `product_id.barcode`; it does not create or modify barcode values.

## Safe-eval / server action policy

All write-capable scripts default to dry-run (`APPLY=False`) and require explicit confirmation. Support probe/export scripts are read-only. The installer includes self-checks for standalone QWeb, QR-on-DN, no invoice-money fields, no EORI-from-VAT, and no `dds_`/`brn_` dependencies.

## Package hygiene

The historical VAT installer reference from the baseline was removed from this DN L1 kit. It was useful as a visual reference, but it contained invoice-only concepts such as IBAN/payment fields and legacy EORI-from-VAT logic, so keeping it in the active support kit created unnecessary confusion.
