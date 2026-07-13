# Milestone supplement: Commercial L4 C02 and B02 post-C02 restore point

**Milestone date:** 2026-06-30
**Repository publication date:** 2026-07-13
**Scope:** Odoo 16 BARANI commercial Q/SO/PF date-format closure, restore-point traceability, and read-only sanitized export tooling.

## Result

```text
C02 commercial Q/SO/PF date format: CLOSED / PASS
B02 post-C02 current baseline restore point: CREATED / PASS
E01.1 sanitized read-only export: COMPLETED / PASS
RI/DPI date format: not changed by C02
Delivery Note date format: not changed by C02
```

C02 changed only the standalone commercial Q/SO/PF body view:

```text
barani_commercial.report_saleorder_document
```

It formats `sale.order.date_order` and `sale.order.validity_date` using fixed English month abbreviations and `DD MON YYYY`, including the validated examples:

```text
04 JUN 2026
09 JUN 2026
30 JUN 2026
30 JUL 2026
```

B02 subsequently captured the validated post-C02 current state in Odoo configuration parameters. It wrote only restore-point keys in `ir.config_parameter`; it did not change QWeb views, report actions, paperformats, invoices, sales orders, delivery notes, or stored payment-reference values.

## Relationship to accepted-current snapshot already on main

The repository already contains the broader accepted-current live-template package at:

```text
platforms/odoo/16/accepted-current/2026-06-30-d03-6-manual/
```

That accepted-current package covers the commercial Q/SO/PF, VAT RI/DPI/Credit Note, Delivery Note, Picking Operations, helper views, report actions, and paperformats. Its commercial Q/SO/PF body already contains the C02 fixed English month tuple and `DD MON YYYY` document-date / Valid Until expressions.

Therefore this supplement intentionally does **not** add another `current_templates/` tree or duplicate QWeb snapshot files. The accepted-current package remains the public template source of truth; this supplement records the applied C02/B02 actions and the later sanitized read-only export method.

## Published server actions

### Applied: C02

```text
platforms/odoo/16/installers/commercial/
C02_HOTFIX_BARANI_Commercial_Q_SO_PF_L4_DATE_FORMAT_DD_MON_YYYY_SAFE.py
```

SHA-256:

```text
8a8901cfa25fba06dffa3ab067440c60197c4e152fc2bf443bcb6e0999683fc8
```

Safety properties:

```text
APPLY=False by default
explicit confirmation token required
commercial body view only
one-time pre-write backup
read-back marker verification
RI/DPI/VAT and Delivery Note untouched
business records untouched
```

### Applied: B02

```text
platforms/odoo/16/support/backup-restore-export/
B02_CREATE_RESTORE_POINT_BARANI_L4_POST_C02_CURRENT_BASELINE_SAFE.py
```

SHA-256:

```text
23e9f13aee86289d0610f69b5c9142b5456016678484a21a369c21dfca9610e3
```

Captured in the private in-database restore point:

```text
8 QWeb view arches
4 report actions
3 paperformats
2,983 exact-one-source account.move payment_reference values
```

The script stores private restore payloads only when run in Odoo. No private restore payload is included in this public repository.

### Read-only: E01.1

```text
platforms/odoo/16/support/backup-restore-export/
E01_1_READONLY_EXPORT_BARANI_L4_POST_C02_CURRENT_TEMPLATES_SANITIZED_FOR_GITHUB_SAFE.py
```

SHA-256:

```text
37777cbdde231a799d85bc7aeaf43939a0c821996ae7e1bc691ac9fc6f6eac7c
```

E01.1:

```text
checks C02 and B02 markers
requires all eight current views to equal B02
reads current QWeb/report/paperformat metadata
replaces bank/account and EXW-default literals dynamically
emits sanitized file blocks
never writes business records or restore payloads
```

## PDF validation

Representative Q/SO/PF PDFs proved all requested target cases:

```text
04 JUN 2026: PF, SO, and Q
09 JUN 2026: PF, SO, and Q
30 JUN 2026: PF and Q
30 JUL 2026: Q Valid Until
```

The following retained commercial behavior was also visually checked:

```text
Payment Reference present and digits-only
Preferred Payment Method retained
Immediate upon receipt retained
numeric VAT Rate retained
Disc. column retained
compact percentage formatting retained
all ten table columns retained
PF-only bank-transfer band retained
English-only rendering retained
Incoterm content retained
```

## Deliberate exclusions

```text
No customer PDFs
No live database export
No private ir.config_parameter payload
No bank account or BIC literal
No customer data
No stored payment-reference changes
No D02/D03 historical replay script
No duplicate current-template snapshot tree
No repository-root MANIFEST_SHA256.txt change
```

The accepted-current snapshot on `main` remains authoritative for public QWeb template bytes. Historical D02/D03 scripts are not republished as current installers.
