# ============================================================================
# ACTION NAME : BARANI VAT REPORT TUNE L22 — customer/shipping email + invoice/SO note fallback
#               (on L21 base; RI keeps payment ref; production label)
#
# L21 CHANGE (cosmetic only):
#   1. Remove the duplicate centered document title in the header.
#   2. Keep the right-side document type + number label only, e.g. Invoice: INV-EXAMPLE.
#   3. No VAT math, totals, tax, fiscal-position, bank, payment-reference,
#      product, account, POHODA, or invoice data changes.
#
# L22 CHANGES (display-only):
#   1. Show Customer Email below Customer Tel when partner email exists.
#   2. Show Shipping Address Email below Shipping Tel when shipping partner email exists.
#   3. Explain/fix missing notes: keep invoice Terms/Notes from account.move.narration;
#      if it is empty, fall back to the linked Sale Order note from native sale_line_ids.order_id.note.
#   4. No VAT math, totals, tax, fiscal-position, bank, payment-reference, product,
#      account, POHODA, or invoice data changes.
#
# L20 CHANGE (cosmetic only):
#   1. Align the company tax-registration block (ID / Tax ID / VAT / EORI)
#      with the customer Shipping Address column by adding the same 18px
#      left gutter used by the body shipping-address cell.
#   2. No VAT math, totals, tax, fiscal-position, bank, payment-reference,
#      product, account, POHODA, or invoice data changes.
#
# L16a CHANGES (micro-patch only):
#   1. Add EORI under VAT in the company registration header, sourced from company.vat.
#   2. Keep Description at 32%, widen Unit/UoM from 5.5% to 7%, narrow VAT Rate from 7% to 5%.
#   3. Preserve all L15.2 totals, notes, bank band, QR omission, payment-reference rules, and Signature baseline.
#
# L16b2 CHANGES (safe layout only):
#   1. Add fiscal-position name + fiscal-position legal note in a left cell beside the totals table.
#   2. Use display:table / display:table-cell, not Bootstrap row/flex, so wkhtmltopdf keeps the totals table.
#   3. Keep totals cell always rendered; only note content is conditional.
#
# L16c CHANGES (micro-patch only):
#   1. Always show an INCOTERMS line in the same left notes cell.
#   2. Source from standard Odoo account.move.invoice_incoterm_id; no DDS/Studio field.
#   3. No totals, line, bank, payment-reference, or signature changes.
#
# L16d CHANGES (micro-patch only):
#   1. Replace the blank Signature label with Prepared by / Issued by.
#   2. Source the name from native Odoo fields: o.invoice_user_id.name, fallback o.create_uid.name.
#   3. Keep the same lower-right location and do not alter totals/notes/table/bank layout.
#
# L16e.1 CHANGES (combined remaining small items):
#   1. Add credit-note Original Invoice / Reference using native reversed_entry_id/ref.
#   2. Add INTRASTAT transport code line in the existing display-table notes cell when known.
#   3. Add template TODO comments for future Tax Point/VAT Date and customer tax-status classification.
#   4. Final visual cleanup: COO column -0.5%, VAT Rate +0.5%, discount header becomes Disc., and discount cells show the percent sign next to the number.
#
# L16f CHANGES (final cleanup):
#   1. Incoterms render as CODE (Full name), avoiding CODE (CODE).
#   2. Bank address is rendered as one clean comma-joined string.
#   3. Intrastat transport line is rendered only once.
#   4. Customer credit notes hide top Due Date, suppress bottom payment/bank band, and label the total as Amount credited.
#
# L16g.3 CHANGES (reconciled with Q/SO/PF-2026v1 production pattern):
#   1. Use the same proven address-row wrapping pattern as Q/SO/PF-2026v1:
#      .barani_addr_block .col-6 { min-width:0; box-sizing:border-box; word-wrap/overflow-wrap }
#      plus 18px inner gutters. This covers BOTH customer and shipping columns.
#   2. Use the confirmed receiving company bank as a non-arbitrary fallback when invoice Recipient Bank is blank/missing.
#      This keeps the same IBAN/SWIFT/Bank band visible on RI/DPI, aligned with Q/SO/PF.
#   3. Always render INCOTERMS; if the standard Odoo field is blank, show "Not specified".
#   4. Rename/keep the account.move Print-menu label VAT Invoices RI/DPI - 2026+ to match the commercial Q/SO/PF 2026+ naming style.
#
# L16h.1 CHANGES (micro-patch only):
#   1. Show customer phone/mobile below the billing address with a Tel: prefix when available.
#   2. Show shipping-address phone/mobile below the shipping address with a Tel: prefix when available.
#   3. On final RI/settlement invoices with down-payment deductions, print a short
#      Down payment reconciliation note inside the red bank-transfer band, explaining
#      that the deduction carries negative VAT base and negative VAT, so down payment VAT is not charged twice.
#
# L17 CHANGES:
#   1. Add an RI-only Down payment reconciliation table directly below the invoice-line table.
#   2. The table shows goods/services, each advance deduction, and net invoice totals in three numeric columns: Base excl. VAT, VAT, Total incl. VAT.
#   3. Down payment deductions are displayed as Odoo posts them: negative base, negative VAT, and negative gross total. The product/HS/COO line table remains goods-only; no accounting/tax data is changed.
#
# L18 CHANGES:
#   1. Reconciles the two L17.1 address-fix variants into one canonical installer.
#   2. Uses the more precise conditional-gutter approach: Customer has no left indent and no right gutter when alone; Customer gets 18px right gutter only when Shipping Address exists; Shipping gets 18px left gutter.
#   3. Retains the L17 down-payment base/VAT reconciliation table and L16h.1 Tel prefix behavior.
#
# L19 CHANGES:
#   1. Rename the RI section to Down payment reconciliation and use down-payment terminology consistently.
#   2. Remove duplicate gross Less: Down Payment / Total Advances rows from the right totals table when the detailed base/VAT reconciliation table is present.
#   3. Settlement RI right-side totals now show Odoo official net invoice totals; the reconciliation table shows supply before down payments and negative down-payment base/VAT/total rows.
#   4. Remove the red-band reconciliation explanation so the bank band stays payment-only.
#
# L12 CHANGES (cumulative on L11.1):
#   A. Settlement totals collapsed to 6 rows: Subtotal (excl. VAT) / Total VAT / Total incl. VAT / Less: <DP invoices> / Total
#      Advances Received / Balance Due; the three official net rows removed.
#   B. Currency line added below Balance Due (and on CASE B invoices).
#   C. Down payment invoices: "Total excl. VAT" relabelled "Subtotal (excl. VAT)";
#      Balance Due row removed; Payment Reference shows the Source/order ref
#      (invoice_origin, e.g. SO-EXAMPLE) instead of the DPI's own number.
#      Detection via native barani_is_dp_invoice (positive 324 lines, no 324
#      deduction). DISPLAY-ONLY: no stored payment_reference field is modified.
#   D. Header spacing: tighten the band above the customer block, add a little
#      space below it before the date/reference row.
#
# L13 CHANGES (visual polish only; still isolated):
#   1. Draw the title/logo divider as an absolute overlay so the logo cannot hide it.
#   2. Add a second thin divider between seller header info and customer/buyer info.
#   3. Remove the stock web.address_layout spacer inside the custom layout.
#   4. Add controlled space between the date/reference row and the VAT table.
#   5. Move the Signature label left by padding it 25% from the right edge.
#
# L14 CHANGES (visual-only on L13 base):
#   1. Improve top divider/logo interaction: the thin header divider is drawn above the logo layer.
#   2. Reduce remaining vertical whitespace slightly between header/company block and buyer/body block.
#   3. Shift the Signature label another small step left.
#   4. Render Unit Price with currency symbol using Odoo's monetary widget.
#   5. Raise and compact the wkhtmltopdf footer by increasing the VAT paperformat
#      bottom margin and tightening footer line-height, preventing clipped page numbers.
#
# L16a CHANGES (micro-patch only):
#   1. Add EORI under VAT in the company registration header, sourced from company.vat.
#   2. Keep Description at 32%, widen Unit/UoM from 5.5% to 7%, narrow VAT Rate from 7% to 5%.
#   3. Preserve all L15.2 totals, notes, bank band, QR omission, payment-reference rules, and Signature baseline.
# MODEL       : Module (ir.module.module) or any model; selected records ignored.
# ACTION TO DO: Execute Python Code
# RUN BY      : Run APPLY=False first; then APPLY=True + CONFIRM='INSTALL_VAT_LAYOUT'.
# PURPOSE     : Updates only the isolated "Invoices VAT — Barani" report family.
#               Creates/updates four BARANI-owned technical artifacts:
#                 - standalone VAT QWeb view
#                 - account.move report action
#                 - dedicated VAT paperformat
#                 - custom external layout view with logo + title header
#               Existing live buttons 234/236/842/900 and title overrides are untouched.
#
# L11 CHANGES (cumulative on L10):
#   1. DEDUCTION LABEL (DDS bypass): each "Less:" line now derives its label from
#      NATIVE Odoo fields, not the DDS line.name string ("Advanced Invoice:").
#      For a deduction line we walk sale_line_ids -> (is_downpayment) ->
#      invoice_lines -> source account.move and print that move's real .name and
#      a type-correct prefix. Falls back to "Advance payment" if no native source.
#   2. HEADER COMPANY IDs: company ID (ICO=company_registry), Tax ID (DIC, derived
#      by stripping a leading 'SK' from company.vat), and VAT (IC DPH=company.vat)
#      are rendered in the header company block, mirroring the legacy invoice.
#   3. OFFICIAL-FIGURE TOTALS: on settlement invoices the totals block anchors to
#      Odoo's official o.amount_untaxed / o.amount_tax / o.amount_total so the
#      chain ties exactly (no goods-gross-minus-flat-advances 2c divergence).
#      The advance "Less:" lines are shown as the bridge; Balance Due = residual.
#   4. LAYOUT: company/customer header block tightened (no large empty band).
#   5. PADDING: right-side cell padding on totals + footer bands.
#   6. VISIBILITY: report bound to Billing + Sales/Administrator (if resolvable).
#
# SAFE_EVAL   : no import/def/lambda/comprehension/with/getattr/hasattr/setattr/
#               eval/exec/open/dir/isinstance in THIS script. Lambdas are inside
#               QWeb arch strings and evaluated by report rendering.
# ============================================================================

APPLY = False
CONFIRM = ''

VAT_VIEW_KEY = 'barani_vat.report_invoice_document_vat'
VAT_VIEW_NAME = 'BARANI VAT report_invoice_document (commercial/VAT layout) v02'
VAT_REPORT_NAME = 'VAT Invoices RI/DPI - 2026+'
PAPERFORMAT_NAME = 'BARANI VAT A4 7mm'

ACTION_NAME = 'BARANI VAT REPORT TUNE L22 — customer/shipping email + invoice/SO note fallback (RI keeps payment ref)'
OUTPUT_PARAMETER_KEY = 'barani.vat_report.install.last_run'
IDS_PARAMETER_KEY = 'barani.vat_report.ids'
LAYOUT_VIEW_KEY = 'barani_vat.external_layout_standard_titled'
LAYOUT_VIEW_NAME = 'BARANI VAT external_layout_standard_titled (logo + title header)'
ARCH_BACKUP_KEY = 'barani.vat_report.pre_l_arch_backup'
ARCH_BACKUP_MARKER_KEY = 'barani.vat_report.pre_l_arch_backup.marker'
LAYOUT_BACKUP_KEY = 'barani.vat_report.pre_l4_layout_arch_backup'
LAYOUT_BACKUP_MARKER_KEY = 'barani.vat_report.pre_l4_layout_arch_backup.marker'
GROUP_XMLID = 'account.group_account_invoice'
SALES_GROUP_XMLID = 'sales_team.group_sale_manager'
# L14.1: the custom external footer has multiple lines; 7mm bottom margin clipped
# page numbers/footer text in wkhtmltopdf. 18mm lifts the footer without using
# the full 32mm company default bottom margin.
VAT_BOTTOM_MARGIN = 18.0
# L15: confirmed receiving account for customer payments. Do not fall back to
# another company bank account because the company has more than one bank account.
RECEIVING_IBAN = 'XX00 0000 0000 0000 0000 0000'
RECEIVING_IBAN_COMPACT = 'XX0000000000000000000000'
RECEIVING_BIC = 'YOURBICXXX'

PRINT_REPORT_NAME_EXPR = "('Credit Note' if object.move_type == 'out_refund' else 'Vendor Credit Note' if object.move_type == 'in_refund' else 'Vendor Bill' if object.move_type == 'in_invoice' else 'Draft Invoice' if object.state == 'draft' else 'Cancelled Invoice' if object.state == 'cancel' else 'Invoice') + ((' ' + object.name) if object.name and object.name != '/' else '')"

