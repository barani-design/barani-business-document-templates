# P1 — Pick List 2026+ placeholder

Status: not implemented in this package.

Before adding a Pick List installer, decide:

- whether the source model is `stock.picking`, `stock.move`, or a warehouse wave/batch flow;
- whether quantities are reserved, demanded, done, or remaining;
- whether lots/serials appear;
- whether QR/barcode appears;
- whether the document is internal-only or customer-facing.

Apply the same report-family pattern: standalone action, standalone body, standalone layout, dedicated paperformat, read-only export, restore-point script, and restore script.
