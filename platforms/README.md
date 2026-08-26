# Platform implementations

This repository is organized by platform and application version.

Current implementations:

- `odoo/16/` — production-verified Odoo 16 Server Action and QWeb baseline.
- `odoo/19/` — reserved placeholder; no validated implementation.
- `odoo/20/` — planned migration target; no deployable implementation yet.

The locked Odoo 16 migration baseline is:

`odoo/16/accepted-current/2026-08-26-production-template-closeout/`

That snapshot is behavioral acceptance evidence and migration input, not executable Odoo 20 code. Each version must independently validate QWeb inheritance, report APIs, model fields, report actions, filename expressions, bindings, Preview routing, paper formats, and rendering. Never replay Odoo 16 Server Actions on another Odoo version.

Shared process-flow documentation lives in the root `docs/` folder. Version-specific templates, installers, probes, migration notes, and verification evidence belong under their platform/version folder.
