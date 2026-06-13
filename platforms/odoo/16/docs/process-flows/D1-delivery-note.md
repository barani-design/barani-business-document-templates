# D1 — Delivery Note 2026+ flow

## Goal

Render a DDS-free delivery note from `stock.picking` with product QR codes generated from native `product_id.barcode`.

## Flow

```text
stock.picking
  -> Print: Delivery Note (DN) — 2026+
  -> ir.actions.report / QWeb body: barani_delivery.report_delivery_note_2026
  -> layout: barani_delivery.external_layout_delivery_2026
  -> BARANI Delivery A4 7mm paperformat
````

## L1 scope

- flat delivery line table;
- QR code on DN only;
- no `dds_` or `brn_` fields;
- no replacement for custom DDS delivered-quantity button;
- kit grouping/parent-child indentation deferred to L2.
