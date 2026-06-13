# dds_barani uninstall notes

This document family is designed so the 2026+ customer-facing templates do not depend on `dds_barani` QWeb inheritance or `brn_*` fields.

Before uninstalling any custom module in a real database:

1. run the uninstall-readiness probe;
2. export any non-empty custom field values you might want to preserve;
3. test uninstall on staging/restored copy;
4. smoke-test VAT invoices, Q/SO/PF, DN, products, partners, pickings, and exports.

Do not confuse `dds_barani` with other DDS modules that may still provide accounting/localization/export behavior.
