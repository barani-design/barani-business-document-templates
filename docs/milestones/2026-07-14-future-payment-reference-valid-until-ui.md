# BARANI Odoo 16 — future Payment Reference and Valid Until UI milestone

**Accepted:** 2026-07-14
**Environment:** Live production Odoo 16
**Publication scope:** Sanitized Server Action source and milestone documentation only.

## Locked policy

```text
Report routing / menus / Invoice Preview:
    already complete; no-touch

Historical sale.order.reference values:
    unchanged

Historical account.move.payment_reference values:
    unchanged

Future Sales Orders:
    standard sale.order.reference = digits-only sale.order.name
    only when reference is blank

Future invoices created from those Sales Orders:
    standard Odoo propagation to account.move.payment_reference

Current BARANI PDF source-derived Payment Reference fallback:
    retained for historical compatibility

Valid Until:
    standard sale.order.validity_date
    visible on quotations and confirmed Sales Orders
    editable in draft/sent
    read-only in sale/done/cancel

Invoice Valid Until field:
    not created

DDS / Studio business fields:
    excluded

Preferred Payment Method:
    fixed Wire transfer document-policy text retained
```


## Relationship to the existing report-routing milestone

The report-routing and Invoice Preview accepted-current package is already published on `main` at:

```text
platforms/odoo/16/accepted-current/2026-07-14-report-routing-preview/
```

This milestone does not duplicate or replace those 17 accepted-current files. It records only the later future Payment Reference and standard Valid Until UI feature, while treating the published routing/Preview package as a no-touch prerequisite.

## Root cause and standard-Odoo solution

Odoo 16 provides the standard Sales field:

```text
sale.order.reference
Label: Payment Ref.
```

Standard invoice preparation copies it to:

```text
account.move.payment_reference
```

Previously, the Sales field was blank, allowing posted customer invoices to fall back to an Odoo-generated RF reference. The accepted prospective fix populates the standard Sales field at Sales Order creation from the digits-only final Q/SO sequence. It does not write existing Sales Orders or invoices.

## Installed artifacts

### F00 — technical restore point

Captures the accepted report-routing/Preview signatures, base Sales form bytes, planned-runtime-record absence, and pre-install business-record cutoffs. It writes only `ir.config_parameter` restore metadata.

### F01 — future-only installer

Creates:

```text
one active on_create base.automation on sale.order
one linked ir.actions.server
one inherited sale.order form view
```

The automation writes only the newly created Sales Order when its standard `reference` is blank. The inherited view modifies only the presentation of the existing standard `validity_date` field.

### F02 — read-only verifier

Final technical result:

```text
problems=0
warnings=0
WRITE ACTIONS PERFORMED: NONE
RESULT: PASS
```

Verified:

```text
runtime automation/action/view definitions: PASS
pre-install sale.order.reference digest: UNCHANGED_PASS
pre-install account.move.payment_reference digest: UNCHANGED_PASS
future Sales Order Payment Ref: PASS
future invoice standard propagation: PASS
report routing and Invoice Preview no-drift: PASS
```

### F99 — rollback

Removes the F01-created automation, linked Server Action, and inherited view. It intentionally does not erase standard references already generated on future business documents.

## Manual acceptance

A new post-install quotation was used to verify:

```text
Valid Until visible and editable in draft
manual Valid Until edit persisted
Valid Until visible and read-only after confirmation
future Payment Ref equals digits-only Q number
new draft invoice inherited the same Payment Reference
no RF fallback on the new invoice
BARANI HTML Preview remained functional
BARANI PDF remained functional
Preferred Payment Method remained Wire transfer
```

## Historical compatibility

The existing BARANI Q/SO/PF and RI/DPI templates retain their source-derived Payment Reference display logic. That fallback remains necessary because historical stored references were deliberately not migrated. New records have matching standard stored and displayed values; historical reprints remain correct through the existing source-derived fallback.

## Safety boundary

This milestone does not include or perform:

```text
historical Payment Reference migration
bulk account.move writes
QWeb body changes
report-action/menu/Preview changes
Delivery Note changes
invoice Valid Until custom field
DDS-field restoration or dependency
customer PDFs
customer data
bank details
credentials
private restore payloads
```
