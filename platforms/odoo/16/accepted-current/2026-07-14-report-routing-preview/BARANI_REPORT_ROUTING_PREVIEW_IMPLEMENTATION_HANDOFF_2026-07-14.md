# BARANI Odoo 16 — report routing + Preview implementation handoff

**Prepared:** 2026-07-14  
**Production authority:** live Odoo  
**Repository:** `barani-design/barani-business-document-templates`

## Scope lock

Preferred Payment Method is explicitly **out of scope** here and is being handled in another chat.

This handoff implements only:

1. Route the standard Odoo Print action XML IDs to the approved BARANI QWeb PDF templates and BARANI paperformats.
2. Route the existing Accounting **Preview** button to a hidden BARANI qweb-html action using the accepted RI/DPI/Credit Note body.
3. Verify all Print/email/Preview paths while duplicate custom `— 2026+` actions remain visible.
4. Only after acceptance, unbind duplicate custom actions and the visible `Invoices without Payment` menu entry.
5. Last, rename only the former Odoo-linked QWeb wrapper **display names** with an `Archived — ` prefix.
6. Preserve rollback through B10/R10.

## Critical distinction

```text
Report action = menu/routing entry
QWeb template = rendered document body
```

Keep the standard report-action XML IDs. Keep all BARANI QWeb templates. Keep all stock/module-owned QWeb templates. Never change QWeb keys, XML IDs or `t-name` values.

## Locked sequence

### Audit

1. Pull actual latest GitHub `main`; record HEAD.
2. Run `P01_READONLY_BARANI_INVOICE_PREVIEW_2026_ROUTING_AUDIT.py`.
3. Run `P03_READONLY_BARANI_REPORT_MENU_CONSOLIDATION_AUDIT.py`.
4. Continue every page to `MORE REMAINS: NO`.
5. Decide the audited route for `account.account_invoices_without_payment`:
   - `SAME_BARANI_BODY`, or
   - an existing controlled BARANI no-payment wrapper.

### Restore point

6. Run B10 dry-run.
7. Apply B10 only after clean output.

### Phase A — route first

8. Set `WITHOUT_PAYMENT_MODE` in C10 from the P03 decision.
9. Run C10 dry-run, review, apply.
10. Run C20 dry-run, review, apply.

### Verify second

11. Run V30.
12. Perform manual tests while all duplicate custom actions remain visible:
    - standard Quotation / Order Print;
    - standard PRO-FORMA Invoice Print;
    - standard Invoices Print;
    - Invoices without Payment route;
    - Send by Email / Send Pro-Forma Invoice;
    - Send & Print invoice and credit-note attachments;
    - Preview RI `2026232`;
    - Preview DPI `2026198`;
    - Preview Credit Note `2026200`;
    - B10 rollback plan.

### Hide duplicates third

13. Set every C30 manual acceptance flag `True`.
14. Run C30 dry-run, review, apply.
15. Verify final menus.

### Archive-label old templates last

16. Run C31 dry-run, review, apply.
17. Export current templates/actions and create a new accepted-current restore point/milestone.

## Standard action targets

```text
sale.action_report_saleorder
    -> barani_commercial.report_saleorder
    -> BARANI Commercial paperformat

sale.action_report_pro_forma_invoice
    -> barani_commercial.report_saleorder_proforma
    -> BARANI Commercial paperformat

account.account_invoices
    -> barani_vat.report_invoice_document_vat
    -> BARANI VAT paperformat

account.account_invoices_without_payment
    -> audited approved BARANI route
    -> BARANI VAT paperformat
```

## Final visible menus

Sales:

```text
Quotation / Order
PRO-FORMA Invoice
Delivery Note
```

Accounting:

```text
Invoices
```

## Hidden but retained

```text
Quotation / Order — 2026+
PRO-FORMA — 2026+
VAT Invoices RI/DPI - 2026+
Invoices without Payment
```

Their action records remain for rollback/internal references; only Print bindings are removed.

## Archived view-name examples

C31 changes only `ir.ui.view.name`:

```text
Archived — Odoo Quotation / Order
Archived — Odoo Pro-Forma Invoice
Archived — Odoo Invoice with Payments
Archived — Odoo Invoice without Payments
```

C31 does not change:

```text
key
XML ID
t-name
arch_db
active
inherit_id
```

## Preview architecture

```text
existing Preview button
    -> hidden ir.actions.report qweb-html action
    -> barani_vat.report_invoice_document_vat
```

The hidden HTML action is not bound into Print. The existing standard portal `preview_invoice()` path is replaced only for the visible form button through one inherited `account.move` form view.

## Rollback

R10 restores:

- standard/custom report action names, report names/files, paperformats and bindings;
- original QWeb wrapper names and bytes;
- removes the C20-created hidden HTML report action and inherited Preview view.

R10 never touches accounting/business records.

## Hard exclusions

```text
No Preferred Payment Method work
No deletion of report actions
No deletion/deactivation of QWeb templates
No QWeb key/XML-ID/t-name changes
No business/accounting record changes
No posted invoice or sales-order changes
No payment-reference migration
No POHODA changes
No email-template writes unless a later audited patch explicitly proves one is required
```

## Fresh-chat starter

Continue BARANI Odoo 16 live-production work with Preferred Payment Method explicitly out of scope. Implement the report-routing and Preview migration in the locked sequence: P01 and P03 audits first; B10 restore point; C10 repoints the standard Odoo report-action XML IDs to approved BARANI PDF templates while all custom `— 2026+` fallbacks stay visible; C20 routes the existing Accounting Preview button to a hidden BARANI qweb-html action using `barani_vat.report_invoice_document_vat`; V30 plus full Print, Send & Print, email-attachment and RI/DPI/Credit Note Preview tests; only then C30 unbinds duplicate actions; C31 archive-labels only the former Odoo-linked view display names last. Keep all XML IDs, QWeb keys, t-name values and template bytes unchanged. Use R10 for rollback.
