# Odoo 20 migration work

The unchanged Purchase candidate `barani_purchase` 20.0.1.0.3 is preserved under `addons/barani_purchase/`. Its source is independently accepted offline. Full native readiness, the 22 application runtime tests, four actual Purchase PDFs and real-data migration remain incomplete. **Runtime-01 remains HOLD.**

Read [the Purchase checkpoint](checkpoints/purchase-20261016/README.md) before resuming. Odoo's reply supplied on 16 October 2026 gives Q1 2027 as the expected v20 upgrade-script window; availability must be confirmed later. This branch is not a production release and does not update the Odoo.sh parent repository.

Other business-document families remain separate work. The Odoo 16 maintained sources and accepted-current snapshots, and the Odoo 19 implementations, are historical inputs to preserve. They are not automatically compatible with v20. A complete migration still requires installed views, real rendering, business workflows, upgraded-data acceptance and an approved rollback/cutover plan.
