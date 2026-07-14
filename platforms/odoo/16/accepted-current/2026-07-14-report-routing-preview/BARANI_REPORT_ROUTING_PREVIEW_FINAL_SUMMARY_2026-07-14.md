# BARANI Odoo 16 — Final Report Routing and Invoice Preview Summary

**Date:** 2026-07-14  
**Environment:** Live production Odoo 16  
**Scope:** Standard Print-action routing, invoice Preview routing, Print-menu consolidation, archival labeling of superseded Odoo QWeb wrappers  
**Explicitly out of scope:** Preferred Payment Method implementation, which is being handled in another chat

---

## 1. Final outcome

The migration is functionally complete and the final read-only audit passed:

```text
problems=0
warnings=0
writes_performed=0
accepted state=PASS
```

The standard Odoo report-action XML IDs were preserved and internally routed to the accepted BARANI QWeb templates and paperformats. Duplicate custom `— 2026+` Print entries were hidden only after manual verification. The Accounting Preview button now renders the accepted BARANI invoice body as HTML. The former Odoo-linked QWeb wrappers were retained and only their human-readable view names were prefixed with `Archived —`.

No accounting documents, sales orders, payments, taxes, journals, totals, payment references, or POHODA records were modified.

---

## 2. Standard report actions now routed to BARANI

### Sales

```text
sale.action_report_saleorder
Action ID: 281
Visible name: Quotation / Order
Renderer: barani_commercial.report_saleorder
Paperformat: BARANI Commercial A4 7mm
Binding: sale.order, visible in Print
```

```text
sale.action_report_pro_forma_invoice
Action ID: 282
Visible name: PRO-FORMA Invoice
Renderer: barani_commercial.report_saleorder_proforma
Paperformat: BARANI Commercial A4 7mm
Binding: sale.order, visible in Print
```

### Accounting

```text
account.account_invoices
Action ID: 234
Visible name: Invoices
Renderer: barani_vat.report_invoice_document_vat
Paperformat: BARANI VAT A4 7mm
Binding: account.move, visible in Print
```

```text
account.account_invoices_without_payment
Action ID: 236
Name retained: Invoices without Payment
Renderer: barani_vat.report_invoice_document_vat
Paperformat: BARANI VAT A4 7mm
Binding: removed from Print menu
Internal action/XML ID retained
```

The audit decision for action 236 was:

```text
WITHOUT_PAYMENT_MODE = SAME_BARANI_BODY
```

There was no separate approved BARANI no-payment wrapper, so both standard invoice actions use the same accepted BARANI RI/DPI/Credit Note body.

---

## 3. Final Print menus

### Sales Order form

```text
Quotation / Order
PRO-FORMA Invoice
Delivery Note
```

### Customer Invoice form

```text
Invoices
```

The following entries are no longer visible:

```text
Quotation / Order — 2026+
PRO-FORMA — 2026+
VAT Invoices RI/DPI - 2026+
Invoices without Payment
Delivery Note (DN) — 2026+
```

`Original Bills` was not changed. It is a separate Odoo/vendor-document workflow and is not expected to render customer RI/DPI documents from the customer-invoice form.

---

## 4. Hidden custom report actions retained

The duplicate custom report actions were unbound, not deleted:

```text
ID 964
Name: Quotation / Order — 2026+
Renderer: barani_commercial.report_saleorder
Binding: removed
Record retained
```

```text
ID 965
Name: PRO-FORMA — 2026+
Renderer: barani_commercial.report_saleorder_proforma
Binding: removed
Record retained
```

```text
ID 918
Name: VAT Invoices RI/DPI - 2026+
Renderer: barani_vat.report_invoice_document_vat
Binding: removed
Record retained
```

This preserves rollback and technical traceability.

---

## 5. Delivery Note

```text
Action ID: 1013
Previous visible name: Delivery Note (DN) — 2026+
Current visible name: Delivery Note
Renderer: barani_delivery.report_sale_order_delivery_note_2026
Paperformat: BARANI Delivery A4 7mm
Binding: sale.order, visible in Print
```

The generated Delivery Note for `Q/126/00151` was manually verified and rendered correctly.

---

## 6. Invoice Preview implementation

The standard Odoo Preview button originally called:

```text
preview_invoice()
→ portal invoice URL
```

It was replaced at the form-view routing level with a hidden BARANI HTML report action.

### Hidden Preview action

