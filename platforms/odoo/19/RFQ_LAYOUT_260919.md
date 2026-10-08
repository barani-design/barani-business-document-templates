# BARANI Purchase Order and RFQ source closeout

## Published source

`barani_purchase` **19.0.1.0.2** is copied unchanged from
[`66d67448c94db3313365b2cc93d3336791d864e7`](https://github.com/barani-design/barani-business-document-templates/tree/66d67448c94db3313365b2cc93d3336791d864e7/platforms/odoo/19/addons/barani_purchase).
The source manifest is authoritative. This record reconciles the older
[19 September note](https://github.com/barani-design/barani-business-document-templates/blob/66d67448c94db3313365b2cc93d3336791d864e7/platforms/odoo/19/RFQ_LAYOUT_260919.md),
which still described `.1` as a candidate.

## Behavior and release history

Native `purchase.action_report_purchase_order` prints the priced PO;
`purchase.report_purchase_quotation` prints the unpriced RFQ. Version `.0`
changed only the PO route. Version `.1` added the RFQ header, structured
company address, supplier/delivery blocks, footer and paper format. Its RFQ
shows description, expected date, quantity and unit (including alternate-unit
quantity), sections/subsections, public notes and the native portal/EDI link.

Version `.2` corrects the RFQ inheritance selector to
`//div[hasclass('barani_po_closing')]`. Relative to `.1`, the correction changes
that selector and the manifest version. The PO template remains unchanged.
The PO uses product-price precision and native document tax totals; the RFQ
does not expose PO prices or amounts. Reports force `en_US` and use the order's
company. Rendering is read-only; Odoo's native Print RFQ button may mark a draft
request as sent as part of its normal workflow.

## Existing acceptance and missing evidence

Historical `.0` evidence recorded 10 development tests, zero failures/errors,
and staging review of one- and two-page PO PDFs. Those results cover `.0`,
not the later RFQ extension or selector correction.

The `.2` source includes 13 test methods covering native routing/filenames,
precision/totals, taxes, addresses, sections/notes, company/language context,
short and multipage PO/RFQ PDFs, and action backup/restore protection.
The owner supplied a read-only staging capture on 8 October. The parent pins
the templates repository to the exact `.2` source above, and its checked-out
templates HEAD matches that pin. The retained update excerpt dated 19 September
records loading both PO and RFQ XML, completion of module loading and normal
shutdown. This establishes staging-load evidence; it is not a test-suite result
or a visual acceptance record. The excerpt is filtered, so it does not establish
that the complete log contains no errors. Database module state was not queried
in this capture.

On 8 October 2026, the owner recalled accepting the final Odoo 19 staging
versions before they went live, except the Delivery `.6` date correction, which
went directly from development to production. This supplies owner-reported
release acceptance, including Purchase in this closeout. It does not reconstruct
which individual PDF/email-preview cases were checked or their dates.

The final `.2` 13-test execution result and individual PO/RFQ visual/email-preview
checklist records were not located. Those record limits do not revoke the owner's
release acceptance, establish a test failure or require repeating deployment or
testing. Existing customer PDFs and runtime logs are not republished.

## Installation and reuse

Dependency: `purchase_stock`. Fresh installation backs up both native report
actions. The included `.1` pre-upgrade migration protects the RFQ action when
upgrading from `.0`; uninstall restores each action only while its BARANI route
is still active. Foreign routes, cached attachments and duplicate backups are
rejected before takeover. Native action identities and email bindings remain.

See the [current catalog](README.md) for configuration, branding, license scope
and report overrides. Publication copies the module only; it does not merge
the older branch or change a production gitlink/database. Odoo 16, existing
P20 work and the three previously published report modules are preserved.
