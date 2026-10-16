# BARANI v20: constant order payment reference

Owner decision: Jan, 16 October 2026, in the active Purchase/v20 controller chat.

The current order-reference implementation is correct. Bank payments commonly
arrive before an accounting invoice exists. Accountants need the pro-forma and
the same SO-derived numeric reference to match those payments later.

| Document | Document number | Payment reference |
| --- | --- | --- |
| Pro-forma | `PF/126/00017` | `12600017` |
| Later invoice for that order | `INV/926/00042` | `12600017` |

The invoice keeps its own legal number. The payment reference remains constant
for the same order. This owner decision supersedes the separate invoice-family
payment-reference requirement in the older
`BARANI_Numbering_and_Payment_Reference_Policy.pdf` on this point. The historical
PDF remains preserved; its old reference rule must not be reintroduced by a port.

## Source successor

Base: published document candidate `5e13c2b592a3d47a37f432a94b7cb89001ac363e`,
tree `46de1359970461ef288639c7e29054b661ab8fff` in
`barani-design/barani-business-document-templates`.

This successor changes only the v20 VAT report module and this checkpoint note.
VAT becomes `20.0.1.0.1`; Purchase remains frozen at `20.0.1.0.3`.

- Invoice payment-reference fields display the exact saved native
  `payment_reference`, preserving leading zeroes and native text references.
- When either protected order-reference marker is present, report rendering
  invokes the existing companion validator. Invalid snapshots stop rendering;
  the report never repairs or changes accounting data.
- Origin text and invoice numbers are not payment-reference fallbacks. Multiple
  origins can never become one concatenated, invented reference. An unmarked
  draft without a saved reference has no payment-reference field.
- Customer credit notes retain their existing suppression of a new payment
  request. Their **Original Payment Reference** comes only from the actual linked
  original invoice. A textual **Original Invoice** label remains unchanged.
- Paid invoices retain their reference for matching. Payment identity does not
  depend on whether a balance is still outstanding.

The existing optional Payment Reference module still owns assignment and
protection. Its company option is not enabled or disabled here. Existing
unmarked/manual invoices are not retroactively adopted. Managed RI/DPI/settlement
exports already use the same saved reference; unmarked DPI exports retain their
existing configurable reference/origin/blank policy. Universal PDF/export equality
for those unmarked DPI records is not claimed by this source correction.

There is no change to SO/PF commercial templates, Delivery, Purchase, Tax Rules
.10, POHODA, Payment Reference assignment, invoice numbering, company settings,
financial arithmetic, payments, reconciliation, historical records or migration.
The present bank-band layout and paid/DPI balance presentation also remain
unchanged; the older PDF alone is not authority to remove a constant reference.

## Verification and acceptance

The included focused offline tests exercise the actual new method bodies and
the actual two QWeb expressions with record stand-ins. They cover preserved
references, combined origins, missing/native values, marker validation and error
propagation, paid-state identity, linked/unlinked credit references and QWeb
escaping directives. They do not import Odoo or establish ORM/QWeb runtime safety.

Five new native rendering tests and a paid-DPI assertion are included for the
future authorized runtime. Existing native test identities are retained. Native
tests and rendered PDF acceptance remain NOT_RUN. Ruff runs on the owner's
existing hash-pinned Mac binary during the new one-shot preparation.

Runtime-01 remains **HOLD_RUNTIME01**. Application acceptance remains
**HOLD_NATIVE_RUNTIME_AND_PDF**. The kit does not retry any original or R2 runtime
launcher and does not erase any consumed attempt guard.

## One-shot owner action

Source checkout:
`/Users/janbarani/Documents/GitHub/barani-p20-documents-preparation-r1`

New checkout:
`/Users/janbarani/Documents/GitHub/barani-p20-reference-documents-r1`

New branch: `p20-reference-documents-20261016-r1`.

The new command checks the exact kit and source identities, runs only focused
reference tests and scoped Ruff, and imports the fixed successor commit into the
new checkout using local Git objects. It records before/after source metadata,
command results and a checksummed evidence archive. No downloads, network Git,
publication, parent gitlink update, Odoo.sh action or database operation occur.

Return the generated evidence ZIP and checksum sidecar. Publication then uses
GitHub Desktop on the exact new branch; this is a source checkpoint, not a
production release.
