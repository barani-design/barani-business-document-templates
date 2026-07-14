# BARANI Odoo 16 — future Payment Reference + Valid Until UI SAFE kit

## Locked policy

- Report routing, Print menus, and Invoice Preview are already complete and are no-touch.
- Historical `sale.order.reference` and `account.move.payment_reference` values remain unchanged.
- Future sale orders receive standard `sale.order.reference` as digits-only `sale.order.name`, only when the field is blank.
- Odoo standard invoice preparation propagates `sale.order.reference` to `account.move.payment_reference`.
- Current BARANI PDF source-derived Payment Reference fallback remains for historical compatibility.
- Standard `sale.order.validity_date` is displayed as **Valid Until** in all states.
- Valid Until is editable in draft/sent and read-only in sale/done/cancel.
- No invoice Valid Until field is created.
- DDS/Studio/custom business fields are excluded.
- Preferred Payment Method remains fixed `Wire transfer` policy text.

## Run order

1. Run `F00...` with `DRY_RUN=True`.
2. Apply F00 only after a clean dry run.
3. Run `F01...` with `APPLY=False`.
4. Apply F01 only after a clean dry run.
5. Create one NEW quotation after F01.
6. Verify its Payment Ref and Valid Until UI; create an invoice from it.
7. Run `F02...` and complete the manual checklist.
8. Use `F99...` only to remove the automation/view. F99 intentionally does not erase standard references already generated on future documents.

## Technical basis

Odoo 16 assigns the sale-order sequence before `super().create()`. An `on_create` Automated Action therefore receives the final Q/SO number. Odoo's standard `sale.order._prepare_invoice()` copies `sale.order.reference` into `account.move.payment_reference`.
