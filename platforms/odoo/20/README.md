# Odoo 20 preparation

**Start here when resuming:** [status, exact source pins and restart steps — 16 October 2026](checkpoints/resume-20261016/README.md).

Source preparation is partly complete and published. Native application/PDF acceptance, combined integration and real-data migration remain outstanding. Runtime-01 stays **HOLD_RUNTIME01**.

| Document module | Source version | Acceptance |
| --- | --- | --- |
| Purchase | 20.0.1.0.3 | Frozen and independently accepted offline; native tests and four actual PDFs pending |
| Commercial | 20.0.1.0.0 | Published candidate; native/PDF acceptance pending |
| Delivery / Picking | 20.0.1.0.0 | Published candidate; native/PDF acceptance pending |
| VAT invoices / DPI / credits | 20.0.1.0.1 | Stored-reference correction; focused offline tests and scoped Mac Ruff passed; native/PDF acceptance pending |

The owner-confirmed SO-derived payment reference stays constant across pro-forma and later invoice; the invoice retains its separate legal document number. See the [reference policy](checkpoints/REFERENCE_POLICY_20261016.md).

The resume guide also identifies the separate private POHODA / Payment Reference / protected Tax Rules .10 checkpoint and the remaining Intrastat, Warranty, automation, inventory and migration work. These repositories have not been assembled into an accepted installable v20 release.

Historical source/evidence records remain: [Purchase](checkpoints/purchase-20261016/README.md) and [document candidates](checkpoints/documents-20261016/README.md). Their time-specific pending items must be read with the newer resume guide.

This documentation checkpoint changes no application source, module version, Odoo.sh parent gitlink, existing environment, database or runtime guard. Publication is source preservation, not go-live acceptance.
