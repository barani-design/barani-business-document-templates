# R1 — Backup / export / restore flow

## Before changing templates

```text
1. Run a read-only export script.
2. Run a create-current-restore-point script with APPLY=False.
3. Review the output.
4. Run create-current-restore-point with APPLY=True and the exact confirmation token.
5. Apply the installer with APPLY=False first.
6. Apply with APPLY=True only after the dry-run is clean.
7. Export the live templates after installation.
````

## Restore principle

Restore scripts should read only known `ir.config_parameter` restore-point keys and restore only BARANI-owned artifacts whose technical identity matches the expected report/view keys. They must not touch stock Odoo, DDS, or Studio templates.

## Public package note

Do not publish live restore-point values. Commit only scripts and sanitized template examples.