LAYOUT_ARCH = '<t t-name="barani_vat.external_layout_standard_titled">\n        <t t-if="not o" t-set="o" t-value="doc"/>\n        <t t-if="not company">\n            <t t-if="company_id">\n                <t t-set="company" t-value="company_id"/>\n            </t>\n            <t t-elif="o and \'company_id\' in o and o.company_id.sudo()">\n                <t t-set="company" t-value="o.company_id.sudo()"/>\n            </t>\n            <t t-else="else">\n                <t t-set="company" t-value="res_company"/>\n            </t>\n        </t>\n        <div t-attf-class="header o_company_#{company.id}_layout" t-att-style="report_header_style">\n            <div style="position:relative; height:41px;">\n                <t t-if="o and o._name == \'account.move\'">\n                    <t t-set="bvt_dp" t-value="o.invoice_line_ids.filtered(lambda l: l.display_type not in (\'line_section\',\'line_note\') and l.account_id and l.account_id.code and l.account_id.code[:3] == \'324\' and (l.price_subtotal or 0.0) &gt;= -0.005)"/>\n                    <t t-set="bvt_ded" t-value="o.invoice_line_ids.filtered(lambda l: l.display_type not in (\'line_section\',\'line_note\') and l.account_id and l.account_id.code and l.account_id.code[:3] == \'324\' and (l.price_subtotal or 0.0) &lt; -0.005)"/>\n                    <t t-set="bvt_goods" t-value="o.invoice_line_ids.filtered(lambda l: l.display_type not in (\'line_section\',\'line_note\') and not (l.account_id and l.account_id.code and l.account_id.code[:3] == \'324\'))"/>\n                    <t t-set="bvt_dp_only" t-value="bvt_dp and not bvt_goods and not bvt_ded"/>\n                    <t t-set="bvt_type_label" t-value="(\'Down Payment Invoice\' if (o.move_type == \'out_invoice\' and o.state == \'posted\' and bvt_dp_only) else \'Invoice\' if (o.move_type == \'out_invoice\' and o.state == \'posted\' and not bvt_dp_only) else \'Draft Down Payment Invoice\' if (o.move_type == \'out_invoice\' and o.state == \'draft\' and bvt_dp_only) else \'Draft Invoice\' if (o.move_type == \'out_invoice\' and o.state == \'draft\' and not bvt_dp_only) else \'Cancelled Down Payment Invoice\' if (o.move_type == \'out_invoice\' and o.state == \'cancel\' and bvt_dp_only) else \'Cancelled Invoice\' if (o.move_type == \'out_invoice\' and o.state == \'cancel\' and not bvt_dp_only) else \'Credit Note\' if o.move_type == \'out_refund\' else \'Vendor Credit Note\' if o.move_type == \'in_refund\' else \'Vendor Bill\' if o.move_type == \'in_invoice\' else \'Document\')"/>\n                </t>\n                <div style="float:left; width:35%; height:41px; line-height:41px; position:relative; z-index:10;">\n                    <img t-if="company.logo" t-att-src="image_data_uri(company.logo)" style="max-height: 41px; vertical-align:middle;" alt="Logo"/>\n                </div>\n                <div t-if="o and o._name == \'account.move\' and o.name != \'/\'" style="position:absolute; right:0; top:0; height:41px; line-height:41px; text-align:right; max-width:45%; z-index:15;">\n                    <span style="font-size:13pt; font-weight:bold; white-space:nowrap; vertical-align:middle;"><t t-esc="bvt_type_label"/>: <span t-field="o.name"/></span>\n                </div>\n                <div name="barani_top_title_divider" style="position:absolute; left:0; right:0; bottom:0; border-bottom:1px solid black; z-index:40;"/>\n                <div style="clear:both;"/>\n            </div>\n            <div class="row" style="margin-top:2px;">\n                <div class="col-6" name="company_address" style="font-size:10pt; line-height:1.25;">\n                    <ul class="list-unstyled" style="margin-bottom:2px;">\n                        <li t-if="company.is_company_details_empty"><t t-esc="company.partner_id" t-options=\'{"widget": "contact", "fields": ["address", "name"], "no_marker": true}\'/></li>\n                        <li t-else=""><t t-esc="company.company_details"/></li>\n                        <li t-if="forced_vat">\n                            <t t-esc="company.country_id.vat_label or \'Tax ID\'"/>:\n                            <span t-esc="forced_vat"/>\n                        </li>\n                    </ul>\n                </div>\n                <div class="col-6" name="company_registration" style="font-size:10pt; line-height:1.25; padding-left:18px; box-sizing:border-box;">\n                    <ul class="list-unstyled" style="margin-bottom:2px;">\n                        <li t-if="company.company_registry">ID: <span t-esc="company.company_registry"/></li>\n                        <li t-if="company.vat">Tax ID: <span t-esc="company.vat[2:] if (company.vat[:2] == \'SK\') else company.vat"/></li>\n                        <li t-if="company.vat">VAT: <span t-esc="company.vat"/></li>\n                        <li t-if="company.vat">EORI: <span t-esc="company.vat"/></li>\n                    </ul>\n                </div>\n            </div>\n            <div name="barani_seller_buyer_divider" style="border-bottom:1px solid black; width:100%; margin:1px 0 0 0;"/>\n        </div>\n\n        <div t-attf-class="article o_report_layout_standard o_company_#{company.id}_layout {{  \'o_report_layout_background\' if company.layout_background in [\'Geometric\', \'Custom\']  else  \'\' }}" t-attf-style="background-image: url({{ \'data:image/png;base64,%s\' % company.layout_background_image.decode(\'utf-8\') if company.layout_background_image and company.layout_background == \'Custom\' else \'/base/static/img/bg_background_template.jpg\' if company.layout_background == \'Geometric\' else \'\'}});" t-att-data-oe-model="o and o._name" t-att-data-oe-id="o and o.id" t-att-data-oe-lang="o and o.env.context.get(\'lang\')">\n            <!-- BARANI VAT: address block is rendered in the report body; suppress the stock address spacer. -->\n            <t t-out="0"/>\n        </div>\n\n        <div t-attf-class="footer o_standard_footer o_company_#{company.id}_layout">\n            <div class="text-center" style="border-top: 1px solid black; font-size:8pt; line-height:1.1; padding-top:2px;">\n                <ul class="list-inline" style="margin:0 0 1px 0; padding:0;">\n                    <div t-field="company.report_footer"/>\n                </ul>\n\n                <div t-if="report_type == \'pdf\'" class="text-muted">\n                    <span class="page"/> of <span class="topage"/>\n                </div>\n                <div t-if="report_type == \'pdf\' and display_name_in_footer" class="text-muted">\n                    <span t-field="o.name"/>\n                </div>\n            </div>\n        </div>\n    </t>'