```text
Action ID: 1115
Display name: Invoice Preview
Model: account.move
Type: qweb-html
Renderer: barani_vat.report_invoice_document_vat
Report file: barani_vat.report_invoice_document_vat
Paperformat: BARANI VAT A4 7mm
Print binding: none
```

### Inherited Preview-routing view

```text
View ID: 2913
Name: BARANI Account Move Preview -> VAT 2026+ HTML
Key: barani_runtime.account_move_preview_2026_button
Model: account.move
Active: True
Priority: 999
```

The effective button is now:

```text
name="1115"
type="action"
string="Preview"
```

The visible breadcrumb was cleaned from:

```text
BARANI Invoice Preview 2026+ (hidden)
```

to:

```text
Invoice Preview
```

---

## 7. Manual Preview verification

### Regular customer invoice

```text
Invoice: 2026233
Preview: PASS
BARANI layout: PASS
No portal-layout fallback: PASS
No RPC/access error: PASS
```

### Down Payment Invoice

```text
DPI: 2026198
Preview: PASS
Correct Down Payment Invoice presentation: PASS
Correct source/payment reference/date formatting: PASS
No RPC/access error: PASS
```

### Credit Note

```text
Credit Note: 2026200
Preview: PASS
Original Invoice shown separately: PASS
Original Payment Reference shown separately: PASS
Payment-request/bank-transfer band suppressed: PASS
Preferred Payment Method suppressed: PASS
No RPC/access error: PASS
```

---

## 8. Manual PDF verification

### Accounting

For invoice `2026233`, the following three outputs were compared:

```text
Invoices
Invoices without Payment
VAT Invoices RI/DPI - 2026+
```

Result:

```text
All rendered the same accepted BARANI invoice body
Same values
Same page count
Same headers/footers
Same totals
Same paperformat/margins
Rendered comparison: identical
```

### Sales

For source order `Q/126/00151`, the following pairs were compared:

```text
Quotation / Order
Quotation / Order — 2026+
```

and:

```text
PRO-FORMA Invoice
PRO-FORMA — 2026+
```

Result:

```text
Standard and fallback Q/SO outputs: identical
Standard and fallback Pro-Forma outputs: identical
Correct BARANI filenames and paperformats
```

---

## 9. Email and Send & Print status

BARANI does not send documents through Odoo, so functional email sending and Send & Print tests were classified as:

```text
N/A — workflow not used
```

The static routing audit passed:

```text
Invoice email template → standard action 234 → BARANI VAT renderer
Credit Note email template → standard action 234 → BARANI VAT renderer
Sales email templates → standard action 281 → BARANI commercial renderer
```

No mail-template rewrite was required.

---

## 10. Archived Odoo QWeb wrappers

The former standard Odoo-linked QWeb wrappers were retained, active, and byte-identical to the pre-migration snapshot. Only `ir.ui.view.name` was changed.

```text
View ID 861
Key: sale.report_saleorder
Name: Archived — Odoo Quotation / Order
```

```text
View ID 862
Key: sale.report_saleorder_pro_forma
Name: Archived — Odoo Pro-Forma Invoice
```

```text
View ID 736
Key: account.report_invoice_with_payments
Name: Archived — Odoo Invoice with Payments
```

```text
View ID 735
Key: account.report_invoice
Name: Archived — Odoo Invoice without Payments
```

Unchanged:

```text
QWeb key
XML ID
t-name
arch_db/template bytes
active state
inheritance
```

---

## 11. Restore points and rollback

### Existing accepted-current restore point

A prior accepted BARANI document-template restore point already exists:

```text
accepted_current_d03_6_manual_2026_06_30
```

That snapshot represents the accepted D03.6/manual template state before this routing/Preview migration.

### New B10 pre-migration restore point

Created successfully in live Odoo:

```text
Snapshot code:
pre_standard_relink_preview_2026_07_14

Parameter prefix:
barani.report_routing_preview.restore.pre_standard_relink_preview_2026_07_14
```

B10 captured eight report actions:

```text
281  Quotation / Order
282  PRO-FORMA Invoice
234  Invoices
236  Invoices without Payment
964  Quotation / Order — 2026+
965  PRO-FORMA — 2026+
918  VAT Invoices RI/DPI - 2026+
1013 Delivery Note (DN) — 2026+
```

For each action it stored the relevant pre-migration state, including:

```text
name
model
report_name
report_file
report_type
paperformat
binding_model
binding_type
binding_view_types
print_report_name
attachment flags/expression
multi flag
```

B10 also captured four original QWeb wrappers:

