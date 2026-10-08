# Odoo 19 report addons

Four report addons are published here. Commercial, Delivery and VAT retain the
production snapshot published on 7 October 2026. Purchase is copied byte for
byte from its separate PO/RFQ source. Publication does not install an app or
change a database. See the [eight-app index](APP_INDEX.md) for the other BARANI
apps, existing documentation and evidence gaps.

| Module | Version | Documents | Direct dependency |
|---|---|---|---|
| `barani_commercial` | `19.0.1.0.2` | Quotations, sales orders, pro-formas | `sale_stock` |
| `barani_delivery` | `19.0.1.0.6` | Delivery Notes, Picking Operations | `sale_stock` |
| `barani_vat` | `19.0.1.0.3` | Regular/down-payment invoices, credit notes | `sale_stock` |
| `barani_purchase` | `19.0.1.0.2` | Priced Purchase Orders, unpriced RFQs | `purchase_stock` |

## Source identity

- Commercial, Delivery and VAT: private addons commit
  [`3d0b241d0b35d7619b87bdf4b0a57238150a0df8`](https://github.com/barani-design/barani-odoo-addons/tree/3d0b241d0b35d7619b87bdf4b0a57238150a0df8), from each module's root directory.
  Public source baseline: [`c69910a0769887c5592cd0202615ba8a96eeb0ec`](https://github.com/barani-design/barani-business-document-templates/tree/c69910a0769887c5592cd0202615ba8a96eeb0ec/platforms/odoo/19/addons).
- Recorded production parent: `a9cdaae5aeffac68f6b1fd70734fd29936e41ba8`.
- Purchase: [`66d67448c94db3313365b2cc93d3336791d864e7`](https://github.com/barani-design/barani-business-document-templates/tree/66d67448c94db3313365b2cc93d3336791d864e7/platforms/odoo/19/addons/barani_purchase),
  path `platforms/odoo/19/addons/barani_purchase/`, tree
  `0102b7ac172bc880225e2646d6b0691677b4b2a8`.
- Only the 12 Purchase module files are copied from that older source. The old
  branch's other modules, catalog and history are not merged.

## Prepared Date correction

Delivery Note `19.0.1.0.6` labels the date cell **Prepared Date** and uses
`stock.picking.date_done` (Effective Date). It stays blank when that field is
empty. Existing Odoo date/time formatting and the technical cell name
`barani_dn_scheduled_date_cell` are retained. The correction changed only the
Delivery Note XML and manifest; Picking Operations, Commercial and VAT were
unchanged.

The owner clarified on 8 October that this date-field correction went directly
from development to production, bypassing staging. It is the exception to the
owner's recalled acceptance of final staging versions before their promotion.

## Verification scope

The owner supplied a successful production build for the recorded parent.
The production source identities and installed Delivery version were checked;
a newly rendered Delivery Note showed the expected Effective Date and a clean
one-page layout. This completed check is not a full report regression run.

The public baseline passed [snapshot validation](https://github.com/barani-design/barani-business-document-templates/actions/runs/37615782838).
That workflow checks repository snapshots, hashes and source parsing, not Odoo
runtime behavior. Existing report tests are included; they were not rerun for
this documentation closeout. Source inventories do not establish test passes.

Purchase's historical PO acceptance applies to `19.0.1.0.0`. A recovered
19 September staging update excerpt records loading both PO and RFQ templates,
completion of module loading and normal shutdown; supplied staging source pins
match the `.2` source above. On 8 October, the owner recalled accepting the final
Odoo 19 staging versions before they went live, with the direct development-to-
production Delivery `.6` date correction as the exception. This is retrospective
owner-reported release acceptance. The `.2` 13-test execution result and individual
PO/RFQ visual/email-preview checklist records were not located. See
[PO/RFQ history and limits](RFQ_LAYOUT_260919.md). Installed status and source
publication must not be presented as complete acceptance.

## Installation requirements and report overrides

For reuse, make this directory's `addons/` available on the Odoo **19** addons
path, provide the dependencies above, update the Apps list and explicitly
install the required modules in the target environment. These report addons
have `application=False`; remove the Apps-only filter when necessary. Provide
Odoo's working PDF renderer and configure the document company, addresses,
logo, footer, colors, taxes, fiscal positions and relevant bank account.
Review conflicting report customizations before installation.

| Addon | Native report actions affected |
|---|---|
| Commercial | `sale.action_report_saleorder`, `sale.action_report_pro_forma_invoice` |
| Delivery | `stock.action_report_delivery`, `stock.action_report_picking` |
| VAT | `account.account_invoices`, `account.account_invoices_without_payment` |
| Purchase | `purchase.action_report_purchase_order`, `purchase.report_purchase_quotation` |

These modules own report routes, paper formats and filenames. Commercial and
VAT also set action access/binding and attachment metadata. Delivery unbinds
the native stock Print entries and uses its own bound actions; the native
actions still route to the BARANI templates. VAT supplies Invoice Preview and
handles identified legacy preview views. Inspect each module's `data/` and
metadata code when combining customizations.

Purchase preserves native action IDs and email bindings. Its hooks back up the
original routes, filenames and paper formats, reject foreign routes/cached
attachments/duplicate backups, and restore only routes it still owns on
uninstall. The included pre-upgrade migration backs up the RFQ action when
upgrading from `.0`. This backup behavior is specific to Purchase, not a
general promise for the other addons.

Never replay Odoo 16 Server Actions on Odoo 19 or 20. Target-version installation
and acceptance remain the adopting site's responsibility; this closeout does
not repeat BARANI's completed deployment or testing.

## Publication notice and reuse

These are exact BARANI source snapshots, not fully generic templates. They
retain the following company-specific choices:

- Company logo, address, footer and primary/secondary colors come from Odoo
  company configuration, alongside fixed/fallback BARANI styling such as
  `#ed1c24` and the `#E79C9C` payment/receipt bands.
- Commercial and VAT contain receiving-bank matching constants:
  `SK1483300000002401465895` (IBAN) and `FIOZSKBAXXX` (BIC). Changing only a
  company's bank record does not generalize that selection logic.
- Commercial and VAT use `Brectanova 2353/1, 83101 Bratislava, SVK` as their
  EXW location fallback. Document titles, order/PF payment-reference parsing,
  `Q/`, `SO/`, `PF/` and `BA/OUT/` filename conventions also reflect BARANI.
- Purchase forces `en_US` report language and uses the order's company context;
  confirm that language and the supplied delivery/terms layout suit reuse.

Review these choices in a separately controlled customization before use by
another company. The immutable baseline itself is preserved. No customer PDFs,
database exports, credentials or private runtime logs accompany this closeout.
Private documentation links require repository access and do not publish the
linked contents or change repository visibility.

## License scope

The repository's root [LICENSE](../../../LICENSE) contains MIT terms. Each of
the four addon manifests declares `LGPL-3`; those declarations are unchanged.
Retain existing file-level copyright and attribution notices. The bundled
background image is attributed in the layout source to Odoo S.A., LGPL-3,
with its upstream source identity. Root MIT wording does not replace these
module declarations or asset notices. This closeout grants no new branding
rights and makes no license change.

## Other version work

Odoo 16 and Odoo 20 directories and all existing P20 work/evidence remain
unchanged. This Odoo 19 index is a versioned migration reference, not an Odoo 20
compatibility claim. Customs remains archived and uninstallable; its
development resumes only after the Odoo 20 upgrade.
