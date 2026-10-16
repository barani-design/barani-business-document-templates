# Purchase v20 checkpoint — 16 October 2026

This branch preserves the unchanged, offline-accepted `barani_purchase` 20.0.1.0.3 candidate. It is a source checkpoint, with Runtime-01 still on HOLD. It is not an installable release recommendation or acceptance of the whole BARANI v20 migration.

## Completed and outstanding

| Area | Recorded result |
|---|---|
| Purchase source port | Offline accepted and frozen; 12 application files unchanged |
| Accepted offline verification | Previously completed; not replayed for this checkpoint |
| Separate hosted v20 development target | Created and identified; no Purchase application installed by these probes |
| Hosted patched-Qt renderer | Synthetic two-page header/footer smoke passed; actual Purchase reports not tested |
| Native checks | Selected imports, CLI, PDF helpers, libmagic and read-only technical DB metadata checked |
| Full runtime readiness | Not established; dependency/source planning incomplete |
| Latest source planner | R2 stopped at its conservative 250-module candidate cap; no complete catalog/closure returned |
| Purchase runtime tests | 0 of 22 executed |
| Actual Purchase PDFs | 0 of 4 produced or accepted |
| Real 19-to-20 database migration | Not run |
| Other BARANI modules and integration | Not assessed by this Purchase checkpoint |
| Production upgrade and deployment | Waiting; no cutover or deployment acceptance |

Odoo's reply supplied by the owner on 16 October 2026 says the v20 upgrade script is expected in Q1 2027. This is the communicated window, not a guaranteed release date. A dev server declaring 20.0 does not establish production upgrade availability. The private email and its unrelated subscription history are not published here.

## Branch boundary

The branch starts from the exact historical Purchase source parent, `66d67448c94db3313365b2cc93d3336791d864e7`; it is not a merge of the latest repository main branch. The existing Odoo 19 Purchase tree is preserved. The frozen module is placed separately at `platforms/odoo/20/addons/barani_purchase/`. Module-relative bytes and modes are unchanged. Repository additions are not application edits.

This checkpoint does not update the Odoo.sh parent repository, a parent gitlink, any existing branch, Tax Rules .10, or an existing environment. It adds no packages, renderer substitutions, runtime retries, or application version change.

See `STATUS.json`, `EVIDENCE_INDEX.json`, `APPLICATION_INVENTORY.json` and `RESUME.md`. Evidence summaries distinguish integrity from runtime acceptance. Original evidence remains outside this public repository.