VAT_ARCH = '<t t-name="barani_vat.report_invoice_document_vat">\n  <t t-call="web.html_container">\n    <t t-foreach="docs" t-as="o">\n      <t t-set="lang" t-value="(o.invoice_user_id.sudo().lang if o.move_type in (\'in_invoice\',\'in_refund\') else o.partner_id.lang) or user.lang"/>\n      <t t-call="barani_vat.external_layout_standard_titled" t-lang="lang">\n        <t t-set="o" t-value="o.with_context(lang=lang)"/>\n        <t t-set="forced_vat" t-value="o.fiscal_position_id.foreign_vat"/>\n        <!-- L16 TODO 2A: VAT Date currently uses o.invoice_date as a stopgap; replace with the confirmed Slovak tax-point/supply-date field when available. -->\n        <!-- L16 TODO 6: Customer VAT/status classification should be data-driven from fiscal position / partner VAT / country; do not infer legal status in QWeb alone. -->\n\n        <!-- Scoped layout for the dense 10-column VAT table. Targets only .barani_vat_table; no other report affected. table-layout:fixed + per-column widths prevent right-margin clipping; description wraps, numerics stay on one line. -->\n        <style>\n          /* Unified 10pt body and table. Keep explicit sizes for wkhtmltopdf. */\n          .barani_vat_doc { font-size: 10pt; line-height: 1.25; } .barani_addr_block { margin-top: -1px; margin-bottom: 0; } .barani_addr_block .barani_addr_cell { min-width: 0; box-sizing: border-box; word-wrap: break-word; overflow-wrap: break-word; } .barani_addr_block .barani_customer_cell { padding-left: 0; padding-right: 0; } .barani_addr_block .barani_customer_cell.barani_has_shipping { padding-right: 18px; } .barani_addr_block .barani_shipping_cell { padding-left: 18px; padding-right: 0; } .barani_info_block { padding-top: 4px; margin-bottom:8px; }\n          .barani_vat_table { table-layout: fixed; width: 100%; font-size: 10pt; line-height: 1.2; }\n          .barani_vat_table th, .barani_vat_table td { padding: 2px 3px; vertical-align: top; overflow: hidden; }\n          .barani_vat_table .text-nowrap { white-space: nowrap; }\n          /* L11: right-side breathing room on totals + footer band cells */\n          #total table.table-sm td.text-end { padding-right: 10px; }\n          .barani_footer_band { padding-right: 10px; }\n          .barani_down_payment_reconciliation_table { table-layout: fixed; width:100%; font-size:9pt; line-height:1.15; margin:6px 0 6px 0; }\n          .barani_down_payment_reconciliation_table th, .barani_down_payment_reconciliation_table td { padding:2px 4px; vertical-align:top; }\n        </style>\n\n        <!-- Fork A, DDS-free split. Positive 324 lines are down-payment invoice lines; negative 324 lines are settlement deductions. -->\n        <t t-set="barani_dp_lines" t-value="o.invoice_line_ids.filtered(lambda l: l.display_type not in (\'line_section\',\'line_note\') and l.account_id and l.account_id.code and l.account_id.code[:3] == \'324\' and (l.price_subtotal or 0.0) &gt;= -0.005)"/>\n        <t t-set="barani_ded_lines" t-value="o.invoice_line_ids.filtered(lambda l: l.display_type not in (\'line_section\',\'line_note\') and l.account_id and l.account_id.code and l.account_id.code[:3] == \'324\' and (l.price_subtotal or 0.0) &lt; -0.005)"/>\n        <t t-set="barani_goods_lines" t-value="o.invoice_line_ids.filtered(lambda l: l.display_type not in (\'line_section\',\'line_note\') and not (l.account_id and l.account_id.code and l.account_id.code[:3] == \'324\'))"/>\n        <t t-set="barani_is_dp_only" t-value="barani_dp_lines and not barani_goods_lines and not barani_ded_lines"/>\n        <t t-set="barani_table_lines" t-value="barani_dp_lines if barani_is_dp_only else barani_goods_lines"/>\n        <t t-set="barani_total_base" t-value="sum(barani_table_lines.mapped(\'price_subtotal\'))"/>\n        <t t-set="barani_total_gross" t-value="sum(barani_table_lines.mapped(\'price_total\'))"/>\n        <t t-set="barani_total_vat" t-value="barani_total_gross - barani_total_base"/>\n        <t t-set="barani_advance_applied" t-value="-sum(barani_ded_lines.mapped(\'price_total\'))"/>\n        <t t-set="barani_has_advance_deduction" t-value="bool(barani_ded_lines)"/>\n        <t t-set="barani_dp_pos_lines" t-value="o.invoice_line_ids.filtered(lambda l: l.display_type not in (\'line_section\',\'line_note\') and l.account_id and l.account_id.code and l.account_id.code[:3] == \'324\' and (l.price_subtotal or 0.0) &gt; 0.005)"/>\n        <t t-set="barani_is_dp_invoice" t-value="bool(barani_dp_pos_lines) and not barani_goods_lines and not barani_has_advance_deduction"/>\n        <!-- Official-display totals: use Odoo document totals when there is no 324 deduction, to preserve tax-rounding exactly; use goods-only totals on 324 settlement invoices. -->\n        <t t-set="barani_line_vat_sum" t-value="barani_total_vat"/>\n        <t t-set="barani_official_goods_total" t-value="(o.amount_total + barani_advance_applied) if barani_has_advance_deduction else o.amount_total"/>\n        <t t-set="barani_official_goods_vat" t-value="barani_official_goods_total - barani_total_base"/>\n        <t t-set="barani_goods_gross" t-value="barani_official_goods_total"/>\n        <t t-set="barani_display_base" t-value="o.amount_untaxed"/>\n        <t t-set="barani_display_vat" t-value="o.amount_tax"/>\n        <t t-set="barani_display_total" t-value="o.amount_total"/>\n        <t t-set="display_discount" t-value="any(l.discount for l in barani_table_lines)"/>\n\n        <div class="row barani_vat_doc barani_addr_block">\n          <div t-att-class="&quot;col-6 barani_addr_cell barani_customer_cell barani_has_shipping&quot; if (o.partner_shipping_id and (o.partner_shipping_id != o.partner_id)) else &quot;col-6 barani_addr_cell barani_customer_cell&quot;">\n            <t t-if="o.move_type in (\'out_invoice\', \'out_refund\')"><strong>Customer</strong></t>\n            <t t-if="o.move_type in (\'in_invoice\', \'in_refund\')"><strong>Vendor</strong></t>\n            <div t-field="o.partner_id" t-options=\'{"widget": "contact", "fields": ["address", "name"], "no_marker": true}\'/>\n            <div t-if="o.partner_id.phone or o.partner_id.mobile" name="barani_customer_phone" class="mt-1"><span>Tel: </span><span t-esc="o.partner_id.phone or o.partner_id.mobile"/></div>\n            <div t-if="o.partner_id.email" name="barani_customer_email" class="mt-1"><span>Email: </span><span t-field="o.partner_id.email"/></div>\n            <div t-if="o.partner_id.company_registry" class="mt-1">ID: <span t-field="o.partner_id.company_registry"/></div>\n            <div t-if="o.partner_id.vat" class="mt-1">\n              <t t-if="o.company_id.account_fiscal_country_id.vat_label" t-esc="o.company_id.account_fiscal_country_id.vat_label"/>\n              <t t-else="">Tax ID</t>: <span t-field="o.partner_id.vat"/>\n            </div>\n          </div>\n          <div class="col-6 barani_addr_cell barani_shipping_cell" t-if="o.partner_shipping_id and (o.partner_shipping_id != o.partner_id)">\n            <strong>Shipping Address</strong>\n            <div t-field="o.partner_shipping_id" t-options=\'{"widget": "contact", "fields": ["address", "name"], "no_marker": true}\'/>\n            <div t-if="o.partner_shipping_id.phone or o.partner_shipping_id.mobile" name="barani_shipping_phone" class="mt-1"><span>Tel: </span><span t-esc="o.partner_shipping_id.phone or o.partner_shipping_id.mobile"/></div>\n            <div t-if="o.partner_shipping_id.email" name="barani_shipping_email" class="mt-1"><span>Email: </span><span t-field="o.partner_shipping_id.email"/></div>\n          </div>\n        </div>\n\n        <div class="page barani_vat_doc">\n          <div id="informations" class="row mt-3 barani_info_block">\n            <div class="col-2 mb-2" t-if="o.invoice_date" name="invoice_date">\n              <t t-if="o.move_type == \'out_invoice\'"><strong>Invoice Date</strong></t>\n              <t t-elif="o.move_type == \'out_refund\'"><strong>Credit Note Date</strong></t>\n              <t t-else=""><strong>Date</strong></t>\n              <p class="m-0" t-field="o.invoice_date"/>\n            </div>\n            <div class="col-2 mb-2" t-if="o.invoice_date and o.move_type in (\'out_invoice\',\'out_refund\')" name="vat_date">\n              <strong>VAT Date</strong><p class="m-0" t-field="o.invoice_date"/>\n            </div>\n            <div class="col-2 mb-2" t-if="o.invoice_date_due and o.move_type == \'out_invoice\' and o.state == \'posted\'" name="due_date">\n              <strong>Due Date</strong><p class="m-0" t-field="o.invoice_date_due"/>\n            </div>\n            <div class="col-2 mb-2" t-if="o.invoice_origin" name="origin">\n              <strong>Source</strong><p class="m-0" t-field="o.invoice_origin"/>\n            </div>\n            <div class="col-3 mb-2" name="barani_credit_origin_reference_wide" t-if="o.move_type in (\'out_refund\',\'in_refund\') and (o.reversed_entry_id or o.ref)">\n              <strong>Original Invoice / Reference</strong><p class="m-0"><span t-esc="(o.reversed_entry_id.name if o.reversed_entry_id else \'\') or (o.ref or \'\')"/></p>\n            </div>\n            <div class="col-2 mb-2" t-if="o.ref and o.move_type not in (\'out_refund\',\'in_refund\')" name="reference">\n              <strong>Reference</strong><p class="m-0" t-field="o.ref"/>\n            </div>\n            <div class="col-2 mb-2" t-if="((barani_is_dp_invoice and o.invoice_origin) or ((not barani_is_dp_invoice) and o.payment_reference)) and o.move_type in (\'out_invoice\',\'in_refund\')" name="payment_reference">\n              <strong>Payment Reference</strong><p class="m-0"><span t-esc="o.invoice_origin if barani_is_dp_invoice else (o.payment_reference or \'\')"/></p>\n            </div>\n            <div class="col-2 mb-2" t-if="o.move_type == \'out_invoice\'" name="payment_method">\n              <strong>Payment Method</strong><p class="m-0">Wire transfer</p>\n            </div>\n          </div>\n\n          <table class="table table-sm o_main_table barani_vat_table" name="invoice_line_table">\n            <colgroup>\n              <col style="width:32%"/>\n              <col style="width:8%"/>\n              <col name="barani_coo_col_final" style="width:5%"/>\n              <col style="width:6.5%"/>\n              <col name="barani_unit_col_wide" style="width:7%"/>\n              <col style="width:8%"/>\n              <col t-if="display_discount" style="width:5.5%"/>\n              <col name="barani_vat_rate_col_final" style="width:5.5%"/>\n              <col style="width:7.5%"/>\n              <col style="width:10%"/>\n            </colgroup>\n            <thead>\n              <tr>\n                <th name="th_description" class="text-start"><span>Description</span></th>\n                <th name="th_hscode" class="text-start"><span>HS Code</span></th>\n                <th name="th_coo" class="text-center"><span>COO</span></th>\n                <th name="th_quantity" class="text-end"><span>Qty</span></th>\n                <th name="th_uom" class="text-start"><span>Unit</span></th>\n                <th name="th_priceunit" class="text-end"><span>Unit Price</span></th>\n                <th name="th_discount" t-if="display_discount" class="text-end"><span>Disc.</span></th>\n                <th name="th_vatrate" class="text-end"><span>VAT Rate</span></th>\n                <th name="th_vatamount" class="text-end"><span>VAT</span></th>\n                <th name="th_vatbase" class="text-end"><span>VAT Base</span></th>\n              </tr>\n            </thead>\n            <tbody class="invoice_tbody">\n              <t t-foreach="o.invoice_line_ids" t-as="line">\n                <t t-set="barani_line_is_real" t-value="line.display_type not in (\'line_section\',\'line_note\')"/>\n                <t t-set="barani_line_is_324" t-value="barani_line_is_real and line.account_id and line.account_id.code and line.account_id.code[:3] == \'324\'"/>\n                <t t-set="barani_line_in_table" t-value="barani_line_is_real and ((barani_is_dp_only and barani_line_is_324 and (line.price_subtotal or 0.0) &gt;= -0.005) or ((not barani_is_dp_only) and not barani_line_is_324))"/>\n\n                <tr t-if="barani_line_in_table">\n                  <td name="td_name"><span t-field="line.name" t-options=\'{"widget": "text"}\'/></td>\n                  <td name="td_hscode" class="text-start"><span t-if="line.product_id.hs_code" t-field="line.product_id.hs_code"/></td>\n                  <td name="td_coo" class="text-center"><span t-if="line.product_id.country_of_origin" t-field="line.product_id.country_of_origin.code"/></td>\n                  <td name="td_qty" class="text-end"><span t-field="line.quantity"/></td>\n                  <td name="td_unit" class="text-start"><span t-field="line.product_uom_id" groups="uom.group_uom"/></td>\n                  <td name="td_priceunit" class="text-end"><span class="text-nowrap" name="barani_unit_price_currency"><span t-field="line.price_unit" t-options=\'{"widget": "float", "precision": 2}\'/>&#160;<span t-esc="o.currency_id.symbol"/></span></td>\n                  <td name="td_discount" t-if="display_discount" class="text-end"><span class="text-nowrap" name="barani_discount_percent_cell"><span t-field="line.discount" t-options=\'{"widget": "float", "precision": 1}\'/>&#160;%</span></td>\n                  <td name="td_vatrate" class="text-end"><span class="text-nowrap" t-esc="\', \'.join(line.tax_ids.mapped(\'description\'))"/></td>\n                  <td name="td_vatamount" class="text-end"><span class="text-nowrap" t-esc="line.price_total - line.price_subtotal" t-options=\'{"widget": "monetary", "display_currency": o.currency_id}\'/></td>\n                  <td name="td_vatbase" class="text-end o_price_total"><span class="text-nowrap" t-field="line.price_subtotal"/></td>\n                </tr>\n\n                <tr t-if="line.display_type == \'line_section\' and line.name != \'Down Payments\'" class="bg-200 fw-bold o_line_section">\n                  <td t-att-colspan="\'10\' if display_discount else \'9\'"><span t-field="line.name" t-options=\'{"widget": "text"}\'/></td>\n                </tr>\n                <tr t-if="line.display_type == \'line_note\'" class="fst-italic o_line_note">\n                  <td t-att-colspan="\'10\' if display_discount else \'9\'"><span t-field="line.name" t-options=\'{"widget": "text"}\'/></td>\n                </tr>\n              </t>\n\n              <tr class="border-black o_total fw-bold">\n                <td class="text-end" t-att-colspan="\'7\' if display_discount else \'6\'"><span>Totals</span></td>\n                <td class="text-end"><span>VAT</span></td>\n                <td class="text-end"><span t-esc="barani_official_goods_vat" t-options=\'{"widget": "monetary", "display_currency": o.currency_id}\'/></td>\n                <td class="text-end"><span t-esc="barani_total_base" t-options=\'{"widget": "monetary", "display_currency": o.currency_id}\'/></td>\n              </tr>\n            </tbody>\n          </table>\n\n          <div name="barani_down_payment_reconciliation_table" t-if="barani_has_advance_deduction and o.move_type == \'out_invoice\'" style="margin:6px 0 6px 0;">\n            <table class="table table-sm barani_down_payment_reconciliation_table">\n              <colgroup>\n                <col style="width:49%"/>\n                <col style="width:17%"/>\n                <col style="width:17%"/>\n                <col style="width:17%"/>\n              </colgroup>\n              <thead>\n                <tr>\n                  <th class="text-start">Down payment reconciliation</th>\n                  <th class="text-end">Base excl. VAT</th>\n                  <th class="text-end">VAT</th>\n                  <th class="text-end">Total incl. VAT</th>\n                </tr>\n              </thead>\n              <tbody>\n                <tr>\n                  <td>Goods/services before down payments</td>\n                  <td class="text-end"><span t-esc="barani_total_base" t-options=\'{"widget": "monetary", "display_currency": o.currency_id}\'/></td>\n                  <td class="text-end"><span t-esc="barani_official_goods_vat" t-options=\'{"widget": "monetary", "display_currency": o.currency_id}\'/></td>\n                  <td class="text-end"><span t-esc="barani_goods_gross" t-options=\'{"widget": "monetary", "display_currency": o.currency_id}\'/></td>\n                </tr>\n                <t t-foreach="barani_ded_lines" t-as="bvt_rec_dl">\n                  <t t-set="bvt_rec_src" t-value="bvt_rec_dl.sale_line_ids.invoice_lines.move_id.filtered(lambda m: m.id != o.id and m.move_type == \'out_invoice\' and m.state == \'posted\')"/>\n                  <t t-set="bvt_rec_is_dp" t-value="any(s.is_downpayment for s in bvt_rec_dl.sale_line_ids)"/>\n                  <t t-set="bvt_rec_label" t-value="(\'Down Payment Invoice \' + bvt_rec_src[0].name) if (bvt_rec_is_dp and bvt_rec_src and bvt_rec_src[0].name and bvt_rec_src[0].name != \'/\') else \'Down payment deduction\'"/>\n                  <tr>\n                    <td>Less: <t t-esc="bvt_rec_label"/></td>\n                    <td class="text-end"><span t-esc="bvt_rec_dl.price_subtotal or 0.0" t-options=\'{"widget": "monetary", "display_currency": o.currency_id}\'/></td>\n                    <td class="text-end"><span t-esc="(bvt_rec_dl.price_total or 0.0) - (bvt_rec_dl.price_subtotal or 0.0)" t-options=\'{"widget": "monetary", "display_currency": o.currency_id}\'/></td>\n                    <td class="text-end"><span t-esc="bvt_rec_dl.price_total or 0.0" t-options=\'{"widget": "monetary", "display_currency": o.currency_id}\'/></td>\n                  </tr>\n                </t>\n                <tr class="border-black fw-bold">\n                  <td><strong>Invoice total after down payments</strong></td>\n                  <td class="text-end"><strong><span t-esc="o.amount_untaxed" t-options=\'{"widget": "monetary", "display_currency": o.currency_id}\'/></strong></td>\n                  <td class="text-end"><strong><span t-esc="o.amount_tax" t-options=\'{"widget": "monetary", "display_currency": o.currency_id}\'/></strong></td>\n                  <td class="text-end"><strong><span t-esc="o.amount_total" t-options=\'{"widget": "monetary", "display_currency": o.currency_id}\'/></strong></td>\n                </tr>\n              </tbody>\n            </table>\n          </div>\n\n          <div name="barani_notes_totals_table" style="display:table; width:100%; table-layout:fixed; margin-top:3px;">\n            <div name="barani_notes_cell" style="display:table-cell; width:57%; vertical-align:top; font-size:10pt; line-height:1.25; padding:0 12px 0 0;">\n              <p t-if="(barani_line_vat_sum - barani_official_goods_vat) &gt; 0.005 or (barani_official_goods_vat - barani_line_vat_sum) &gt; 0.005" class="text-muted" style="font-size:10pt; margin:0 0 6px 0;">VAT is rounded globally; the VAT total follows Odoo\'s official tax rounding. Sum of displayed line VAT amounts: <span t-esc="barani_line_vat_sum" t-options=\'{"widget": "monetary", "display_currency": o.currency_id}\'/>.</p>\n              <t t-set="barani_incoterm_code" t-value="o.invoice_incoterm_id.code or \'\' if o.invoice_incoterm_id else \'\'"/>\n              <t t-set="barani_incoterm_name" t-value="o.invoice_incoterm_id.name or \'\' if o.invoice_incoterm_id else \'\'"/>\n              <t t-set="barani_incoterm_display" t-value="barani_incoterm_code + ((\' (\' + barani_incoterm_name + \')\') if (barani_incoterm_name and barani_incoterm_name != barani_incoterm_code) else \'\')"/>\n              <div name="barani_incoterms_line" style="margin:0 0 4px 0; font-size:10pt; line-height:1.25;">\n                <strong>INCOTERMS:</strong> <span name="barani_incoterms_code_name" t-esc="barani_incoterm_display if o.invoice_incoterm_id else \'Not specified\'"/>\n              </div>\n              <div t-if="o.fiscal_position_id" name="barani_fiscal_position_note" style="margin:0 0 4px 0; font-size:10pt; line-height:1.25;">\n                <strong>Fiscal position:</strong> <span t-field="o.fiscal_position_id.name"/>\n              </div>\n              <div t-if="not is_html_empty(o.fiscal_position_id.note)" name="barani_fiscal_position_note_text" style="margin:0 0 4px 0; font-size:10pt; line-height:1.25;">\n                <span t-field="o.fiscal_position_id.note"/>\n              </div>\n              <div t-if="o.intrastat_transport_mode_id" name="barani_intrastat_transport_code" style="margin:0 0 4px 0; font-size:10pt; line-height:1.25;">\n                <strong>INTRASTAT transport code:</strong> <span t-esc="o.intrastat_transport_mode_id.display_name"/>\n              </div>\n            </div>\n            <div id="total" name="barani_totals_cell" style="display:table-cell; width:43%; vertical-align:top;">\n                <table class="table table-sm">\n                                    <t t-if="barani_has_advance_deduction and o.move_type in (\'out_invoice\',\'out_refund\')">\n                  <tr>\n                    <td>Subtotal after down payments (excl. VAT)</td>\n                    <td class="text-end"><span t-esc="o.amount_untaxed" t-options=\'{"widget": "monetary", "display_currency": o.currency_id}\'/></td>\n                  </tr>\n                  <tr>\n                    <td>VAT after down payments</td>\n                    <td class="text-end"><span t-esc="o.amount_tax" t-options=\'{"widget": "monetary", "display_currency": o.currency_id}\'/></td>\n                  </tr>\n                  <tr class="border-black fw-bold" name="barani_invoice_total_after_down_payments">\n                    <td><strong>Invoice total after down payments</strong></td>\n                    <td class="text-end"><strong><span t-esc="o.amount_total" t-options=\'{"widget": "monetary", "display_currency": o.currency_id}\'/></strong></td>\n                  </tr>\n                  <tr class="border-black fw-bold">\n                    <td><strong><t t-esc="\'Amount credited\' if o.move_type == \'out_refund\' else \'Balance Due\'"/></strong></td>\n                    <td class="text-end"><strong><span t-esc="o.amount_total if o.move_type == \'out_refund\' else o.amount_residual" t-options=\'{"widget": "monetary", "display_currency": o.currency_id}\'/></strong></td>\n                  </tr>\n                  <tr>\n                    <td>Currency</td>\n                    <td class="text-end"><span t-esc="o.currency_id.name or \'EUR\'"/></td>\n                  </tr>\n                  </t>\n                  <t t-if="not barani_has_advance_deduction">\n                  <tr>\n                    <td><t t-esc="\'Subtotal (excl. VAT)\' if barani_is_dp_invoice else \'Total excl. VAT\'"/></td>\n                    <td class="text-end"><span t-esc="o.amount_untaxed" t-options=\'{"widget": "monetary", "display_currency": o.currency_id}\'/></td>\n                  </tr>\n                  <tr>\n                    <td>Total VAT</td>\n                    <td class="text-end"><span t-esc="o.amount_tax" t-options=\'{"widget": "monetary", "display_currency": o.currency_id}\'/></td>\n                  </tr>\n                  <tr class="border-black">\n                    <td><strong>Total incl. VAT</strong></td>\n                    <td class="text-end"><strong><span t-esc="o.amount_total" t-options=\'{"widget": "monetary", "display_currency": o.currency_id}\'/></strong></td>\n                  </tr>\n                    <t t-if="(not barani_is_dp_invoice) and o.move_type == \'out_invoice\' and o.state == \'posted\'">\n                  <tr class="border-black fw-bold">\n                    <td><strong>Balance Due</strong></td>\n                    <td class="text-end"><strong><span t-field="o.amount_residual"/></strong></td>\n                  </tr>\n                    </t>\n                    <t t-if="o.move_type == \'out_refund\' and o.state == \'posted\'">\n                  <tr class="border-black fw-bold">\n                    <td><strong>Amount credited</strong></td>\n                    <td class="text-end"><strong><span t-esc="o.amount_total" t-options=\'{"widget": "monetary", "display_currency": o.currency_id}\'/></strong></td>\n                  </tr>\n                    </t>\n                  <tr>\n                    <td>Currency</td>\n                    <td class="text-end"><span t-esc="o.currency_id.name or \'EUR\'"/></td>\n                  </tr>\n                  </t>\n                </table>\n            </div>\n          </div>\n\n          <t t-set="barani_note_source_orders" t-value="o.invoice_line_ids.sale_line_ids.order_id"/>\n          <t t-set="barani_note_source_order" t-value="barani_note_source_orders[0] if barani_note_source_orders else False"/>\n          <div t-if="not is_html_empty(o.narration)" name="comment"><span t-field="o.narration"/></div>\n          <div t-if="is_html_empty(o.narration) and barani_note_source_order and not is_html_empty(barani_note_source_order.note)" name="barani_sale_order_note_fallback"><span t-field="barani_note_source_order.note"/></div>\n\n          <p class="text-muted" style="font-size:8pt; margin-top:6px;">COO = Country of Origin</p>\n\n          <t t-set="barani_pdf_payment_ref" t-value="\'\' if o.move_type == \'out_refund\' else (o.invoice_origin if barani_is_dp_invoice else (o.payment_reference or \'\'))"/>\n          <t t-set="barani_bank_iban_compact" t-value="(o.partner_bank_id.acc_number or \'\').replace(\' \', \'\') if o.partner_bank_id else \'\'"/>\n          <t t-set="barani_bank_bic_compact" t-value="(o.partner_bank_id.bank_id.bic or \'\').replace(\' \', \'\') if (o.partner_bank_id and o.partner_bank_id.bank_id) else \'\'"/>\n          <t t-set="barani_invoice_bank_ok" t-value="o.partner_bank_id and barani_bank_iban_compact == \'XX0000000000000000000000\' and barani_bank_bic_compact == \'YOURBICXXX\'"/>\n          <t t-set="barani_company_receiving_banks" t-value="o.company_id.partner_id.bank_ids.filtered(lambda b: (b.acc_number or \'\').replace(\' \', \'\') == \'XX0000000000000000000000\' and b.bank_id and (b.bank_id.bic or \'\').replace(\' \', \'\') == \'YOURBICXXX\')"/>\n          <t t-set="barani_effective_bank" t-value="o.partner_bank_id if barani_invoice_bank_ok else (barani_company_receiving_banks[0] if barani_company_receiving_banks else False)"/>\n          <t t-set="barani_receiving_bank_ok" t-value="bool(barani_effective_bank)"/>\n          <t t-set="barani_bank_record" t-value="barani_effective_bank.bank_id if (barani_effective_bank and barani_effective_bank.bank_id) else False"/>\n          <t t-set="barani_bank_has_address" t-value="barani_bank_record and (barani_bank_record.street or barani_bank_record.city or barani_bank_record.country)"/>\n          <div name="barani_bank_transfer_band" t-if="o.move_type != \'out_refund\' and (barani_effective_bank or barani_pdf_payment_ref or o.invoice_date_due)" style="display:table; width:100%; table-layout:fixed; background-color:#E79C9C; font-size:9pt; line-height:1.2;">\n            <div name="barani_bank_details_cell" class="barani_footer_band" style="display:table-cell; width:75%; text-align:left; vertical-align:top; background-color:#E79C9C; padding:3px 6px;" t-if="barani_effective_bank">\n              <div><strong>Bank transfer:</strong></div>\n              <div><span>IBAN: </span><span t-field="barani_effective_bank.acc_number"/><span> | SWIFT/BIC: </span><span t-field="barani_effective_bank.bank_id.bic"/></div>\n              <div t-if="barani_bank_record and (barani_bank_record.name or barani_bank_has_address)">\n                <t t-if="barani_bank_record.name"><span>Bank: </span><span t-field="barani_bank_record.name"/></t>\n                <t t-if="barani_bank_record.name and barani_bank_has_address"><span> | </span></t>\n                <t t-if="barani_bank_has_address">\n                  <t t-set="barani_bank_city_line" t-value="(barani_bank_record.zip or \'\') + (\' \' if (barani_bank_record.zip and barani_bank_record.city) else \'\') + (barani_bank_record.city or \'\')"/>\n                  <t t-set="barani_bank_address_text" t-value="(barani_bank_record.street or \'\') + ((\', \' + barani_bank_city_line) if (barani_bank_city_line and barani_bank_record.street) else (barani_bank_city_line if barani_bank_city_line and not barani_bank_record.street else \'\')) + ((\', \' + barani_bank_record.country.name) if (barani_bank_record.country and ((barani_bank_record.street or \'\') or barani_bank_city_line)) else (barani_bank_record.country.name if barani_bank_record.country else \'\'))"/>\n                  <span>Bank address: </span><span name="barani_bank_address_clean" t-esc="barani_bank_address_text"/>\n                </t>\n              </div>\n            </div>\n            <div name="barani_payment_ref_cell" class="barani_footer_band" t-if="barani_pdf_payment_ref" t-att-style="\'display:table-cell; width:12.5%; text-align:right; vertical-align:top; background-color:#E79C9C; padding:3px 6px;\' if (barani_effective_bank and o.invoice_date_due) else \'display:table-cell; width:25%; text-align:right; vertical-align:top; background-color:#E79C9C; padding:3px 6px;\' if barani_effective_bank else \'display:table-cell; width:50%; text-align:right; vertical-align:top; background-color:#E79C9C; padding:3px 6px;\' if o.invoice_date_due else \'display:table-cell; width:100%; text-align:right; vertical-align:top; background-color:#E79C9C; padding:3px 6px;\'"><span><strong>Payment Ref.:</strong><br/></span><span t-esc="barani_pdf_payment_ref"/></div>\n            <div name="barani_due_date_cell" class="barani_footer_band" t-if="o.invoice_date_due" t-att-style="\'display:table-cell; width:12.5%; text-align:right; vertical-align:top; background-color:#E79C9C; padding:3px 6px;\' if (barani_effective_bank and barani_pdf_payment_ref) else \'display:table-cell; width:25%; text-align:right; vertical-align:top; background-color:#E79C9C; padding:3px 6px;\' if barani_effective_bank else \'display:table-cell; width:50%; text-align:right; vertical-align:top; background-color:#E79C9C; padding:3px 6px;\' if barani_pdf_payment_ref else \'display:table-cell; width:100%; text-align:right; vertical-align:top; background-color:#E79C9C; padding:3px 6px;\'"><span><strong>Due Date:</strong><br/></span><span t-field="o.invoice_date_due"/></div>\n          </div>\n\n          <t t-set="barani_issued_by" t-value="o.invoice_user_id.name if o.invoice_user_id else (o.create_uid.name if o.create_uid else \'\')"/>\n          <div class="row mt-4" name="barani_issued_by_slot"><div class="col-12 text-end" style="padding-right:33%; font-size:10pt;"><span><strong>Prepared by / Issued by:</strong> </span><span t-esc="barani_issued_by"/></div></div>\n\n          <!-- L15.2: payment QR intentionally omitted; bank transfer details use confirmed invoice recipient bank only. -->\n        </div>\n      </t>\n    </t>\n  </t>\n</t>'

