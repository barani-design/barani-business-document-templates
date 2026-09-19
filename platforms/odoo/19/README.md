# Odoo 19 business-document templates

Commercial and business-document source belongs in this repository. Maintain Odoo
19 addons under `platforms/odoo/19/addons/`.

## Purchase Order and RFQ candidate

| Item | Value |
|---|---|
| Module | `barani_purchase` |
| Version | `19.0.1.0.1` |
| Source | [`addons/barani_purchase/`](addons/barani_purchase/) |
| Dependency | `purchase_stock` |
| Status | PO baseline passed 10 Odoo tests and staging PDF review; RFQ extension needs runtime/PDF validation |
| License | LGPL-3, as declared by the module manifest |

The PO layout follows the accepted BARANI invoice style: logo/title header,
structured company address, supplier and delivery blocks, ten invoice-style
columns, Odoo tax totals, payment terms, Incoterms, prepared-by and page numbers.
Unit prices retain Odoo Product Price precision, including prices such as 0.0119.

The existing Purchase Order and Request for Quotation actions use separate QWeb
reports with the same BARANI branding. RFQs remain unpriced: description, expected
date, quantity and unit only. The PO's ten-column financial table is unchanged.
Both original action configurations are saved for controlled uninstall. A
pre-upgrade script saves the RFQ action when upgrading an existing 19.0.1.0.0
installation, without replacing its existing PO backup.

Report rendering does not change orders or send email. Odoo's native Print RFQ
button still marks a draft RFQ as sent. Only supplier-facing standard terms are
printed; internal notes and the retired Studio datetime fields are not used.

The module and its attributed legacy background image are LGPL-3; the root draft
MIT license does not replace the module's declared license.

## Deployment

The source repository is `barani-design/barani-business-document-templates`.
Do not copy the maintained source into the POHODA/Intrastat/import application
repository. Check the Odoo.sh parent project's existing submodules and addon-path
configuration before wiring this source into a staging branch. That deployment
wiring is not changed by this source patch.

After the module is available to staging, update the Apps List and explicitly
install BARANI Purchase Order Documents. For an existing 19.0.1.0.0 installation,
upgrade this module to 19.0.1.0.1. Use the existing Print RFQ and Purchase Order
actions. Test the email attachments without sending them.

## Validation still required

Thirteen ORM/QWeb/PDF tests are supplied under `addons/barani_purchase/tests/`, tagged
`barani_purchase_reports`. Run them on a development/test database, never on
production. They cover action titles, filenames, price precision, discounts,
included/excluded taxes, global rounding, addresses, sections/notes, company
selection, language, the company header, short/multipage PO and RFQ PDFs,
native Print RFQ routing, unpriced RFQ content, upgrade backups and uninstall.

Review the generated PDFs visually for repeated table headings, numeric column
widths, header/body separation and the totals/prepared-by closing block.
Static checks do not establish runtime or visual acceptance.

## Other document families

This module covers PO and RFQ layouts only. It does not republish the existing Odoo 19
invoice, quotation/order, pro-forma, delivery or picking modules, and does not alter
the accepted Odoo 16 snapshots. Synchronizing those Odoo 19 sources into this
repository is a separate source-maintenance task.