```text
861 sale.report_saleorder
862 sale.report_saleorder_pro_forma
736 account.report_invoice_with_payments
735 account.report_invoice
```

For each view it stored:

```text
key
name
active state
full arch_db/template bytes
```

B10 performed no report-action, QWeb, or business-record writes.

### R10 rollback action

The implementation kit contains:

```text
R10_RESTORE_BARANI_REPORT_ROUTING_PREVIEW_FROM_B10_SAFE.py
```

Its intended rollback behavior is:

```text
restore all B10-snapshotted report-action fields
restore original QWeb wrapper names and bytes
remove Preview view 2913
remove hidden Preview action 1115
restore original bindings and Delivery Note name
```

Important remaining maintenance item:

```text
R10 was created before C32.
It should be amended to reset/clear the C32 marker:
barani.report_routing_preview.c32.preview_action_rename.marker
```

The actual rollback of action 1115 remains functionally correct because R10 removes the Preview action entirely. The marker cleanup must nevertheless be added so rollback metadata is internally consistent.

---

## 12. Final V40 audit

The final read-only audit verified:

```text
C10 marker: PASS
C20 marker: PASS
C30 marker: PASS
C31 marker: PASS
C32 marker: PASS

Standard action routing/bindings: PASS
Hidden custom actions retained/unbound: PASS
Delivery Note visibility/name: PASS
Final Print menus: PASS
Preview action/view/effective button: PASS
Archived wrapper names/keys/bytes: PASS
Mail-template standard-action references: PASS
```

Final result:

```text
problems=0
warnings=0
writes_performed=0
accepted state=PASS
```

---

## 13. What remains to do

### A. Reset and archive write-capable Server Actions

Confirm these are returned to safe defaults:

```text
B10
C10
C20
C30
C31
C32
```

Each should have:

```python
APPLY = False
CONFIRM = ''
```

They may then be archived or clearly marked as completed/rollback-controlled to prevent accidental execution.

### B. Patch the R10 rollback marker cleanup

Add C32 awareness to R10:

```text
define C32_MARKER
reset C32_MARKER to 0 during successful restore
optionally clear its action_id/display_name metadata parameters
```

Then compile, checksum, and retain the corrected R10 in the final handoff package.

### C. Create a post-migration accepted-current snapshot

Create a new accepted-current technical snapshot representing the state verified by V40. Suggested identifier:

```text
accepted_current_report_routing_preview_2026_07_14
```

It should export at minimum:

```text
standard report actions 281, 282, 234, 236
hidden custom actions 964, 965, 918
Delivery Note action 1013
Preview action 1115
Preview inherited view 2913
archived QWeb wrappers 861, 862, 736, 735
active BARANI QWeb templates
paperformats 6 and 7 and Delivery paperformat
mail-template report references
B10 restore metadata
C10–C32 phase markers
V40 final audit output
```

### D. Update the final implementation package

The original implementation kit predates C32 and V40. The final package should add:

```text
C32_LAST_RENAME_BARANI_PREVIEW_ACTION_DISPLAY_NAME_SAFE.py
V40_READONLY_BARANI_FINAL_REPORT_ROUTING_PREVIEW_STATE_AUDIT.py
corrected R10 rollback action
final V40 output
this final summary
updated manifest and SHA-256
```

### E. Publish a new GitHub milestone

At the beginning of this run, the repository base was:

```text
main: 49c3fe5
accepted-current milestone 43ce726 contained in main
```

A new feature branch should publish only the approved sanitized artifacts. Recommended scope:

```text
new accepted-current routing/Preview snapshot
final handoff
final summary
server actions B10/C10/C20/V30/C30/C31/C32/R10/V40
checksums and manifest
no customer data
no live invoice PDFs/screenshots unless deliberately sanitized
```

Then:

```text
review staged file list
run sensitive-data scan
commit
push/publish branch
open PR into main
verify only intended files changed
merge with normal merge commit
pull main
verify milestone commit is contained in main
```

### F. Reconcile with Preferred Payment Method work

Preferred Payment Method remains a separate workstream.

After that work is applied, rerun a narrow regression:

```text
standard Q/SO Print
standard Pro-Forma Print
standard Invoice Print
RI/DPI/Credit Note Preview
final Print menus
V40 final audit
```

Confirm that the new editable payment-method source appears consistently in both PDF and HTML without changing the routing established here.

### G. No further functional work is required for this scope

Within the present scope, no unresolved routing, Preview, menu, or archived-wrapper defect remains. The remaining work is packaging, rollback-script maintenance, accepted-current export, and GitHub publication.
