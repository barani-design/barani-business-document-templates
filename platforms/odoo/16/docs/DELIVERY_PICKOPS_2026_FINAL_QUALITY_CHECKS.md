# Delivery/PickOps 2026 final quality checks

```text
PY platforms/odoo/16/support/backup-restore-export/company_report_colours_READONLY.py: PASS
PY platforms/odoo/16/support/backup-restore-export/create_delivery_and_picking_2026_restore_point_SAFE.py: PASS
PY platforms/odoo/16/support/backup-restore-export/db_identity_and_delivery_template_probe_READONLY.py: PASS
PY platforms/odoo/16/support/backup-restore-export/dn_l2_nested_kit_package_count_READONLY.py: PASS
PY platforms/odoo/16/support/backup-restore-export/export_live_delivery_and_picking_2026_templates_READONLY.py: PASS
PY platforms/odoo/16/support/backup-restore-export/restore_delivery_and_picking_2026_from_restore_point_SAFE.py: PASS
PY platforms/odoo/16/installers/delivery-note/install_delivery_note_2026_FINAL_SAFE_v4.py: PASS
PY platforms/odoo/16/installers/pick-list/install_picking_operations_2026_FINAL_SAFE_v4.py: PASS
XML platforms/odoo/16/templates/delivery-note/DELIVERY_ARCH_barani_delivery.report_delivery_note_2026.xml: PASS
XML platforms/odoo/16/templates/delivery-note/LAYOUT_ARCH_barani_delivery.external_layout_delivery_2026.xml: PASS
XML platforms/odoo/16/templates/delivery-note/SO_BRIDGE_ARCH_barani_delivery.report_sale_order_delivery_note_2026.xml: PASS
XML platforms/odoo/16/templates/pick-list/PICKOPS_ARCH_barani_delivery.report_picking_operations_2026.xml: PASS
XML platforms/odoo/16/templates/pick-list/LAYOUT_ARCH_barani_delivery.external_layout_picking_operations_2026.xml: PASS
EMBEDDED DN body: PASS
EMBEDDED DN layout: PASS
EMBEDDED SO bridge: PASS
EMBEDDED PickOps body: PASS
EMBEDDED PickOps layout: PASS
TOKEN #B00020: PRESENT
TOKEN dds_: PRESENT
TOKEN brn_: PRESENT
TOKEN IBAN: PRESENT
TOKEN Payment Ref: PRESENT
TOKEN Unit Price: PRESENT
```

## Apply script smoke test

```text
PASS: ran against a temporary repository root; copied files, regenerated manifest, syntax validation passed, privacy/risky-file scans passed, no __pycache__ left behind.
```
