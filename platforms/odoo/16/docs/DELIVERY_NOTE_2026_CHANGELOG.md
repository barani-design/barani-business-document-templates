# Delivery Note / Picking Operations 2026+ Changelog

## 2026-06-17 — Reconciled final v4 repo package

- Reconciled against `barani_business_documents_dn_pickops_repo_update.zip`.
- Kept the attached package's repo-root update workflow and existing `delivery-note` / `pick-list` taxonomy.
- Replaced the attached v1 installers with v4 installers retaining savepoint/cache/readback safety.
- Delivery Note body includes DN L2 customs/package behavior, non-kit package fallback, address-label unification, BARANI red `#ed1c24`, and parent-company ID/VAT fallback.
- Picking Operations body includes internal exploded rows, barcode columns, notes/contact/prepared-by cosmetics, duplicate transfer-number removal, BARANI red `#ed1c24`, and parent-company ID/VAT fallback.
- Incremental hotfixes are consolidated; use final installers for clean database installs.