View = env['ir.ui.view'].sudo()
Report = env['ir.actions.report'].sudo()
Model = env['ir.model'].sudo()
Param = env['ir.config_parameter'].sudo()
Paper = env['report.paperformat'].sudo()
Tax = env['account.tax'].sudo()
Field = env['ir.model.fields'].sudo()
Ref = env.ref

lines = []
lines.append(ACTION_NAME)
lines.append('APPLY=%s CONFIRM=%s' % (APPLY, CONFIRM))
lines.append('Scope: isolated VAT print option only; live buttons 234/236/842/900 untouched.')
lines.append('VAT arch length: %s chars | layout arch length: %s chars' % (len(VAT_ARCH), len(LAYOUT_ARCH)))
lines.append('')

# TEST 0 - savepoint and cache invalidation.
manual_sp_ok = False
cache_inv_method = ''
lines.append('TEST 0 - manual SQL savepoint recovery + ORM cache invalidation')
try:
    env.cr.execute('SAVEPOINT t0_ok')
    env.cr.execute('SELECT 1')
    env.cr.execute('RELEASE SAVEPOINT t0_ok')
    env.cr.execute('SAVEPOINT t0_fail')
    try:
        env.cr.execute('SELECT * FROM __barani_missing_table_for_rollback_probe__')
        env.cr.execute('RELEASE SAVEPOINT t0_fail')
    except Exception:
        env.cr.execute('ROLLBACK TO SAVEPOINT t0_fail')
        env.cr.execute('RELEASE SAVEPOINT t0_fail')
        try:
            env.invalidate_all()
            cache_inv_method = 'env.invalidate_all'
        except Exception:
            try:
                env.cache.invalidate()
                cache_inv_method = 'env.cache.invalidate'
            except Exception:
                cache_inv_method = ''
        if cache_inv_method:
            env.cr.execute('SELECT 1')
            manual_sp_ok = True
            lines.append('PASS: SAVEPOINT recovery works; cache method=%s' % cache_inv_method)
