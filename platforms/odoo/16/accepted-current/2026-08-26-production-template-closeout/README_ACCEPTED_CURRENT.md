# BARANI production template closeout — accepted current

Accepted on production Odoo 16 on 26 August 2026. The independent final verifier classified the complete report state as `TARGET` and finished with `PASS`; its checks were read-only.

This milestone is the migration baseline for future Odoo versions. It preserves all eleven accepted QWeb views, all eleven report-action filename policies, four paper formats, and the final stock Print-menu contract.

## Accepted behavior

- Invoice and credit-note layouts always show the shipping block when a shipping partner exists, including when billing and shipping resolve to the same partner.
- Commercial, VAT, Delivery Note, and Picking Operations address columns use a 10 mm left gutter.
- Delivery Note L2.2 always shows shipping, uses the envelope-window information row, and handles a unique source order, Incoterms, and sale-less pickings.
- Download filenames are numeric-first and use document-specific suffixes.
- The custom Delivery Note and Picking Operations actions use the translated labels of the corresponding standard Odoo actions.
- The stock Print menu contains Packages, Delivery Slip, and Picking Operations; duplicate standard Delivery Slip and Picking Operations bindings are hidden.
- Invoice Preview continues to resolve through the BARANI VAT HTML route.

## Contents

- `qweb/` — the eleven production-accepted `en_US` QWeb strings.
- `metadata/qweb_target.json` — logical view identities and exact production target hashes.
- `metadata/report_actions_target.json` — the report-action, filename, label, route, and Print-menu contract without tenant record IDs.
- `metadata/paperformats.json` — the four accepted A4 paper formats.
- `PROVENANCE.md` — deterministic reconstruction sources and the seven authorized transformations.
- `VALIDATION_SUMMARY.md` — sanitized verification and manual acceptance coverage.
- `CONTENT_PUBLICATION_NOTICE.md` — publication and exclusion boundary.
- `validate_snapshot.py` — offline integrity, XML, metadata, and canonical-source checks.

The XML files have one terminal line feed for normal repository handling. The `plain_md5`, `plain_sha256`, character length, and `storage_md5` values in `qweb_target.json` are calculated from the Odoo `arch_db` string without that publication line feed.

## Canonical reusable sources

The maintained portable sources are under `../../templates/`. They match this accepted behavior but replace the reviewed business payment/location constants with documented placeholders. The validator proves that the only allowed differences are those substitutions.

## Safety boundary

This snapshot is not an installer. It intentionally excludes production-bound Server Actions, database identity, numeric tenant record IDs, restore payloads, backup evidence, execution transcripts, and customer PDFs. Never run an Odoo 16 Server Action on a later Odoo version; port by logical XMLID/route and revalidate on that version.
