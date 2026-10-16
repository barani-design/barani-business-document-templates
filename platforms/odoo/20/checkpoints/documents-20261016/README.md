# BARANI v20 document source candidates — 16 October 2026

This branch adds three separate Odoo 20 source candidates, version `20.0.1.0.0`:
Commercial (quotation/order/pro-forma), Delivery (delivery/picking/sale-order bridge),
and VAT (invoices/advances/credit notes/preview). They start from the exact production-
linked addon commit `3d0b241d0b35d7619b87bdf4b0a57238150a0df8`, not an old download.
The parent source graph is recorded; it is not a fresh live-database inventory.

Purchase `20.0.1.0.3` remains byte-for-byte in the parent commit and is not a new
port, rebuild or replay. Its Runtime-01 remains HOLD. This branch preserves the
Purchase checkpoint ancestry; it does not merge the newer main branch's Odoo 19
catalog. No parent gitlink or Odoo.sh build is updated by publication.

## Actual port work

- Delivery stock move and move-line units use native v20 `uom_id`. Sale/invoice
  line `product_uom_id` stays as defined by those separate native models.
- Scrap exclusion uses native `is_scrap`. Picked/completed quantities, conversion
  without extra rounding, cancellation and entire-package behavior are retained.
- Prepared Date still uses `date_done` only, blank if absent. Scheduled Date is
  not used as its fallback. Picking Operations keeps its separate scheduled date.
- Registration rows use stored `additional_identifiers` classified as `EN` by
  native metadata, with native labels. No VAT derivation, enrichment, backfill or
  data write occurs during registration rendering. VAT's direct-contact/parent
  precedence is retained through an explicit fallback.
- Native v20 removed `layout_background` and `layout_background_image`. These
  candidates use a plain background, as the frozen Purchase candidate does.
  The attributed LGPL background asset remains byte-identical and unused.
- Seller Tax ID/EORI values formerly derived from VAT are no longer inferred.
  VAT itself remains displayed. The exact identifier data and any separately
  required Tax ID/EORI presentation require review before release. Arbitrary
  free-form company header content is retained, not rewritten by this port.
- Report actions, menu bindings, filenames, metadata collision checks, invoice
  attachment behavior, legacy Preview retirement, bank matching, EXW fallback,
  tax arithmetic and existing business policies remain as in the source baseline.

## What the verification proves

Python/XML/expression parsing, selected pinned native field/method/action/view
contracts, asset identity and bounded source-level fixtures passed locally.
Critical Ruff is unavailable in the controller environment (127); the Mac kit
uses the already pinned owner binary before creating a commit. It downloads
nothing and does not repeat Purchase's accepted offline suite.

Actual Odoo tests are included, adapted and extended. They have NOT run on v20.
New tests cover stored/blank/fallback/escaped identifiers, Prepared Date, scrap
and cancellation. PDF helpers require a real PDF, A4 geometry, and both a known
header and footer on every page. Existing business, attachment, multi-company,
serial/lot, package, advance and credit-note cases remain. Background tests are
explicitly replaced by the native20 plain-background contract; this is not a
claim that the removed native configuration has been migrated.

See RUNTIME_TEST_INVENTORY.json for source definitions, including the distinct
fullset classes. Do not count definitions or inherited cases as passes.
The VAT legacy Preview tests must also be selected; a generic `barani_reports`
tag alone does not include all original tests. The fullset cases require native
sale_mrp/HS/origin and Enterprise Intrastat owners; missing prerequisites are HOLD,
not skipped acceptance. No exact-target runnable runtime launcher is issued here.

## Release gates

1. Mac critical lint and local source commit; review the exact diff and candidate
   appearance/data choices above. Git publication is a candidate checkpoint only.
2. Complete target dependency/auto-install planning and exact database/resource
   scope. Preserve all consumed Purchase probes and attempt guards.
3. Fresh synthetic native installs and all applicable real ORM/QWeb/PDF tests,
   under the normal platform renderer wrapper with patched Qt; no direct binary
   bypass or HTML/mock acceptance. Test isolated and combined report modules.
4. Visual review of short and multipage documents for all document families,
   source-company/header/identifier accuracy, taxes/totals, languages and routing.
5. Revalidate against the actual supported production v20 native/Enterprise pins,
   then complete the separately deferred real-data upgrade rehearsal, identifier
   reconciliation, workflow acceptance and rollback/cutover checks.

No static source package makes the entire migration ready for deployment.
