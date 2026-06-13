# Process flows

The `C*` labels are documentation shorthand for business-document flows, not Odoo module names.

| Flow | Purpose | Main model | Main reports |
|---|---|---|---|
| C1 | Commercial quote/order/pro-forma | `sale.order` | Q/SO/PF 2026+ |
| C2 | Accounting VAT invoice/down-payment/credit-note | `account.move` | VAT RI/DPI 2026+ |
| C2-edge | Accounting edge cases and validation matrix | `account.move` + accounting data | VAT RI/DPI 2026+ |
| D1 | Delivery Note | `stock.picking` | DN 2026+ |
| P1 | Pick List | TBD | Placeholder |
| R1 | Backup/export/restore support process | `ir.ui.view`, `ir.actions.report`, `report.paperformat`, `ir.config_parameter` | support scripts |
