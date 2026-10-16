# Remaining v20 work

| Area | Prepared now | Still required |
|---|---|---|
| Purchase PO/RFQ | Frozen offline-accepted 20.0.1.0.3 published at 9c80f35f | Readiness successor, 22 real tests, four PDFs, visual and later upgrade acceptance |
| Commercial | New separate v20 source candidate and adapted/extended tests | Mac lint, native execution, PDF/business acceptance |
| Delivery/Picking | New separate v20 source candidate; Prepared Date preserved | Mac lint, stock/package/serial/kit/native execution and PDF acceptance |
| VAT invoices/advances/credit notes | New separate v20 source candidate and tests | Mac lint, native accounting/report/attachment/preview/fullset acceptance |
| Payment Reference | Source inventoried at 19.0.1.0.0 | Port with Tax Rules and POHODA dependencies; order/invoice/export tests |
| Tax Rules | Production-linked manifest says 19.0.1.1.8 | Reconcile exact protected .10 authority before any port; do not substitute older source or change existing .10 |
| POHODA | Source inventoried at 19.0.3.3.46 | v20 accounting/API port, export/schema/advance/reference regression and interface acceptance |
| Intrastat SK | Source inventoried at 19.0.2.6.28 | Native Enterprise v20 contract port, report extraction/schema/rounding/configuration tests |
| Warranty Check | Database-native app identified in source inventory | Exact source/current metadata reconciliation, native API adaptation and synthetic tests |
| DDS unreserve / other automations | Inventory records an unresolved business-intent HOLD | Preserve exact source; resolve intended selection before replacement; inventory remaining DB-only objects |
| Customs Documents | Archived 16.0.0.2.0-alpha.3, installable=False | Keep archived; not an installed v20 migration dependency |
| Whole system | Source graph and phased test plan | Current customization completeness, combined integration tests, release pin review |
| Real data | Deliberately deferred by owner | Official upgrade rehearsal, data/identifier/configuration reconciliation, acceptance and rollback before go-live |

Order of work: finish document candidate validation; reconcile authoritative Tax
Rules source; port the coupled Tax Rules/Payment Reference/POHODA set; port
Intrastat against the matching Enterprise target; reconcile Warranty and other
database-native customizations; test the combined release. These remaining source
ports are not claimed completed by the document package.

The inventory source is production-repository commit eb69634c7e7d42586a01c48b8dc57072044b0c84.
It states that full current database-native inventory is still incomplete. Its old
Purchase Git-publication gap has since been closed by checkpoint 9c80f35f.
Odoo's owner-supplied 16 October support reply expects the production upgrade
script in Q1 2027. This is a planning window, not a guaranteed release date. The
existing dev20 build is not production-upgrade availability.
