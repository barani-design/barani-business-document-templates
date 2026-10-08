# BARANI Odoo 19 app index

Documentation closeout: **8 October 2026**, evidence reconciled in review revision 4. This covers the eight apps in the
owner's installed inventory, plus the archived Customs module. It is a pinned
source/documentation index, not a new database inventory or Odoo 20 acceptance.

Seven installed apps use addons commit `3d0b241d0b35d7619b87bdf4b0a57238150a0df8`. Purchase uses public
templates commit `66d67448c94db3313365b2cc93d3336791d864e7`. The manifests determine the versions and direct
dependencies below. Private links require existing access; private source and
runtime evidence are not copied into this public repository.

| App / pinned source | Version | Direct dependencies |
|---|---|---|
| [barani_commercial](https://github.com/barani-design/barani-odoo-addons/tree/3d0b241d0b35d7619b87bdf4b0a57238150a0df8/barani_commercial) | `19.0.1.0.2` | `sale_stock` |
| [barani_delivery](https://github.com/barani-design/barani-odoo-addons/tree/3d0b241d0b35d7619b87bdf4b0a57238150a0df8/barani_delivery) | `19.0.1.0.6` | `sale_stock` |
| [barani_vat](https://github.com/barani-design/barani-odoo-addons/tree/3d0b241d0b35d7619b87bdf4b0a57238150a0df8/barani_vat) | `19.0.1.0.3` | `sale_stock` |
| [barani_purchase](https://github.com/barani-design/barani-business-document-templates/tree/66d67448c94db3313365b2cc93d3336791d864e7/platforms/odoo/19/addons/barani_purchase) | `19.0.1.0.2` | `purchase_stock` |
| [barani_intrastat_sk](https://github.com/barani-design/barani-odoo-addons/tree/3d0b241d0b35d7619b87bdf4b0a57238150a0df8/barani_intrastat_sk) | `19.0.2.6.28` | `account_intrastat`, `mail`, `sale_management`, `stock` |
| [barani_pohoda_export](https://github.com/barani-design/barani-odoo-addons/tree/3d0b241d0b35d7619b87bdf4b0a57238150a0df8/barani_pohoda_export) | `19.0.3.3.46` | `base`, `account`, `sale_management`, `product`, `mail`; Python `lxml` |
| [barani_tax_rules](https://github.com/barani-design/barani-odoo-addons/tree/3d0b241d0b35d7619b87bdf4b0a57238150a0df8/barani_tax_rules) | `19.0.1.1.8` | `sale_management`, `sale_stock`, `account`, `mail` |
| [barani_order_payment_reference](https://github.com/barani-design/barani-odoo-addons/tree/3d0b241d0b35d7619b87bdf4b0a57238150a0df8/barani_order_payment_reference) | `19.0.1.0.0` | `barani_tax_rules`, `barani_pohoda_export` |

All eight inspected manifests declare `LGPL-3`. The four report modules are
available under [addons/](addons/); the other four remain private. See the
[catalog](README.md) for report installation, company-specific values,
native action overrides and the separate root/asset license notices.

## Implemented behavior, configuration and limits

**Commercial.** Quotations, sales orders and pro-formas use BARANI layouts,
payment-reference display and native report routes. Configure company identity,
colors, receiving bank, payment terms and fiscal positions; pro-formas retain
the native access group. Bank selection and EXW fallback are company-specific.
This report does not implement invoice creation or bank reconciliation.
Public pinned [source](https://github.com/barani-design/barani-business-document-templates/tree/c69910a0769887c5592cd0202615ba8a96eeb0ec/platforms/odoo/19/addons/barani_commercial)
and [tests](https://github.com/barani-design/barani-business-document-templates/tree/c69910a0769887c5592cd0202615ba8a96eeb0ec/platforms/odoo/19/addons/barani_commercial/tests).

**Delivery.** Delivery Notes, a sales-order delivery route and Picking Operations
use stock quantities and product QR codes. Completed/picked quantities use
read-only Odoo 19 adapters. Prepared Date uses `date_done`, blank when unset;
it does not fall back to scheduled date. Configure company/warehouse/product
facts and document timezone. These reports do not complete transfers.
Public pinned [source](https://github.com/barani-design/barani-business-document-templates/tree/c69910a0769887c5592cd0202615ba8a96eeb0ec/platforms/odoo/19/addons/barani_delivery)
and [tests](https://github.com/barani-design/barani-business-document-templates/tree/c69910a0769887c5592cd0202615ba8a96eeb0ec/platforms/odoo/19/addons/barani_delivery/tests).

**VAT.** Invoice, down-payment and credit-note layouts, native invoice routes
and Invoice Preview use BARANI references, totals and payment presentation.
Configure company/bank data and native accounting/tax facts. The printed
reference preference does not repair historical stored invoice references or
change taxes, posting, payment matching or reconciliations.
Public pinned [source](https://github.com/barani-design/barani-business-document-templates/tree/c69910a0769887c5592cd0202615ba8a96eeb0ec/platforms/odoo/19/addons/barani_vat)
and [tests](https://github.com/barani-design/barani-business-document-templates/tree/c69910a0769887c5592cd0202615ba8a96eeb0ec/platforms/odoo/19/addons/barani_vat/tests).

**Purchase.** Priced PO and unpriced RFQ share the company layout, supplier and
delivery blocks; PO totals use native tax totals. Configure company, warehouse,
delivery address, incoterms and terms. Reports force English. Native action
backup/restore hooks protect takeover; `.2` fixes the RFQ class selector.
See [PO/RFQ history and acceptance](RFQ_LAYOUT_260919.md).

**Intrastat SK.** Dispatch-only Slovak XML, freight/insurance allocation by raw
product net weight, preflight snapshots, field validation, recipient overrides,
traceability and XSD validation extend native `account_intrastat` reportability.
Provide that dependency, configure company/reporting identity, shipping rules,
recipient facts and the pinned official XSD/approval chain. Arrival filing is
not released; historical Arrival batches remain readable. Portal acceptance is
a separate business result, not implied by source installation. The accepted
`.28` development module tree matches the production source exactly.
Use the existing [guide map](https://github.com/barani-design/barani-odoo-addons/blob/3d0b241d0b35d7619b87bdf4b0a57238150a0df8/docs-user/BARANI_INTRASTAT_DOCS_00_MAP_AND_FLOWS.md),
[monthly guide](https://github.com/barani-design/barani-odoo-addons/blob/3d0b241d0b35d7619b87bdf4b0a57238150a0df8/docs-user/BARANI_INTRASTAT_DOCS_10_MONTHLY_DECLARATION_GUIDE.md),
[configuration reference](https://github.com/barani-design/barani-odoo-addons/blob/3d0b241d0b35d7619b87bdf4b0a57238150a0df8/docs-user/BARANI_INTRASTAT_DOCS_21_CONFIGURATION_FIELD_REFERENCE.md)
and [.28 release note](https://github.com/barani-design/barani-odoo-addons/blob/3d0b241d0b35d7619b87bdf4b0a57238150a0df8/barani_intrastat_sk/docs/RELEASE_NOTES_19.0.2.6.28.md).
The module README still names `.19`; use the manifest and `.28` note for version
identity. The `.28` change concerns configuration-form layout, not business rules.

**POHODA Export.** Native invoice/advance/settlement/credit-note classification,
mapping gates, cumulative advance capacity, request XML/XSD validation and manual
response import. It does not automatically transmit to POHODA. Configure company,
journals, dictionaries, fiscal profiles, reviewed mapping cells and XSD bundle.
Native productless down-payment matching is opt-in and requires 324-account and
native same-company down-payment links. `.46` defaults only a missing legacy
settings element to false; empty/invalid Booleans remain errors. Approval and
fingerprint checks remain enforced. Managed Tax Rules advances stay blocked.
Use the [README](https://github.com/barani-design/barani-odoo-addons/blob/3d0b241d0b35d7619b87bdf4b0a57238150a0df8/barani_pohoda_export/README.rst),
[native down-payment note](https://github.com/barani-design/barani-odoo-addons/blob/3d0b241d0b35d7619b87bdf4b0a57238150a0df8/docs/pohoda/260927_02/Native_downpayments.md)
and [.46 import repair](https://github.com/barani-design/barani-odoo-addons/blob/3d0b241d0b35d7619b87bdf4b0a57238150a0df8/docs/pohoda/260927_05/Legacy_settings_repair.md).
The README's Odoo 16 installation line and old migration examples are historical;
this manifest targets Odoo 19. A retained staging review confirms the corrected positive zero-VAT advance
mapping in regenerated XML. Desktop import/accounting acceptance was waived
by the owner and remains assumed working, not verified; final-settlement import
is also unverified. This waiver is not a new publication gate.

**Tax Rules.** Saved company/purchaser/product/transaction facts resolve native
order taxes and fiscal positions. It provides controlled adoption of eligible
orders, purchaser-category guards and ordinary single-treatment invoice flow.
Configure company policy, purchaser evidence, product purposes and approved
tax/fiscal mappings. New-order automation and all-document purchaser enforcement
default off; managed documents retain their checks. It does not perform VIES.
Full invoice tax lifecycle, managed advances, grouped-treatment workflows and
POHODA import validation remain outside implemented acceptance. `.8` restores
native sales-line dragging by preserving sequence metadata; it does not
resequence history or require enabling tax automation.
Use the [README](https://github.com/barani-design/barani-odoo-addons/blob/3d0b241d0b35d7619b87bdf4b0a57238150a0df8/barani_tax_rules/README.md),
[in-app help](https://github.com/barani-design/barani-odoo-addons/blob/3d0b241d0b35d7619b87bdf4b0a57238150a0df8/barani_tax_rules/static/description/help.json)
and [line-order repair note](https://github.com/barani-design/barani-odoo-addons/blob/3d0b241d0b35d7619b87bdf4b0a57238150a0df8/docs/tax/260929_08/Sales_line_ordering.md).

**Order Payment Reference.** Optional companion; install explicitly and enable
**Use order/PF payment references** for the company (default off). New native
order-generated customer invoices save the numeric Q/SO/PF reference and verify
its protected source snapshot at posting/POHODA serialization. Different orders
remain separate invoices while enabled. Regular, native advance and positive
settlement invoices are covered; managed-order advance guards still apply.
Manual/copy/credit-note flows retain native behavior. Existing invoices are not
rewritten, and disabling the policy does not rewrite marked invoices.
Use its [README](https://github.com/barani-design/barani-odoo-addons/blob/3d0b241d0b35d7619b87bdf4b0a57238150a0df8/barani_order_payment_reference/README.md)
and [integration note](https://github.com/barani-design/barani-odoo-addons/blob/3d0b241d0b35d7619b87bdf4b0a57238150a0df8/docs/tax/260926_04/Order_payment_reference.md).
Their inspected POHODA `.44` baseline is historical; the current source pin
contains `.46` and Tax Rules `.8`.

## Actual test and acceptance evidence

The following includes recovered private acceptance records reviewed on
8 October 2026. The Intrastat `.28` module tree and all 304 files across Tax Rules
`.8`, POHODA `.46` and Payment Reference `.0` match the pinned production source.
Their committed preparation notes saying “pending” predate these results. Only
sanitized outcomes are recorded here; runtime logs and customer evidence remain
private. No Odoo tests, deployment, portal filing or accounting import were
repeated.

On 8 October, the owner recalled accepting the final Odoo 19 staging versions
before they went live, except the Delivery `.6` date correction, which went
directly from development to production. This is retrospective owner-reported
release acceptance of the staging releases; Delivery retains its separately
recorded targeted production check. It does not reconstruct individual checklist results, supply missing
automated logs, or override the explicit POHODA posting-test waiver. The record
limits below remain visible without reopening completed release acceptance.

| App / scope | Recorded evidence | Limit or missing record |
|---|---|---|
| Commercial / VAT | Published production source; existing rendering/routing tests retained; public snapshot workflow passed | No full suite rerun at this publication; current versions must not inherit an unqualified historical pass |
| Delivery `.6` | Owner reports direct development-to-production date correction; production source/version check and targeted Prepared Date PDF acceptance completed | Bypassed staging; targeted acceptance, not full report regression |
| Purchase `.2` | Historical `.0`: 10 tests passed and short/multipage PO review; retained 19 September staging update records PO/RFQ template loading and normal shutdown; supplied source pins match `.2`; owner-reported final release acceptance recorded 8 October | Final `.2` 13-test execution result and individual PO/RFQ visual/email-preview checklist records not located; staging loading is not a test pass |
| Intrastat `.28` | Accepted 12 September development record: 63 runtime tests passed, zero failures/errors; CSS and supplied wide/narrow dark-theme layout checks accepted | Demo-company acceptance; migrated-company/combined-business acceptance and final portal filing result not located |
| Tax Rules `.8` | 29 September development record: exact 86-method combined selection passed, zero failures/errors; focused staging source/version/view check recorded; owner reported dragging worked and appeared to persist after Save | Refresh, print, salesperson and locked/read-only checks not explicitly confirmed; earlier broad accounting comparison timed out |
| POHODA `.46` + reference `.0` | 27 September record: 86 selected tests passed, zero failures/errors; repeated successfully with Tax `.8` on 29 September; retained staging review reports 19 focused positive-DPI XML checks passed | Desktop import and actual posting waived by owner, assumed working rather than verified; final-settlement import remains unverified |

The 86-method selection comprises 47 Tax Rules, 15 reference, 17 native
down-payment and 7 POHODA release-resource methods. It is not the entire POHODA
suite. Its documented static inventory of 883 methods is not an execution
result. The companion's four standalone parser tests are separate from its
15 native Odoo methods. The recovered 29 September capture contains all 86 distinct expected method
starts and the final zero-failure/error result. The earlier 27 September tail
contains 85 starts plus the final 86-test aggregate. Nineteen translation-context
warnings were retained; they do not change the passing test result and are not
a claim of complete localized-message acceptance.

These are missing records, not instructions to repeat completed Odoo 19 work.
Current live settings and all-app database state were not re-read for this
documentation task. Existing private evidence stays private.

## Archived Customs and Odoo 20 handover

`barani_customs_documents` remains `16.0.0.2.0-alpha.3`, `installable=False`,
according to the owner's manifest inventory at the same addons pin. Its source
was not part of the four-app documentation export. It is excluded from the
eight installed apps; no acceptance or Odoo 19 compatibility is claimed.
Customs development resumes only after the Odoo 20 upgrade.

Preserve all existing P20 work and evidence. Use these exact source pins for
comparison; do not replace P20 work wholesale or assume Odoo 19 tests establish
Odoo 20 compatibility. The Prepared Date behavior, purchase RFQ selector,
native down-payment repair, reference safeguards and sales-line ordering fix
are explicit migration inputs. This closeout changes documentation/publication
only: no logic, module versions, production gitlinks or database state.