except Exception as e0:
    lines.append('FATAL TEST 0: %s' % str(e0)[:500])
if not manual_sp_ok:
    lines.append('STOP: savepoint/cache mechanism unusable.')
    raise UserError('\n'.join(lines)[:90000])
lines.append('')

# Template self-checks. These are string checks, not XML parsing.
lines.append('TEMPLATE SELF-CHECK')
self_error = False
checks = [
    ('docs wrapper', 't-foreach="docs"' in VAT_ARCH and 'web.html_container' in VAT_ARCH),
    ('VAT calls custom layout', 't-call="barani_vat.external_layout_standard_titled"' in VAT_ARCH),
    ('custom layout sets company', 't-if="not company"' in LAYOUT_ARCH and 'res_company' in LAYOUT_ARCH),
    ('right-side title label only', 'Down Payment Invoice' in LAYOUT_ARCH and 'barani_doc_title' not in LAYOUT_ARCH and 'bvt_type_label' in LAYOUT_ARCH and 't-field="o.name"' in LAYOUT_ARCH and 'dds_' not in LAYOUT_ARCH),
    ('company EORI from VAT', 'EORI:' in LAYOUT_ARCH and 'company.vat' in LAYOUT_ARCH),
    ('company registration aligned with shipping column', 'name="company_registration" style="font-size:10pt; line-height:1.25; padding-left:18px; box-sizing:border-box;"' in LAYOUT_ARCH),
    ('fiscal position note table layout', 'barani_notes_totals_table' in VAT_ARCH and 'barani_fiscal_position_note' in VAT_ARCH and 'barani_totals_cell' in VAT_ARCH and 'display:table-cell' in VAT_ARCH),
    ('incoterms always shown', 'barani_incoterms_line' in VAT_ARCH and 'invoice_incoterm_id' in VAT_ARCH and 'INCOTERMS:' in VAT_ARCH),
    ('old bootstrap totals row removed', 'id="total" class="row"' not in VAT_ARCH and 'col-5 ms-auto' not in VAT_ARCH),
    ('no sample placeholders', 'sample' not in VAT_ARCH),
    ('old full-width fiscal note removed', '<p t-if="not is_html_empty(o.fiscal_position_id.note)" name="note"' not in VAT_ARCH),
    ('in-body title removed', '<h2' not in VAT_ARCH and 'barani_doc_title' not in VAT_ARCH),
    ('user.lang fallback', 'or user.lang' in VAT_ARCH),
    ('table lines split', 'barani_table_lines' in VAT_ARCH),
    ('deduction-only settlement', 'barani_ded_lines' in VAT_ARCH and 'barani_has_advance_deduction' in VAT_ARCH),
    ('official total rounding guard', 'barani_display_base' in VAT_ARCH and 'barani_display_vat' in VAT_ARCH and 'barani_display_total' in VAT_ARCH and 'o.amount_untaxed' in VAT_ARCH and 'o.amount_tax' in VAT_ARCH and 'o.amount_total' in VAT_ARCH),
    ('official goods settlement bridge', 'barani_official_goods_total' in VAT_ARCH and 'barani_official_goods_vat' in VAT_ARCH and 'VAT is rounded globally' in VAT_ARCH),
    ('native deduction label', 'sale_line_ids.invoice_lines.move_id' in VAT_ARCH and 'is_downpayment' in VAT_ARCH and 'Advanced Invoice:' not in VAT_ARCH),
    ('no old adv-lines lumping', 'barani_adv_lines' not in VAT_ARCH),
    ('strict tax labels', "line.tax_ids.mapped('description')" in VAT_ARCH),
    ('no tax list comprehension', 'for t in line.tax_ids' not in VAT_ARCH),
    ('no stale display test', 'not line.display_type' not in VAT_ARCH),
    ('reference field preserved', 'name="reference"' in VAT_ARCH and 't-field="o.ref"' in VAT_ARCH),
    ('DPI detection excludes goods', 'bool(barani_dp_pos_lines) and not barani_goods_lines and not barani_has_advance_deduction' in VAT_ARCH),
    ('RI payment reference preserved', 'o.payment_reference' in VAT_ARCH),
    ('QR omitted entirely', 'o.display_qr_code' not in VAT_ARCH and '_generate_qr_code' not in VAT_ARCH),
    ('adaptive footer widths', 'barani_payment_ref_cell' in VAT_ARCH and 'barani_due_date_cell' in VAT_ARCH and 'width:12.5%' in VAT_ARCH),
    ('COO short header', '<span>COO</span>' in VAT_ARCH),
    ('no CSS custom properties', 'var(--' not in VAT_ARCH and '--barani-' not in VAT_ARCH),
    ('payment footer band widths', 'barani_bank_details_cell' in VAT_ARCH and 'display:table-cell' in VAT_ARCH and 'width:75%' in VAT_ARCH and 'width:12.5%' in VAT_ARCH),
    ('bank transfer band', 'barani_bank_transfer_band' in VAT_ARCH and 'Bank transfer:' in VAT_ARCH and 'SWIFT/BIC' in VAT_ARCH and 'IBAN:' in VAT_ARCH),
    ('bank name/address same-line renderers', 'Bank: ' in VAT_ARCH and 'Bank address:' in VAT_ARCH and 'barani_bank_has_address' in VAT_ARCH and '<span> | </span>' in VAT_ARCH),
    ('sanitized receiving bank guard', 'barani_receiving_bank_ok' in VAT_ARCH and RECEIVING_IBAN_COMPACT in VAT_ARCH and RECEIVING_BIC in VAT_ARCH and '.replace(' in VAT_ARCH),
    ('confirmed company receiving bank fallback', 'barani_company_receiving_banks' in VAT_ARCH and 'barani_effective_bank' in VAT_ARCH and 'partner_id.bank_ids[0]' not in VAT_ARCH),
    ('address wrap/padding no-single-column-indent (L18 canonical)', '.barani_addr_block .barani_addr_cell {' in VAT_ARCH and 'min-width: 0' in VAT_ARCH and 'overflow-wrap: break-word' in VAT_ARCH and 'barani_customer_cell.barani_has_shipping' in VAT_ARCH and 'padding-left: 0' in VAT_ARCH),
    ('shipping address wrap/padding explicit (L18 canonical)', '.barani_addr_block .barani_shipping_cell {' in VAT_ARCH and 'padding-left: 18px' in VAT_ARCH and 't-field="o.partner_shipping_id"' in VAT_ARCH),
    ('customer/shipping phone display with Tel prefix', 'name="barani_customer_phone"' in VAT_ARCH and 'name="barani_shipping_phone"' in VAT_ARCH and 'Tel: ' in VAT_ARCH),
    ('customer/shipping email display', 'name="barani_customer_email"' in VAT_ARCH and 'name="barani_shipping_email"' in VAT_ARCH and 'Email: ' in VAT_ARCH),
    ('invoice/SO note fallback', 'barani_sale_order_note_fallback' in VAT_ARCH and 'barani_note_source_orders' in VAT_ARCH and 'o.narration' in VAT_ARCH and 'sale_line_ids.order_id' in VAT_ARCH),
    ('down payment reconciliation table', 'barani_down_payment_reconciliation_table' in VAT_ARCH and 'Base excl. VAT' in VAT_ARCH and 'Invoice total after down payments' in VAT_ARCH and 'bvt_rec_dl.price_subtotal' in VAT_ARCH),
    ('no duplicate gross down-payment rows in totals', 'Total Advances Received' not in VAT_ARCH and 'bvt_dl.price_total' not in VAT_ARCH and 'barani_advance_vat_reconciliation_red_band_note' not in VAT_ARCH and 'flat gross discount' not in VAT_ARCH and 'barani_invoice_total_after_down_payments' in VAT_ARCH),
    ('incoterms Not specified when blank', 'name="barani_incoterms_line"' in VAT_ARCH and '<strong>INCOTERMS:</strong>' in VAT_ARCH and 'Not specified' in VAT_ARCH and 'barani_incoterm_display if o.invoice_incoterm_id else' in VAT_ARCH),
    ('production print label', VAT_REPORT_NAME == 'VAT Invoices RI/DPI - 2026+'),
    ('top divider overlay present', 'barani_top_title_divider' in LAYOUT_ARCH and 'z-index:40' in LAYOUT_ARCH),
    ('center header title removed', 'barani_doc_title' not in LAYOUT_ARCH),
    ('seller/buyer divider present', 'barani_seller_buyer_divider' in LAYOUT_ARCH and 'margin:1px 0 0 0' in LAYOUT_ARCH),
    ('stock address spacer removed', 'web.address_layout' not in LAYOUT_ARCH and 'suppress the stock address spacer' in LAYOUT_ARCH),
    ('info-to-table spacing present', 'margin-bottom:8px' in VAT_ARCH and 'mt-3 barani_info_block' in VAT_ARCH),
    ('issued by from Odoo user', 'barani_issued_by_slot' in VAT_ARCH and 'Prepared by / Issued by:' in VAT_ARCH and 'o.invoice_user_id.name' in VAT_ARCH and 'o.create_uid.name' in VAT_ARCH and 'Signature:' not in VAT_ARCH),
    ('future VAT date/customer-status comments', 'L16 TODO 2A' in VAT_ARCH and 'L16 TODO 6' in VAT_ARCH),
    ('credit-note original invoice reference', 'barani_credit_origin_reference' in VAT_ARCH and 'reversed_entry_id' in VAT_ARCH and 'Original Invoice / Reference' in VAT_ARCH),
    ('intrastat transport optional', 'barani_intrastat_transport_code' in VAT_ARCH and 'intrastat_transport_mode_id' in VAT_ARCH and 'INTRASTAT transport code' in VAT_ARCH),
    ('unit price shows currency', 'barani_unit_price_currency' in VAT_ARCH and 'o.currency_id.symbol' in VAT_ARCH),
    ('footer compacted', 'font-size:8pt' in LAYOUT_ARCH and 'line-height:1.1' in LAYOUT_ARCH),
    ('vat header shortened', 'th_vatamount' in VAT_ARCH and 'VAT Amount' not in VAT_ARCH),
    ('description column remains 32%', 'width:32%' in VAT_ARCH),
    ('unit column widened', 'barani_unit_col_wide' in VAT_ARCH and 'width:7%' in VAT_ARCH),
    ('COO/VAT Rate final widths', 'barani_coo_col_final' in VAT_ARCH and 'barani_vat_rate_col_final' in VAT_ARCH and 'width:5%' in VAT_ARCH and 'width:5.5%' in VAT_ARCH),
    ('discount percent in cell', '<span>Disc.</span>' in VAT_ARCH and 'barani_discount_percent_cell' in VAT_ARCH),
    ('incoterms code plus name', 'barani_incoterms_code_name' in VAT_ARCH and 'barani_incoterm_display' in VAT_ARCH),
    ('clean bank address renderer', ('barani_bank_address_joined' in VAT_ARCH or 'barani_bank_address_clean' in VAT_ARCH) and 'barani_bank_address_text' in VAT_ARCH),
    ('single intrastat renderer', VAT_ARCH.count('name="barani_intrastat_transport_code"') == 1),
    ('credit note payment suppression', ("o.move_type not in ('out_refund','in_refund') and (barani_effective_bank" in VAT_ARCH or "o.move_type != 'out_refund' and (barani_effective_bank" in VAT_ARCH) and ("'' if o.move_type in ('out_refund','in_refund')" in VAT_ARCH or "'' if o.move_type == 'out_refund'" in VAT_ARCH)),
    ('credit note amount credited label', 'Amount credited' in VAT_ARCH),
    ('credit reference widened', ('col-3 mb-2' in VAT_ARCH and 'barani_credit_origin_reference' in VAT_ARCH) or 'barani_credit_origin_reference_wide' in VAT_ARCH),
]
for chk in checks:
    lines.append('  %s: %s' % (chk[0], 'PASS' if chk[1] else 'FAIL'))
    if not chk[1]:
        self_error = True
