# BARANI Delivery Note + Picking Operations 2026+ Runbook

## Purpose

This folder contains the canonical Odoo 16 Server Action installers and QWeb templates for:

- `Delivery Note (DN) — 2026+`
- `Delivery Note (DN) — 2026+` Sales Order bridge
- `Picking Operations — 2026+`

The Delivery Note is the external/customer/customs document. It prints commercial parent lines, HS/COO from the parent product in kit context, package-code traceability, line notes, customer/shipping address details, and no monetary/payment fields.

The Picking Operations report is the internal warehouse document. It remains exploded into physical stock move/move-line rows with serial/product barcodes, notes, delivery-address details, and no customs grouping.

## Clean installation

Run from Odoo built-in Server Actions. Use dry-run first.

1. Create a restore point on existing databases using `support/backup-restore-export/create_delivery_and_picking_2026_restore_point_SAFE.py`.
2. Verify restore dry-run using `restore_delivery_and_picking_2026_from_restore_point_SAFE.py`.
3. Run `installers/delivery-note/install_delivery_note_2026_FINAL_SAFE_v4.py` with `DRY_RUN=True`, review the write plan, then apply with `CONFIRM='INSTALL_BARANI_DELIVERY_NOTE_2026_FINAL'`.
4. Run `installers/pick-list/install_picking_operations_2026_FINAL_SAFE_v4.py` with `DRY_RUN=True`, review the write plan, then apply with `CONFIRM='INSTALL_BARANI_PICKING_OPERATIONS_2026_FINAL'`.
5. Print-test representative delivery orders and sales-order bridge output.

## Safety

Installers write only BARANI-owned QWeb views, report actions, paperformats, and config parameters. They do not write stock moves, sales orders, invoices, products, BoMs, accounting data, DDS fields, or `brn_` fields.
