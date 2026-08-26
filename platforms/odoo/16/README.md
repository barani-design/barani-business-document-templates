# Odoo 16 implementation

Status: production-verified template baseline.

Sources of truth:

- `templates/` — maintained portable QWeb sources.
- `accepted-current/2026-08-26-production-template-closeout/` — locked production-accepted QWeb hashes and behavioral contract.

The `installers/` and `support/` directories contain useful Odoo 16 Server Actions from multiple milestones. Some installers predate the latest accepted source. Never infer current production state from an installer filename alone; compare it with the accepted-current metadata and validate on a disposable database before clean installation.

Production-bound closeout actions are intentionally not published because they contain tenant identity, backup, restore, and record guards. Future deployment tooling should resolve views and actions by stable logical identity and fail closed on drift.

For the planned Odoo 20 port, start at `../20/README.md` and do not replay these Server Actions.