if self_error:
    lines.append('ERROR: template self-check failed. Refusing.')
    raise UserError('\n'.join(lines)[:90000])
lines.append('')

# Strict tax label preflight because VAT Rate uses mapped(description).
lines.append('STRICT TAX-LABEL PREFLIGHT')
taxes = Tax.with_context(active_test=False).search([('type_tax_use', 'in', ['sale', 'purchase'])])
empty_tax_count = 0
for tax in taxes:
    if not tax.description:
        empty_tax_count = empty_tax_count + 1
        lines.append('  EMPTY: id=%s name=%s type=%s active=%s' % (tax.id, tax.name, tax.type_tax_use, tax.active))
lines.append('  checked sale/purchase taxes=%s; empty Label on Invoices=%s' % (len(taxes), empty_tax_count))
if empty_tax_count:
    lines.append('ERROR: strict tax-label preflight failed. Fill Label on Invoices first.')
    raise UserError('\n'.join(lines)[:90000])
lines.append('PASS: mapped(description) tax-rate cell is safe on current taxes.')
lines.append('')

lines.append('STANDARD FIELD PREFLIGHT')
incoterm_field = Field.search([('model', '=', 'account.move'), ('name', '=', 'invoice_incoterm_id')], limit=1)
if not incoterm_field:
    lines.append('ERROR: account.move.invoice_incoterm_id not found. Refusing to install L16g.')
    raise UserError('\n'.join(lines)[:90000])
rev_field = Field.search([('model', '=', 'account.move'), ('name', '=', 'reversed_entry_id')], limit=1)
if not rev_field:
    lines.append('ERROR: account.move.reversed_entry_id not found. Refusing to install L16g.')
    raise UserError('\n'.join(lines)[:90000])
intrastat_field = Field.search([('model', '=', 'account.move'), ('name', '=', 'intrastat_transport_mode_id')], limit=1)
if not intrastat_field:
    lines.append('ERROR: account.move.intrastat_transport_mode_id not found. Refusing to install L16g. If Intrastat is not installed, remove this item from L16g.')
    raise UserError('\n'.join(lines)[:90000])
lines.append('PASS: account.move.invoice_incoterm_id exists; template may print standard Odoo Incoterms.')
lines.append('PASS: account.move.reversed_entry_id exists; template may print credit-note original invoice reference.')
lines.append('PASS: account.move.intrastat_transport_mode_id exists; template may print Intrastat transport mode when set.')
lines.append('')

move_model = Model.search([('model', '=', 'account.move')], limit=1)
if not move_model:
    lines.append('ERROR: ir.model account.move not found.')
    raise UserError('\n'.join(lines)[:90000])

# Stored id parse. Existing deployments may have 3 ids; L4.1 writes 4.
id_text = Param.get_param(IDS_PARAMETER_KEY, '') or ''
view_id = 0
report_id = 0
paper_id = 0
layout_id = 0
if id_text:
    parts = id_text.split(',')
    if len(parts) >= 1:
        try:
            view_id = int(parts[0] or '0')
        except Exception:
            view_id = 0
    if len(parts) >= 2:
        try:
            report_id = int(parts[1] or '0')
        except Exception:
            report_id = 0
    if len(parts) >= 3:
        try:
            paper_id = int(parts[2] or '0')
        except Exception:
            paper_id = 0
    if len(parts) >= 4:
        try:
            layout_id = int(parts[3] or '0')
        except Exception:
            layout_id = 0

existing_views = View.search([('key', '=', VAT_VIEW_KEY)])
stored_report = Report.browse(report_id).exists() if report_id else Report.browse([])
technical_reports = Report.search([('model', '=', 'account.move'), ('report_name', '=', VAT_VIEW_KEY), ('report_file', '=', VAT_VIEW_KEY)])
name_reports = Report.search([('name', '=', VAT_REPORT_NAME)])
existing_papers = Paper.search([('name', '=', PAPERFORMAT_NAME)])
existing_layouts = View.search([('key', '=', LAYOUT_VIEW_KEY)])
if stored_report:
    existing_reports = stored_report
elif len(technical_reports) == 1:
    existing_reports = technical_reports
else:
    existing_reports = name_reports
lines.append('DISCOVERY')
lines.append('  stored ids %s = %r' % (IDS_PARAMETER_KEY, id_text))
lines.append('  VAT views with key:      %s' % len(existing_views))
lines.append('  VAT report by stored id: %s' % (stored_report.id if stored_report else 'none'))
lines.append('  VAT technical reports:   %s' % len(technical_reports))
lines.append('  reports with new name:   %s' % len(name_reports))
lines.append('  VAT papers with name:    %s' % len(existing_papers))
lines.append('  layout views with key:   %s' % len(existing_layouts))

if len(existing_views) > 1:
    lines.append('ERROR: duplicate views with key=%s. Refusing.' % VAT_VIEW_KEY)
    raise UserError('\n'.join(lines)[:90000])
if len(technical_reports) > 1:
    lines.append('ERROR: duplicate technical VAT reports for report_name=%s. Refusing.' % VAT_VIEW_KEY)
    raise UserError('\n'.join(lines)[:90000])
name_collision_count = 0
for rr in name_reports:
    if (not existing_reports) or rr.id != existing_reports.id:
        name_collision_count = name_collision_count + 1
if name_collision_count:
    lines.append('ERROR: another report already uses target name=%r. Refusing.' % VAT_REPORT_NAME)
    raise UserError('\n'.join(lines)[:90000])
if len(existing_papers) > 1:
    lines.append('ERROR: duplicate paperformats with name=%r. Refusing.' % PAPERFORMAT_NAME)
    raise UserError('\n'.join(lines)[:90000])
if len(existing_layouts) > 1:
    lines.append('ERROR: duplicate custom layouts with key=%s. Refusing.' % LAYOUT_VIEW_KEY)
    raise UserError('\n'.join(lines)[:90000])

existing_view = existing_views
existing_report = existing_reports
existing_paper = existing_papers
existing_layout = existing_layouts

# Collision / ownership checks.
collision = False
if existing_view:
    if existing_view.name not in (VAT_VIEW_NAME, 'BARANI VAT report_invoice_document (commercial/VAT layout)'):
        collision = True
        lines.append('COLLISION: view key exists but name=%r.' % existing_view.name)
    if existing_view.type != 'qweb':
        collision = True
        lines.append('COLLISION: VAT view type=%s not qweb.' % existing_view.type)
    if existing_view.inherit_id:
        collision = True
        lines.append('COLLISION: VAT view inherits id=%s; expected standalone.' % existing_view.inherit_id.id)
if existing_report:
    if not (existing_report.report_type == 'qweb-pdf' and existing_report.model == 'account.move' and existing_report.report_name == VAT_VIEW_KEY and existing_report.report_file == VAT_VIEW_KEY):
        collision = True
        lines.append('COLLISION: report exists but identity mismatch type=%s model=%s report_name=%s report_file=%s.' % (existing_report.report_type, existing_report.model, existing_report.report_name, existing_report.report_file))
if existing_paper:
    paper_used = Report.search([('paperformat_id', '=', existing_paper.id)])
    other_paper_users = 0
    for rr in paper_used:
        if not existing_report or rr.id != existing_report.id:
            other_paper_users = other_paper_users + 1
    if paper_id and paper_id != existing_paper.id:
        collision = True
        lines.append('COLLISION: stored paper id=%s but found name id=%s.' % (paper_id, existing_paper.id))
    if existing_report and existing_report.paperformat_id and existing_report.paperformat_id.id != existing_paper.id:
        collision = True
        lines.append('COLLISION: VAT report uses paper id=%s, not named paper id=%s.' % (existing_report.paperformat_id.id, existing_paper.id))
    if (not existing_report) and (not paper_id):
        collision = True
        lines.append('COLLISION: paperformat name exists without stored id/report ownership. Refusing to overwrite.')
    if other_paper_users:
        collision = True
        lines.append('COLLISION: paperformat is used by %s other report(s). Refusing.' % other_paper_users)
if existing_layout:
    if existing_layout.name != LAYOUT_VIEW_NAME:
        collision = True
        lines.append('COLLISION: custom layout key exists but name=%r.' % existing_layout.name)
    if existing_layout.type != 'qweb':
        collision = True
        lines.append('COLLISION: custom layout type=%s not qweb.' % existing_layout.type)
    if existing_layout.inherit_id:
        collision = True
        lines.append('COLLISION: custom layout inherits id=%s; expected standalone.' % existing_layout.inherit_id.id)
    if layout_id and layout_id != existing_layout.id:
        collision = True
        lines.append('COLLISION: stored layout id=%s but found key id=%s.' % (layout_id, existing_layout.id))
if collision:
    lines.append('ABORTING: resolve collision manually before applying.')
    raise UserError('\n'.join(lines)[:90000])
lines.append('PASS: duplicate/collision/ownership checks passed.')

billing_group = Ref(GROUP_XMLID, raise_if_not_found=False)
if billing_group:
    lines.append('Billing group resolved: %s id=%s.' % (GROUP_XMLID, billing_group.id))
else:
    lines.append('WARNING: Billing group not found; VAT report will not be group-restricted.')

# L11: widen visibility to Sales/Administrator (sales managers) in addition to Billing.
sales_group = Ref(SALES_GROUP_XMLID, raise_if_not_found=False)
if sales_group:
    lines.append('Sales/Administrator group resolved: %s id=%s.' % (SALES_GROUP_XMLID, sales_group.id))
else:
    lines.append('WARNING: Sales/Administrator group %s not found; report will bind Billing only.' % SALES_GROUP_XMLID)

# Build the group id list from whichever groups resolved (OR-visibility).
report_group_ids = []
if billing_group:
    report_group_ids.append(billing_group.id)
if sales_group:
    report_group_ids.append(sales_group.id)
if report_group_ids:
    lines.append('Report visibility groups_id will be set to: %s' % report_group_ids)
else:
    lines.append('NOTE: no visibility groups resolved; groups_id left unset (report visible to all).')
lines.append('')

# L15.2 receiving-bank data check. Report rendering uses o.partner_bank_id and does
# not fall back to another company bank account; this check confirms the intended
# receiving account exists on the company partner.
lines.append('RECEIVING BANK CHECK')
receiving_bank_count = 0
receiving_bank_ids = []
receiving_bank_name = ''
receiving_bank_address_bits = ''
receiving_bank_has_address = False
if env.company and env.company.partner_id:
    for bank in env.company.partner_id.bank_ids:
        bank_acc_compact = (bank.acc_number or '').replace(' ', '')
        bank_bic_compact = ''
        if bank.bank_id:
            bank_bic_compact = (bank.bank_id.bic or '').replace(' ', '')
        if bank_acc_compact == RECEIVING_IBAN_COMPACT and bank.bank_id and bank_bic_compact == RECEIVING_BIC:
            receiving_bank_count = receiving_bank_count + 1
            receiving_bank_ids.append(str(bank.id))
            receiving_bank_name = bank.bank_id.name or ''
            addr = ''
            if bank.bank_id.street:
                addr = bank.bank_id.street
            if bank.bank_id.zip or bank.bank_id.city:
                if addr:
                    addr = addr + ', '
                if bank.bank_id.zip:
                    addr = addr + bank.bank_id.zip
                if bank.bank_id.zip and bank.bank_id.city:
                    addr = addr + ' '
                if bank.bank_id.city:
                    addr = addr + bank.bank_id.city
            if bank.bank_id.country:
                if addr:
                    addr = addr + ', '
                addr = addr + bank.bank_id.country.name
            receiving_bank_address_bits = addr
            if addr:
                receiving_bank_has_address = True
