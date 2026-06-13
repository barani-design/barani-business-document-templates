# Server Action Script Standardization Audit

This package was standardized after reviewing all Python Server Action scripts under `platforms/odoo/16/`.

## Standard applied

### Read-only scripts

Read-only scripts must:

- have `READ-ONLY:` in the action name/header/output;
- use `PAGE = 1` and `PAGE_SIZE = 80000`;
- write no data: no `create`, `write`, `unlink`, `set_param`, commits, or SQL writes;
- emit paged output with a footer in this form:

```text
--- END PAGE <n> | MORE REMAINS: YES/NO ---
```

### Write-capable scripts

Write-capable scripts must:

- default to `APPLY = False` and `CONFIRM = ''`;
- print a dry-run plan before any write;
- require an exact confirmation token before applying;
- run writes inside an explicit savepoint;
- roll back the savepoint on failure;
- invalidate ORM cache after writes;
- avoid unsafe `safe_eval` helper functions such as `getattr`, `hasattr`, `setattr`, `eval`, `exec`, `open`, `dir`, and `isinstance` in executable code.

## Files audited

### Installers

- `installers/commercial/barani_commercial_q_so_pf_report_installer_Q-SO-PF-2026v3_PF_NO_DUEDATE_plus_NOQ_ALLDOCS_DRYRUN_SAFE.py`
- `installers/delivery-note/barani_delivery_note_report_installer_DN_L1_QR_ONLY_DDS_FREE_SAFE.py`
- `installers/vat/barani_vat_report_tune_L22_EMAIL_AND_NOTE_FALLBACK_SAFE.py`

All three are write-capable installers and have:

- `APPLY = False` default;
- `CONFIRM = ''` default;
- dry-run branch;
- savepoint / rollback pattern;
- no unsafe reflection/helper calls found by textual scan.

### Backup / restore / export support

- `support/backup-restore-export/barani_vat_template_export_READONLY_L22_FINAL_SAFE.py`
- `support/backup-restore-export/barani_vat_create_CURRENT_RESTORE_POINT_L22_FINAL_SAFE.py`
- `support/backup-restore-export/barani_vat_restore_FROM_CURRENT_L22_FINAL_SAFE.py`
- `support/backup-restore-export/barani_delivery_note_export_READONLY_v2.py`
- `support/backup-restore-export/barani_delivery_note_probe_READONLY_v2.py`
- `support/backup-restore-export/barani_delivery_note_create_CURRENT_RESTORE_POINT_SAFE.py`
- `support/backup-restore-export/barani_delivery_note_restore_FROM_CURRENT_SAFE.py`

Changes made:

- Delivery Note read-only probe now uses `PAGE_SIZE = 80000` and the full read-only header/output format.
- Delivery Note export now uses the full read-only header/output format.
- Delivery Note create-restore-point script now has a full boxed header, dry-run plan, savepoint, rollback, and cache invalidation pattern.
- Delivery Note restore script now has a full boxed header, savepoint test, dry-run plan, rollback, and cache invalidation pattern.
- VAT L22 export wording corrected from stale L21 wording to L22, and output action name standardized to `READ-ONLY:`.

### Tax / fiscal-position support

- `support/tax-fiscal-position/barani_new_db_downpayment_accounting_readiness_probe_READONLY_v2.py`
- `support/tax-fiscal-position/barani_option_b_included_downpayment_tax_audit_READONLY.py`
- `support/tax-fiscal-position/barani_oss_included_advance_tax_audit_READONLY.py`
- `support/tax-fiscal-position/barani_tax_fiscal_position_full_verify_READONLY.py`
- `support/tax-fiscal-position/barani_oss_included_advance_tax_create_and_map_SAFE.py`

Changes made:

- Read-only probes now use `PAGE_SIZE = 80000`.
- `barani_option_b_included_downpayment_tax_audit_READONLY.py` now has `PAGE` / `PAGE_SIZE` paging and standard read-only output footer.
- Read-only output lines now consistently use `READ-ONLY:YES — search/read only; no writes` style.
- Write-capable OSS create/map script already had dry-run, confirmation, savepoint, and rollback pattern.

## Validation

All Python files under `platforms/odoo/16/` compile successfully with Python syntax validation after this cleanup.

This audit is repository hygiene only. It does not alter Odoo business logic, QWeb templates, taxes, fiscal positions, accounts, reports, or generated documents.
