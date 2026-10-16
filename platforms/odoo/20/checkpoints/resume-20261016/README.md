# Odoo 20 upgrade — resume here

**Status at 16 October 2026: source preparation is partly complete and published. The complete BARANI system is not accepted for v20, Runtime-01 is on HOLD, and real-data migration has not run.**

This is the current cross-repository status and restart guide for the pause. It records the work completed in the Purchase controller chat and identifies work that remains. It is a documentation-only successor of the published document checkpoint. Every application file, version and prior checkpoint is unchanged.

Start with this page and [STATUS.json](STATUS.json). [EVIDENCE_INDEX.json](EVIDENCE_INDEX.json) records evidence identities and limits. Earlier checkpoint files are historical records; later decisions below supersede their stale status paragraphs without rewriting their history. A future controller should read the exact source and evidence, not infer completion from a branch name or this narrative alone.

## Exact published source checkpoints

Use full commit IDs when resuming. Branch tips may move after this snapshot. These repositories have different roles; they have not been combined into an installable v20 release.

| Repository and branch | Exact commit | Purpose and current acceptance |
| --- | --- | --- |
| `barani-design/barani-business-document-templates` — `p20-reference-documents-20261016-r1` | [`c5de4242a3bfd5fb25f451d3a085d6c253a12672`](https://github.com/barani-design/barani-business-document-templates/commit/c5de4242a3bfd5fb25f451d3a085d6c253a12672) | Latest document source: frozen Purchase, Commercial, Delivery and VAT reference correction. Remote commit/tree/parent verified. Native document/PDF acceptance pending. |
| `barani-design/barani-odoo-addons` — `p20-pohoda-gates-20261016-r1` | [`04dea5f6d991b7fd7f43b38da99e802cbc59b6ea`](https://github.com/barani-design/barani-odoo-addons/commit/04dea5f6d991b7fd7f43b38da99e802cbc59b6ea) | Latest private addon checkpoint: POHODA source/gate port plus unchanged Payment Reference and protected Tax Rules .10. Remote publication verified. Other root addons remain historical versions; do not install the whole checkout as a v20 set. |
| `barani-design/barani-odoo-production` — `p20-purchase-readiness-20261015-r1` | [`620dbdf50801ac9ee4310c47eaa14868ed58068f`](https://github.com/barani-design/barani-odoo-production/commit/620dbdf50801ac9ee4310c47eaa14868ed58068f) | Separate native hosted development bootstrap; no Purchase application included. It is not the production branch or an integration release. |

The documents source tree is `6ddddb380aeab7f484447859aba66c785748c5d8`; its parent is `5e13c2b592a3d47a37f432a94b7cb89001ac363e`. The addon source tree is `231f8864f6291885515fb8abf99f295a2ecb3df4`; its parent is `507054c5d9618a561defcd17917b66ef75423e6c`.

Historical document checkpoints remain available: Purchase `9c80f35ff6a5d7ade9a7e8cd3b0a66e0db9063a8`, then document candidates `5e13c2b592a3d47a37f432a94b7cb89001ac363e`, then the reference correction above. The coupled-addon predecessor is `507054c5d9618a561defcd17917b66ef75423e6c`. Follow the latest checkpoint for current status while retaining the older evidence.

## What is ready, and what is not

| Component | Prepared version / result | Work still required |
| --- | --- | --- |
| Purchase PO/RFQ | `20.0.1.0.3`; independently accepted offline and frozen. 12 source files retained exactly. | Establish native readiness; run 22 real Odoo tests; generate and accept four actual Purchase PDFs; later upgrade/data acceptance. |
| Commercial: quotation/SO/pro-forma | `20.0.1.0.0`; v20 source candidate and native test definitions published. | Native installation, report routing/rendering, business workflow and PDF review. Full original document Mac evidence was not returned to this controller; do not invent a complete evidence acceptance. |
| Delivery / Picking | `20.0.1.0.0`; v20 source candidate published; Prepared Date remains tied to completed delivery. | Stock/package/serial/kit cases, native tests and PDF review; same original document-evidence limitation. |
| VAT invoice / DPI / credit note | `20.0.1.0.1`; stored-reference correction published. New Mac return audited PASS: 25 focused offline tests; Ruff over 15 scoped Python files; six changed paths. | 23 retained plus five new native test definitions have not run. Real invoices, down payments, settlements, credits, report attachments/preview and PDFs need native acceptance. |
| Order Payment Reference | `20.0.1.0.0`; published in private coupled checkpoint; established assignment behavior retained. | Native interaction with Tax Rules, invoices, reports and POHODA. Keep existing optional setting behavior; no silent configuration change or adoption of unmarked invoices. |
| Tax Rules | Exact protected `20.0.1.1.10` source carried unchanged in private checkpoint. Recorded static and focused browser evidence is bounded. | Combined native business/UI regression and the existing open issue review. A focused browser check is not whole-module runtime acceptance. Do not replace it with production's older source or bump it by default. |
| POHODA | `20.0.3.3.46`; v20 source and gate successors published. 49 source gates, 173 offline negative cases, 20 new offline regressions and returned pinned Mac Ruff passed. | 891 retained Odoo test identities are NOT_RUN. Native installation/migration hooks, discovery/execution, browser behavior, XML/export/advance/reference cases and combined acceptance remain. |

Tax follow-up retains the recorded B1 managed-order change decision, O1 reload-recovery behavior, deferred O2 accessibility disposition, and B3/R8 migrated-copy/combined qualification. Preserve the existing B4 lock behavior. The historical 55-test result for Tax .9 is not a fresh .10 test result. These are review items, not authorization to edit protected .10.

The 25 reference tests use candidate method bodies/XML expressions with synthetic records. POHODA's offline checks likewise do not establish ORM, browser, accounting or migration correctness. A passing source checkpoint is not a production-ready release.

Purchase content SHA-256 remains `bc81e637529172588f797addcfa6fdec92863ac3633d8af61bd13ae806567ca2`; Git subtree `a1bd871def34dc3a6e0be55d549a8cc5f198d3ec`. Protected Tax .10 content SHA-256 is `c1c6879245341117592b9509ba320d2735cca2b306794fda33b8e409b02fdfd5` under its recorded authority's content algorithm. Hashes must be compared with the same manifest algorithm and scope.

## Business decisions that must survive the pause

The owner confirmed that customers commonly pay before an invoice exists. Accountants match those payments through the pro-forma. **Keep one SO-derived numeric payment reference throughout the documents for that order, while retaining each invoice's separate legal number.**

| Document | Document number | Payment reference |
| --- | --- | --- |
| Pro-forma | `PF/126/00017` | `12600017` |
| Later invoice | `INV/926/00042` | `12600017` |

The older numbering-policy PDF's separate invoice-family reference rule is superseded by this owner decision. Do not ask the same policy question again. See [the recorded policy](../REFERENCE_POLICY_20261016.md).

VAT PDFs now use the saved reference and call existing companion validation for managed records. They do not manufacture a reference by stripping punctuation or concatenating `invoice_origin`. Unmarked native/manual references and leading zeroes remain intact. A credit's original reference comes from its linked original invoice; an unlinked credit does not guess. Customer credits continue to suppress their own payment request. Payment state does not change reference identity. Existing bank-band layout, balance labels and financial calculations were not redesigned.

Managed RI/DPI/settlement references still require combined native verification. The managed DPI POHODA override uses the stored reference; unmarked DPI retains the exporter's configured origin/blank/reference behavior. Do not claim universal PDF/POHODA equality before checking the applicable policy.

The approved POHODA registration selection also remains: one eligible nonblank native EN identifier is selected automatically; multiple candidates require an explicit contact selection; stale/invalid selections block export; absence retains the existing absent-identifier behavior. Do not infer company registration identifiers from VAT numbers. The same identifier text under two eligible identifier types still requires a choice (for example, two EN types). Customer and seller identities must follow the actual invoice/contact/company source, with the selection bound into the established evidence fingerprint.

## Why runtime remains on HOLD

Two different environments were examined:

- **Preserved Docker attempt:** Runtime-01 PROBE_FIX_R2 evidence was accepted, but its selected renderer did not report patched Qt. Diagnostic R3 collection passed; runtime readiness did not. Keep the original Mac workspace, native TAR, exact stopped owned probe and all attempt markers. Never rerun original/R2 launchers or erase guards.
- **Hosted development target:** the platform wrapper led to `wkhtmltopdf 0.12.6.1 (with patched qt)` and passed a synthetic two-page header/footer smoke. This was not an Odoo report or an accepted Purchase PDF, and it does not prove the running server's renderer selection. Preserve the platform wrapper's scheduling behavior; do not silently bypass or replace it.

The hosted Community source pin was `a7950cab13fcb9400d58d582f5583c0f1c0f5405`, with Enterprise `d68e2160cdb4bf4de3756314b7731a89974c2163`. These historical pins differ from the Docker basis; there is no equivalence claim. The declared target was development Odoo 20, build `39948538`. It may expire or change during the pause.

Selected dependency/import, CLI, PDF helper, libmagic and read-only technical database checks were collected. They did not establish complete native readiness. The latest addon planner **R2 stopped at its 250-module candidate-closure limit** and returned no complete catalog/closure. Its preservation result covered prior named identities only. The limit is a planning failure, not proof of a missing addon and not permission simply to increase the cap. Resolve native auto-install and conditional selection semantics, saving the catalog before closure planning. Reassess actual relevance of unresolved `serial` and `usb`; do not turn metadata differences alone into acceptance or package-install instructions.

The owner's 16 October support reply described Q1 2027 as an expected production-upgrade-script window. This is historical planning context, not a guaranteed date or evidence of current availability. Development v20 availability does not establish production-upgrade availability.

## Remaining migration work beyond these checkpoints

| Area | Recorded position / next work |
| --- | --- |
| Intrastat SK | Inventoried `19.0.2.6.28`; v20 native Enterprise contract port, extraction/schema/rounding/configuration tests remain. Do not use the much older attached v16 archives as current source authority. |
| Warranty Check | Database-native app identified; exact current source/metadata reconciliation, v20 API adaptation and synthetic/native tests remain. |
| DDS unreserve / Server Actions / Scheduled and Automated Actions / Studio | Inventory is incomplete. Preserve current source and resolve the recorded unreserve-selection intent before replacing behavior. Reconcile database-only objects and tenant configuration. |
| Autosave customization | Confirm installed third-party module and supported v20 behavior; do not assume the earlier trial proves readiness. |
| Customs Documents | Archived `16.0.0.2.0-alpha.3`, `installable=False`; remains deferred and is not an installed v20 migration dependency. |
| Cross-module release | Select exact compatible commits, resolve remaining ports/dependencies, then test the combined reports/payment/tax/export/stock workflows. No combined installable branch or parent gitlink release has been accepted. |
| Real-data migration | Intentionally deferred. Official upgrade rehearsal, data/configuration/identifier reconciliation, business acceptance, backup/rollback and cutover are still required before go-live. |

Production and other chats may continue changing Odoo 19 during this pause. At resumption, reconcile all source and configuration changes since this snapshot; these October pins are not a claim about the future production baseline. Obtain the separate inventory auditor's current result if available. Do not describe this document as a complete tenant inventory.

## Resume in this order

1. **Read this guide and verify exact identities.** Locate the retained evidence through EVIDENCE_INDEX.json and the linked prior checkpoints. Verify relevant archive sidecars, source commits and protected content. Reuse accepted results; do not routinely repeat accepted static suites, rebuild frozen Purchase, bump its version or start another application build. If evidence/resources are missing, record the exact gap instead of reconstructing history from prose.
2. **Confirm the supported target and production upgrade availability.** Capture actual current Community/Enterprise release/build and compare changes with the historical pins. Record production customizations added during the pause. Plan targeted checks for genuine target/source drift.
3. **Finish remaining source work and runtime readiness.** Correct the addon planner with offline fixtures; then use a new bounded collector to establish its complete catalog/closure and dependency compatibility. Preserve old attempts. No package/image download, build/substitution or renderer change is implied by this guide.
4. **Prepare a NEW one-shot runtime continuation from actual retained state.** Reuse the reviewed post-readiness path in `RUN_RUNTIME01.py:continue_after_runner_probe` and `ODOO_JOB.py`, explicitly adapting environment-specific assumptions. Never retry consumed launchers. Original named Docker-resource authorization does not itself authorize hosted installation/database writes; obtain only genuinely new resource/write scope, not wholesale Runtime-01 reapproval.
5. **Execute native application and integration acceptance only after readiness and scope are satisfied.** Include Purchase's 22 tests/four PDFs, all relevant document cases, POHODA discovery/execution, protected Tax/reference interactions, stock behavior, installed browser assets and export schema checks. Validate saved reference versus customer PDF and applicable POHODA output. Require patched Qt and actual multipage headers/footers plus visual/business review. Include VAT legacy Preview and fullset cases explicitly; a generic report tag is not proof they ran. Missing native `sale_mrp`, HS/origin or Enterprise prerequisites remain HOLD conditions, not hidden skips. Record skips/failures honestly.
6. **Rehearse real-data upgrade and then decide release.** Check configuration, identifiers, accounting balances, report attachments, migration hooks and real workflows; prepare rollback. Only an explicitly reviewed release may change parent gitlinks, existing staging/production or deployment. Source publication alone never authorizes go-live.

## Evidence and authority notes

The source checkpoints were published through GitHub Desktop and their remote identities verified. This guide itself is prepared for the same publication route; its current publication must be established from GitHub, not inferred from this sentence.

The first document package's printed local result was received, but its complete Mac evidence archive was not audited here. The later coupled-addon, POHODA-gate and reference-document returns were audited within their stated scopes. Before/after preservation refers to recorded Git identities/metadata, not an exhaustive byte inventory of every historical working-tree file.

The earlier documents remaining-work table predates the Payment Reference/Tax/POHODA checkpoints. The POHODA gate kit's “Ruff pending” paragraph predates its passing Mac return. An earlier POHODA review also recorded a pre-publication 404 and an undecided reference policy; publication and the owner's constant-reference decision resolved those items. Proposed paid/DPI layout changes in older discussion were not approved or implemented by the narrow reference correction.

Useful historical detail: [Purchase checkpoint](../purchase-20261016/README.md), [Purchase resume constraints](../purchase-20261016/RESUME.md), [document candidate checkpoint](../documents-20261016/README.md), and [reference policy](../REFERENCE_POLICY_20261016.md). Do not include customer PDFs, database dumps, account statements, credentials or private support emails in this public repository.