lines.append('  expected IBAN=%s compact=%s BIC=%s' % (RECEIVING_IBAN, RECEIVING_IBAN_COMPACT, RECEIVING_BIC))
lines.append('  matching company bank accounts found=%s ids=%s' % (receiving_bank_count, ','.join(receiving_bank_ids)))
lines.append('  bank name=%r' % receiving_bank_name)
lines.append('  bank address=%r' % receiving_bank_address_bits)
if receiving_bank_count != 1:
    lines.append('ERROR: expected exactly one company bank account matching the confirmed receiving IBAN/BIC. Refusing.')
    raise UserError('\n'.join(lines)[:90000])
if not receiving_bank_name:
    lines.append('ERROR: matching bank record has no bank name. Complete res.bank.name before applying L15.2.')
    raise UserError('\n'.join(lines)[:90000])
if not receiving_bank_has_address:
    lines.append('ERROR: matching bank record has no printable bank address. Complete res.bank street/zip/city/country before applying L15.2.')
    raise UserError('\n'.join(lines)[:90000])
lines.append('PASS: confirmed receiving bank exists exactly once with name/address. Template will render it when invoice Recipient Bank matches it.')
lines.append('')

# Resolve paperformat source in dry-run too so the plan is exact.
good_spacing = 0.0
good_top = 0.0
src_desc = ''
for src_rid in [900, 234, 236, 842]:
    src_r = Report.browse(src_rid)
    if src_r.exists() and src_r.paperformat_id:
        good_spacing = src_r.paperformat_id.header_spacing or 0.0
        good_top = src_r.paperformat_id.margin_top or 0.0
        src_desc = 'report %s paper %r' % (src_rid, src_r.paperformat_id.name)
        break
if good_spacing <= 0.0:
    comp_pf = env.company.paperformat_id
    if comp_pf:
        good_spacing = comp_pf.header_spacing or 0.0
        good_top = comp_pf.margin_top or 0.0
        src_desc = 'company default paper %r' % comp_pf.name
if good_spacing <= 0.0:
    good_spacing = 35.0
    good_top = 12.0
    src_desc = 'fallback default (35mm spacing / 12mm top)'

lines.append('PAPERFORMAT PLAN')
lines.append('  source: %s' % src_desc)
lines.append('  margin_top=%s margin_bottom=%s margin_left=7 margin_right=7 header_spacing=%s dpi=90' % (good_top, VAT_BOTTOM_MARGIN, good_spacing))
lines.append('')

lines.append('PLAN')
lines.append('  - create/update standalone QWeb VAT view key=%s' % VAT_VIEW_KEY)
lines.append('  - create/update custom layout view key=%s' % LAYOUT_VIEW_KEY)
lines.append('  - create/update report action name=%r on account.move' % VAT_REPORT_NAME)
lines.append('  - create/update dedicated paper format name=%r only if owned by this VAT report' % PAPERFORMAT_NAME)
lines.append('  - raise VAT paperformat bottom margin to %s mm so footer/page numbers are not clipped' % VAT_BOTTOM_MARGIN)
lines.append('  - keep EORI, fiscal-position notes, issued-by, credit-note original reference, and Intrastat transport; format Incoterms as CODE (Full name)')
lines.append('  - keep address wrapping; retain no-indent customer/shipping gutter logic')
lines.append('  - align company tax-registration header block with the Shipping Address column using the same 18px gutter')
lines.append('  - use confirmed company receiving bank as fallback when invoice Recipient Bank is blank/missing')
lines.append('  - replace blank Signature label with Prepared by / Issued by from o.invoice_user_id/create_uid')
lines.append('  - final table cleanup retained: Description 32%; Unit 7%; COO 5%; VAT Rate 5.5%; Disc. header + percent in discount cells')
lines.append('  - keep Bank transfer band for RI/DPI; suppress customer-credit-note payment band; render bank address as a clean comma-joined string')
lines.append('  - omit payment QR entirely for now; plain IBAN/SWIFT/name/address wire instructions only')
lines.append("  - set Print-menu report label to 'VAT Invoices RI/DPI - 2026+'; technical report_name/report_file stay unchanged")
lines.append('  - add customer/shipping phone lines with Tel: prefix; rename to Down payment reconciliation; remove duplicate right-side down-payment rows and red-band note')
lines.append('  - remove duplicate centered header title; keep only the right-side document type + number label')
lines.append('  - set report filename expression to document type + number')
lines.append('  - restrict visibility to Billing + Sales/Administrator (whichever resolves)')
lines.append('  - store ids in %s as view,report,paper,layout' % IDS_PARAMETER_KEY)
lines.append('  - store one-time previous VAT arch backup and one-time previous layout arch backup when updating')
lines.append('  - NO live buttons/reports 234/236/842/900 touched')
lines.append('')

if not APPLY:
    lines.append('DRY RUN COMPLETE: no writes performed.')
    lines.append('Set APPLY=True and CONFIRM=INSTALL_VAT_LAYOUT to apply.')
    raise UserError('\n'.join(lines)[:90000])
if CONFIRM != 'INSTALL_VAT_LAYOUT':
    lines.append('ERROR: APPLY=True but CONFIRM != INSTALL_VAT_LAYOUT. Refusing.')
    raise UserError('\n'.join(lines)[:90000])

lines.append('APPLY VAT REPORT')
try:
    env.cr.execute('SAVEPOINT sp_vat_l22_install')
    paper_vals = {
        'name': PAPERFORMAT_NAME,
        'format': 'A4',
        'orientation': 'Portrait',
        'margin_top': good_top,
        'margin_bottom': VAT_BOTTOM_MARGIN,
        'margin_left': 7.0,
        'margin_right': 7.0,
        'header_spacing': good_spacing,
        'header_line': False,
        'dpi': 90,
    }
    if existing_paper:
        vat_paper = existing_paper
        vat_paper.write(paper_vals)
        lines.append('PASS: updated owned paper format id=%s.' % vat_paper.id)
    else:
        vat_paper = Paper.create(paper_vals)
        lines.append('PASS: created paper format id=%s.' % vat_paper.id)

    if existing_layout:
        layout_view = existing_layout
        if not Param.get_param(LAYOUT_BACKUP_MARKER_KEY, ''):
            Param.set_param(LAYOUT_BACKUP_KEY, layout_view.arch_db or '')
            Param.set_param(LAYOUT_BACKUP_MARKER_KEY, '1')
            lines.append('PASS: stored one-time previous layout arch backup in %s.' % LAYOUT_BACKUP_KEY)
        else:
            lines.append('NOTE: layout backup marker already exists; not overwriting backup.')
        layout_view.write({'name': LAYOUT_VIEW_NAME, 'arch_db': LAYOUT_ARCH, 'inherit_id': False, 'type': 'qweb'})
        lines.append('PASS: updated custom layout view id=%s.' % layout_view.id)
    else:
        layout_view = View.create({'name': LAYOUT_VIEW_NAME, 'key': LAYOUT_VIEW_KEY, 'type': 'qweb', 'arch_db': LAYOUT_ARCH})
        lines.append('PASS: created custom layout view id=%s key=%s.' % (layout_view.id, LAYOUT_VIEW_KEY))

    if existing_view:
        vat_view = existing_view
        if not Param.get_param(ARCH_BACKUP_MARKER_KEY, ''):
            Param.set_param(ARCH_BACKUP_KEY, vat_view.arch_db or '')
            Param.set_param(ARCH_BACKUP_MARKER_KEY, '1')
            lines.append('PASS: stored one-time previous VAT arch backup in %s.' % ARCH_BACKUP_KEY)
        else:
            lines.append('NOTE: VAT arch backup marker already exists; not overwriting backup.')
        vat_view.write({'name': VAT_VIEW_NAME, 'arch_db': VAT_ARCH, 'inherit_id': False, 'type': 'qweb'})
        lines.append('PASS: updated standalone VAT view id=%s.' % vat_view.id)
    else:
        vat_view = View.create({'name': VAT_VIEW_NAME, 'key': VAT_VIEW_KEY, 'type': 'qweb', 'arch_db': VAT_ARCH})
        lines.append('PASS: created standalone VAT view id=%s.' % vat_view.id)

    report_vals = {
        'name': VAT_REPORT_NAME,
        'model': 'account.move',
        'report_type': 'qweb-pdf',
        'report_name': VAT_VIEW_KEY,
        'report_file': VAT_VIEW_KEY,
        'binding_model_id': move_model.id,
        'binding_type': 'report',
        'paperformat_id': vat_paper.id,
        'print_report_name': PRINT_REPORT_NAME_EXPR,
    }
    if report_group_ids:
        report_vals['groups_id'] = [(6, 0, report_group_ids)]
    if existing_report:
        vat_report = existing_report
        vat_report.write(report_vals)
        lines.append('PASS: updated VAT report id=%s and reasserted binding/filename.' % vat_report.id)
    else:
        vat_report = Report.create(report_vals)
        lines.append('PASS: created VAT report id=%s.' % vat_report.id)

    Param.set_param(IDS_PARAMETER_KEY, '%s,%s,%s,%s' % (vat_view.id, vat_report.id, vat_paper.id, layout_view.id))
    lines.append('PASS: stored ids view=%s report=%s paper=%s layout=%s in %s.' % (vat_view.id, vat_report.id, vat_paper.id, layout_view.id, IDS_PARAMETER_KEY))

    if cache_inv_method == 'env.invalidate_all':
        env.invalidate_all()
    else:
        env.cache.invalidate()
    lines.append('PASS: ORM cache invalidated via %s.' % cache_inv_method)

    # Read-back verification.
    check_view = View.browse(vat_view.id)
    check_report = Report.browse(vat_report.id)
    check_layout = View.browse(layout_view.id)
    if check_view.key != VAT_VIEW_KEY or 'barani_table_lines' not in (check_view.arch_db or '') or 'barani_display_total' not in (check_view.arch_db or ''):
        raise Exception('VAT view read-back failed')
    if 'barani_vat.external_layout_standard_titled' not in (check_view.arch_db or ''):
        raise Exception('VAT arch does not reference the custom layout')
    # Body must not carry the repeating title BAND (that lives in the layout header).
    # NOTE: the bare phrase "Down Payment Invoice" now legitimately appears in the
    # body as a native deduction LABEL, so we check for the title-band marker
    # 'barani_doc_title' instead of the bare phrase to avoid a false abort.
    if '<h2' in (check_view.arch_db or '') or 'barani_doc_title' in (check_view.arch_db or ''):
        raise Exception('VAT body still appears to contain the title band')
    # L11: native deduction label present (bypasses DDS line.name).
    if 'sale_line_ids.invoice_lines.move_id' not in (check_view.arch_db or ''):
        raise Exception('L11 native deduction label logic missing from VAT body')
    # L11: settlement summary anchors to official figures.
    if 'barani_official_goods_vat' not in (check_view.arch_db or '') or 'VAT is rounded globally' not in (check_view.arch_db or ''):
        raise Exception('L11.1 official-rounded settlement bridge missing from VAT body')
    # L12: DP-invoice detection flag + currency line present.
    if 'barani_is_dp_invoice' not in (check_view.arch_db or ''):
        raise Exception('L12 DP-invoice flag missing from VAT body')
    # L12.2: tighter DP detection (excludes goods lines).
    if 'bool(barani_dp_pos_lines) and not barani_goods_lines and not barani_has_advance_deduction' not in (check_view.arch_db or ''):
        raise Exception('L12.2 DP-invoice flag does not exclude goods lines')
    # L12.2: RI payment reference deliberately PRESERVED (per user choice).
    if 'o.payment_reference' not in (check_view.arch_db or ''):
        raise Exception('L12.2 RI payment_reference display missing (should be preserved)')
    # L15: QR intentionally omitted entirely until payment-QR behavior is proven for IBAN/SWIFT use.
    if 'o.display_qr_code' in (check_view.arch_db or '') or '_generate_qr_code' in (check_view.arch_db or ''):
        raise Exception('L15 QR code block should be omitted')
    if 'barani_bank_transfer_band' not in (check_view.arch_db or '') or 'Bank transfer:' not in (check_view.arch_db or '') or 'SWIFT/BIC' not in (check_view.arch_db or ''):
        raise Exception('L15.2 bank transfer band missing from VAT body')
    if 'barani_bank_details_cell' not in (check_view.arch_db or '') or 'width:75%' not in (check_view.arch_db or '') or 'width:12.5%' not in (check_view.arch_db or ''):
        raise Exception('L15.2 compact bank/payment/due widths missing from VAT body')
    if 'Bank: ' not in (check_view.arch_db or '') or 'Bank address:' not in (check_view.arch_db or '') or 'barani_bank_has_address' not in (check_view.arch_db or '') or '<span> | </span>' not in (check_view.arch_db or ''):
        raise Exception('L15.2 bank name/address same-line renderers missing from VAT body')
    if RECEIVING_IBAN_COMPACT not in (check_view.arch_db or '') or RECEIVING_BIC not in (check_view.arch_db or '') or 'barani_receiving_bank_ok' not in (check_view.arch_db or '') or 'barani_effective_bank' not in (check_view.arch_db or '') or 'barani_company_receiving_banks' not in (check_view.arch_db or '') or '.replace(' not in (check_view.arch_db or ''):
        raise Exception('L16g sanitized confirmed receiving bank/fallback guard missing')
    if 'IBAN/BIC:' in (check_view.arch_db or ''):
        raise Exception('L15 old IBAN/BIC label still present')
    if 'Currency' not in (check_view.arch_db or ''):
        raise Exception('L12 currency line missing from VAT body')
    if not (check_layout.key == LAYOUT_VIEW_KEY and 'o_report_layout_standard' in (check_layout.arch_db or '') and 't-if="not company"' in (check_layout.arch_db or '') and 'bvt_type_label' in (check_layout.arch_db or '') and 't-field="o.name"' in (check_layout.arch_db or '') and 'barani_doc_title' not in (check_layout.arch_db or '')):
        raise Exception('custom layout read-back failed / centered header title still present')
    # L11: header company registration block present.
    if 'company_registration' not in (check_layout.arch_db or ''):
        raise Exception('L11 company registration header block missing from layout')
    if 'name="company_registration" style="font-size:10pt; line-height:1.25; padding-left:18px; box-sizing:border-box;"' not in (check_layout.arch_db or ''):
        raise Exception('L20 company registration block is not aligned with Shipping Address column')
    if 'EORI:' not in (check_layout.arch_db or ''):
        raise Exception('L16a EORI header line missing from layout')
    if 'barani_top_title_divider' not in (check_layout.arch_db or '') or 'barani_seller_buyer_divider' not in (check_layout.arch_db or ''):
        raise Exception('L13 header divider markers missing from layout')
    if 'web.address_layout' in (check_layout.arch_db or ''):
        raise Exception('L13 stock address spacer still present in custom layout')
    if 'margin-bottom:8px' not in (check_view.arch_db or ''):
        raise Exception('L14 spacing polish missing from VAT body')
    if 'barani_issued_by_slot' not in (check_view.arch_db or '') or 'Prepared by / Issued by:' not in (check_view.arch_db or '') or 'o.invoice_user_id.name' not in (check_view.arch_db or '') or 'o.create_uid.name' not in (check_view.arch_db or '') or 'Signature:' in (check_view.arch_db or ''):
        raise Exception('L16d issued-by block missing or old Signature label still present')
    if 'barani_unit_price_currency' not in (check_view.arch_db or '') or 'o.currency_id.symbol' not in (check_view.arch_db or ''):
        raise Exception('L14.2 unit-price currency marker missing from VAT body')
    if 'VAT Amount' in (check_view.arch_db or '') or 'th_vatamount' not in (check_view.arch_db or ''):
        raise Exception('L14.3 VAT header was not shortened to VAT')
    if 'width:32%' not in (check_view.arch_db or ''):
        raise Exception('L14.3 Description column width not applied')
    if 'barani_unit_col_wide' not in (check_view.arch_db or '') or 'barani_vat_rate_col_final' not in (check_view.arch_db or '') or 'barani_coo_col_final' not in (check_view.arch_db or ''):
        raise Exception('L16g unit/COO/VAT-rate column markers missing')
    if '<span>Disc.</span>' not in (check_view.arch_db or '') or 'barani_discount_percent_cell' not in (check_view.arch_db or ''):
        raise Exception('L16g discount header/cell percent cleanup missing')
    if 'barani_incoterms_code_name' not in (check_view.arch_db or '') or 'barani_incoterm_display' not in (check_view.arch_db or '') or 'Not specified' not in (check_view.arch_db or ''):
        raise Exception('L16g.3 Incoterms code/name/Not specified display missing')
    if ('barani_bank_address_joined' not in (check_view.arch_db or '') and 'barani_bank_address_clean' not in (check_view.arch_db or '')) or 'barani_bank_address_text' not in (check_view.arch_db or ''):
        raise Exception('L16g clean bank-address renderer missing')
    if (check_view.arch_db or '').count('name="barani_intrastat_transport_code"') != 1:
        raise Exception('L16g should contain exactly one Intrastat transport renderer')
    if ("o.move_type not in ('out_refund','in_refund') and (barani_effective_bank" not in (check_view.arch_db or '') and "o.move_type != 'out_refund' and (barani_effective_bank" not in (check_view.arch_db or '')):
        raise Exception('L16g credit-note bank/payment-band suppression missing')
    if 'Amount credited' not in (check_view.arch_db or ''):
        raise Exception('L16g credit-note Amount credited label missing')
    if ('col-3 mb-2' not in (check_view.arch_db or '') or 'barani_credit_origin_reference' not in (check_view.arch_db or '')) and 'barani_credit_origin_reference_wide' not in (check_view.arch_db or ''):
        raise Exception('L16g widened credit-note reference cell missing')
    if 'barani_notes_totals_table' not in (check_view.arch_db or '') or 'barani_totals_cell' not in (check_view.arch_db or '') or 'barani_fiscal_position_note' not in (check_view.arch_db or ''):
        raise Exception('L16b2 fiscal-position display-table notes/totals layout missing')
    if 'barani_incoterms_line' not in (check_view.arch_db or '') or 'invoice_incoterm_id' not in (check_view.arch_db or ''):
        raise Exception('L16c Incoterms line missing from VAT body')
    if 'barani_credit_origin_reference' not in (check_view.arch_db or '') or 'reversed_entry_id' not in (check_view.arch_db or ''):
        raise Exception('L16g credit-note original invoice reference missing from VAT body')
    if 'barani_intrastat_transport_code' not in (check_view.arch_db or '') or 'intrastat_transport_mode_id' not in (check_view.arch_db or ''):
        raise Exception('L16g Intrastat transport code block missing from VAT body')
    if 'barani_customer_phone' not in (check_view.arch_db or '') or 'barani_shipping_phone' not in (check_view.arch_db or '') or 'Tel: ' not in (check_view.arch_db or ''):
        raise Exception('L16h.1 customer/shipping phone display markers / Tel prefix missing')
    if 'barani_customer_email' not in (check_view.arch_db or '') or 'barani_shipping_email' not in (check_view.arch_db or '') or 'Email: ' not in (check_view.arch_db or ''):
        raise Exception('L22 customer/shipping email display missing')
    if 'barani_sale_order_note_fallback' not in (check_view.arch_db or '') or 'barani_note_source_orders' not in (check_view.arch_db or '') or 'sale_line_ids.order_id' not in (check_view.arch_db or ''):
        raise Exception('L22 invoice/SO note fallback missing')
    if 'barani_advance_vat_reconciliation_red_band_note' in (check_view.arch_db or '') or 'flat gross discount' in (check_view.arch_db or ''):
        raise Exception('L19 red-band down payment reconciliation note should be removed')
    if 'barani_down_payment_reconciliation_table' not in (check_view.arch_db or '') or 'Down payment reconciliation' not in (check_view.arch_db or '') or 'Invoice total after down payments' not in (check_view.arch_db or '') or 'bvt_rec_dl.price_subtotal' not in (check_view.arch_db or ''):
        raise Exception('L19 Down payment reconciliation table missing')
    if 'Total Advances Received' in (check_view.arch_db or '') or 'bvt_dl.price_total' in (check_view.arch_db or ''):
        raise Exception('L19 duplicate gross down-payment rows still present in right totals')
    if 'L16 TODO 2A' not in (check_view.arch_db or '') or 'L16 TODO 6' not in (check_view.arch_db or ''):
        raise Exception('L16g future TODO comments missing from VAT body')
    if 'barani_incoterm_display' not in (check_view.arch_db or '') or 'barani_incoterm_name' not in (check_view.arch_db or ''):
        raise Exception('L16g Incoterms CODE (Full name) renderer missing')
    if (check_view.arch_db or '').count('name="barani_intrastat_transport_code"') != 1:
        raise Exception('L16g Intrastat transport code should render only once')
    if "o.move_type != 'out_refund' and (barani_effective_bank" not in (check_view.arch_db or '') or "'' if o.move_type == 'out_refund'" not in (check_view.arch_db or ''):
        raise Exception('L16g customer credit-note payment band suppression missing')
    if 'Amount credited' not in (check_view.arch_db or ''):
        raise Exception('L16g credit-note amount credited label missing')
    if 'barani_bank_address_clean' not in (check_view.arch_db or ''):
        raise Exception('L16g clean bank-address renderer missing')
    if 'sample' in (check_view.arch_db or ''):
        raise Exception('L16b2 sample placeholder text should not be present')
    if '<p t-if="not is_html_empty(o.fiscal_position_id.note)" name="note"' in (check_view.arch_db or ''):
        raise Exception('L16b2 old full-width fiscal note paragraph still present')
    if 'id="total" class="row"' in (check_view.arch_db or '') or 'col-5 ms-auto' in (check_view.arch_db or ''):
        raise Exception('L16b2 old Bootstrap totals row still present')
    if 'font-size:8pt' not in (check_layout.arch_db or '') or 'line-height:1.1' not in (check_layout.arch_db or ''):
        raise Exception('L14.1 compact footer styling missing from custom layout')
    if vat_paper.margin_bottom < VAT_BOTTOM_MARGIN - 0.01:
        raise Exception('L14.1 paperformat bottom margin was not raised enough')
    if not (check_report.report_name == VAT_VIEW_KEY and check_report.report_file == VAT_VIEW_KEY and check_report.paperformat_id.id == vat_paper.id):
        raise Exception('report read-back failed')
    if check_report.name != VAT_REPORT_NAME:
        raise Exception('report display name/read-back failed')
    if (check_report.print_report_name or '') != PRINT_REPORT_NAME_EXPR:
        raise Exception('print_report_name read-back failed')
    # L11: visibility groups bound as expected (whichever resolved).
    bound_ids = check_report.groups_id.ids
    for gid in report_group_ids:
        if gid not in bound_ids:
            raise Exception('L11 visibility group id=%s not bound on report' % gid)
    lines.append('PASS: read-back verification passed (native label, header IDs/EORI, official totals, fiscal-position display-table notes, Incoterms code/name, issued-by, credit-note reference/payment cleanup, Intrastat transport once, final table cleanup, L20 company-registration/shipping-column alignment, L19 address no-indent/gutter fix and duplicate-row cleanup, customer/shipping phone/email, invoice/SO note fallback, RI Down payment reconciliation table/no duplicate gross rows, confirmed bank fallback, visibility groups, L15.2 bank/no-QR, layout wrapper).')

    env.cr.execute('RELEASE SAVEPOINT sp_vat_l22_install')
    lines.append('INSTALL COMPLETE.')
    lines.append('TEST: Print -> %r.' % VAT_REPORT_NAME)
    lines.append('Expected: L22 keeps L21/L21/L20/L19/L16g.3/L16h.1/L17 final behavior, removes the duplicate centered header title, keeps only the right-side document type + number label, adds Customer/Shipping Tel and Email when available, and prints invoice Terms/Notes with Sale Order note fallback when invoice narration is empty, prints an RI Down payment reconciliation table with negative base/VAT/total down-payment rows, removes the duplicate right-side down-payment rows, removes the red-band reconciliation note, and keeps the company tax-registration header block aligned with the Shipping Address column; settlement invoice right-side totals show Odoo official net invoice totals plus Balance Due and Currency, while the Down payment reconciliation table shows supply before down payments and each negative down-payment base/VAT/total row; DP invoices (INV-EXAMPLE-181) show "Subtotal (excl. VAT)" label, NO Balance Due row, and Payment Reference = Source order ref (SO-EXAMPLE); header dividers/white-space/issued-by/footer polish applied; Bank transfer band shows IBAN + SWIFT/BIC + Bank + Bank address; QR omitted; rounding note retained; report visible to Billing + Sales/Administrator.')
    lines.append('HYGIENE: reset APPLY=False / CONFIRM="", or archive/delete this server action.')
except Exception as e_apply:
    try:
        env.cr.execute('ROLLBACK TO SAVEPOINT sp_vat_l22_install')
        env.cr.execute('RELEASE SAVEPOINT sp_vat_l22_install')
        if cache_inv_method == 'env.invalidate_all':
            env.invalidate_all()
        else:
            env.cache.invalidate()
        lines.append('PASS: rolled back savepoint after failure.')
    except Exception as e_rb:
        lines.append('ROLLBACK PROBLEM: %s' % str(e_rb)[:500])
    lines.append('INSTALL FAILED: %s' % str(e_apply)[:1500])
    raise UserError('\n'.join(lines)[:90000])

text = '\n'.join(lines)
Param.set_param(OUTPUT_PARAMETER_KEY, text)
param = Param.search([('key', '=', OUTPUT_PARAMETER_KEY)], limit=1)
action = {'type': 'ir.actions.act_window', 'name': ACTION_NAME, 'res_model': 'ir.config_parameter', 'view_mode': 'form', 'res_id': param.id, 'target': 'current'}
