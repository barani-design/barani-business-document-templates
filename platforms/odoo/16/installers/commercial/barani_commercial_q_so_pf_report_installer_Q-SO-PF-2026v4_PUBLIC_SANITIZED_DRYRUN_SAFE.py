# ============================================================================
# ACTION NAME : BARANI COMMERCIAL Q/SO/PF REPORT INSTALLER — Q-SO-PF-2026v4 PUBLIC SANITIZED (commercial v3 + tune L1)
#
# Q-SO-PF-2026v3 CHANGES (arch-only; CONFIRM token unchanged):
#   1. PRO-FORMA: remove the validity/expiration column entirely (it had been relabelled
#      "Due Date" in v2). Rationale: "Payment Terms" already conveys the due/payment timing,
#      so a separate "Due Date" was redundant. Implemented by gating the column on
#      "o.validity_date and not barani_is_proforma"; Quotation/Order still show "Valid Until".
#      The v2 conditional label is reverted to plain "Valid Until" (dead branch removed).
#   2. RED PAYMENT BAND: strip a single leading "Q" from the Payment Ref. number on ALL
#      document types (Quotation, Sales Order, Pro-forma), not just the pro-forma -- the
#      reference is the same number and the band appears on all three. The v2 proforma-only
#      gate is removed. Band/cell visibility logic unchanged; only the displayed value changes.
#   (Original Q-SO-PF-2026v2 / v1 headers retained below for provenance.)
# ACTION NAME : BARANI COMMERCIAL Q/SO/PF REPORT INSTALLER — Q-SO-PF-2026v2 (production)
#
# Q-SO-PF-2026v2 CHANGES (PRO-FORMA ONLY; arch-only; CONFIRM token unchanged):
#   1. Pro-forma "Valid Until" label renamed to "Due Date". Value is still o.validity_date
#      (the order's expiration date), only the label changes. Gated on barani_is_proforma,
#      so Quotation/Order keep showing "Valid Until".
#   2. Pro-forma red payment band: strip a single leading "Q" from the Payment Ref. number
#      (e.g. Q20XXNNN -> 20XXNNN) so the reference is numeric for internet banking.
#      Gated on barani_is_proforma; band/cell visibility logic unchanged; Quotation/Order
#      red-bar reference unchanged.
#   (Original Q-SO-PF-2026v1 header retained below for provenance.)
# ACTION NAME : BARANI COMMERCIAL Q/SO/PF REPORT INSTALLER — Q-SO-PF-2026v1 (first production release)
#               Supersedes v2.4.1 and v3.1. Combines: isolated barani_commercial_* CSS
#               namespace; bank band on ALL THREE documents (Q/SO/PF); flush-before-
#               invalidate cache fix; explicit sale.order title guard; and exact-equality
#               read-back (stored arch_db must match installer arch byte-for-byte).
#               v2.4.1 fix retained: flush queued writes BEFORE invalidating the ORM cache.
#               v2.4 invalidated first, which on the update path (existing views)
#               failed with "Could not find all values of ir.ui.view(...) to flush them".
# MODEL       : Module (ir.module.module) or any model; selected records ignored.
# ACTION TO DO: Execute Python Code
# VISIBILITY  : Create/run from Settings > Technical > Server Actions. When
#               APPLY=True creates the reports, the NEW print entries will appear
#               on sale.order under Sales > Orders/Quotations > Print as
#               'Quotation / Order — 2026+' and 'PRO-FORMA — 2026+'.
#               The server action itself should normally be run from its form;
#               selected records are ignored.
#
# OUTPUT      : APPLY=False dry-run output is raised via UserError and performs
#               no writes. APPLY=True stores technical output/backups/ids in
#               ir.config_parameter, while business/report writes remain gated
#               by APPLY and CONFIRM.
#
# PAGINATION  : Dry-run output is designed to fit one dialog. If future output
#               grows beyond that, clone the standard PAGE/PAGE_SIZE pattern
#               from the BARANI template.
#
# PURPOSE     : Create/update a standalone BARANI-owned Quotation / Sales Order
#               and Pro-forma PDF family for sale.order, visually aligned with
#               the isolated BARANI VAT RI/DPI report family.
#
#               Creates/updates ONLY BARANI-owned artifacts:
#                 - standalone commercial external layout view
#                 - standalone shared sale.order body view
#                 - standalone Quotation / Sales Order wrapper view
#                 - standalone Pro-forma wrapper view
#                 - two new ir.actions.report records bound to sale.order
#                 - dedicated commercial paperformat cloned from BARANI VAT A4
#
#               Existing Odoo/DDS/Studio actions/templates are NOT modified.
#               In particular, actions 281/282 and sale.report_saleorder_document
#               are left untouched.
#
# DEFAULT     : APPLY=False. In dry-run mode, this reports the complete plan and
#               performs NO writes. To apply, set APPLY=True and
#               CONFIRM='INSTALL_BARANI_COMMERCIAL_Q_SO_PF_2026V1'.
#
# V2 CHANGES   : fixes the v1 false-positive x_ self-check; passes PF flags
#               through QWeb t-set variables instead of record context; uses
#               account.tax.description for VAT labels with an empty-label
#               preflight; sets report visibility groups where resolvable.
#
# V2.2 CHANGES : adds sales_team.group_sale_salesman so regular sales users see
#               the new Q/SO/PF print buttons; keeps Billing + Sales Manager.
#               Uses commercial_partner_id.company_registry fallback for the
#               customer ID to match commercial_partner_id.vat behavior.
#
# V2.3 CHANGES : changes the temporary customer-facing print-menu names to
#               'Quotation / Order — 2026+' and 'PRO-FORMA — 2026+'; moves
#               the PF bank-transfer band into the sale body so it prints once
#               near the totals, and mirrors the L16 RI/DPI bank details style
#               including bank name/address where present and strict IBAN+BIC.
#
# V2.4 CHANGES : rebuilds the commercial body and layout as faithful field-renamed
#               clones of the BARANI VAT invoice views (centered title, bordered
#               10-column o_main_table with per-line VAT + VAT Base, INCOTERMS and
#               fiscal-position notes, COO legend, Issued-by line, and the
#               company.report_footer footer). account.move-only constructs
#               (move_type forks, the 324 down-payment fork, amount_residual /
#               Balance Due, VAT Date, Due Date, Source, structured Payment
#               Reference, INTRASTAT, refunds) are dropped. The bank-transfer band
#               now prints on all three documents, like the invoice. Self-check
#               adds account.move-only leak guards and invoice-look assertions;
#               the field preflight expands to every sale field the clone uses.
#
# V3.2 CHANGES : consolidates v2.4.1 + v3.1 (summarised in the ACTION NAME block
#               above): isolated barani_commercial_* namespace, bank-transfer band
#               on all three documents (Q/SO/PF), flush-before-invalidate cache
#               fix, explicit sale.order title guard, and byte-for-byte exact
#               read-back of every written arch_db.
#
# V3.2.1 CHANGES: audit hygiene; no rendering or behaviour change. Corrects the
#               stale CONFIRM-token text in this header to the V32 token; switches
#               the customer ID/VAT to a commercial_partner_id fallback (matches
#               the V2.2 intent, and is byte-identical to the invoice for
#               company-direct orders, differing only for child-contact orders
#               where it shows the company identity); renames the residual
#               barani_vat_rate_col_final column to barani_commercial_vat_rate_col_final
#               for a fully isolated namespace; and adds
#               res.partner.commercial_partner_id to the field preflight.
#
# V3.2.2 CHANGES: canonical read-back + duplicate cleanup. The layout/body arch
#               strings are stored in Odoo canonical XML form (address-widget
#               t-options use double quotes with &quot;), so byte-for-byte read-back
#               round-trips cleanly. The upper red Incoterm metadata cell is also
#               removed; the only Incoterms display is the lower invoice-style
#               INCOTERMS block below the table.
#
# V3.2.3 CHANGES: layout-only; no field or logic change. Adds CSS for the
#               customer/shipping address row (.barani_addr_block .col-6): min-width:0
#               + word-wrap/overflow-wrap so a long customer or shipping name wraps
#               inside its 50% column instead of overflowing into the neighbour, plus
#               an 18px gutter on each inner edge so the two columns never touch.
#               Uses descendant selectors (no '>' combinator, which would serialise
#               to &gt; and break in the PDF). Body re-serialised canonically so the
#               exact read-back still round-trips.
#
# PRODUCTION   : Q-SO-PF-2026v1 is the FIRST PRODUCTION release, cut from development
#  RELEASE       v3.2.3. Carries the full audited invoice clone (isolated namespace,
#               bank band on all three, exact canonical read-back, commercial-partner
#               ID fallback, no upper Incoterm row, address wrap + column gutter) PLUS
#               one behaviour change: the INCOTERMS line now ALWAYS prints. When no
#               incoterm is set it shows 'INCOTERMS: Not specified' so sales can see
#               the gap. CONFIRM token is now INSTALL_BARANI_COMMERCIAL_Q_SO_PF_2026V1
#               (was ...V32). Older Vx.x changelog below is retained as provenance.
#
# SAFE_EVAL   : no import/def/lambda/comprehension/with/getattr/hasattr/setattr/
#               eval/exec/open/dir in THIS script. Lambdas occur only inside
#               stored QWeb arch strings, as in the VAT installer pattern.
# ============================================================================

APPLY = False
CONFIRM = ''

CONFIRM_TOKEN = 'INSTALL_BARANI_COMMERCIAL_Q_SO_PF_2026V1'
ACTION_NAME = 'BARANI COMMERCIAL Q/SO/PF REPORT INSTALLER — Q-SO-PF-2026v4 PUBLIC SANITIZED (commercial v3 + tune L1)'
OUTPUT_PARAMETER_KEY = 'barani.commercial_report.install.last_run'
IDS_PARAMETER_KEY = 'barani.commercial_report.ids'

LAYOUT_VIEW_KEY = 'barani_commercial.external_layout_standard_titled'
LAYOUT_VIEW_NAME = 'BARANI Commercial external_layout_standard_titled'
BODY_VIEW_KEY = 'barani_commercial.report_saleorder_document'
BODY_VIEW_NAME = 'BARANI Commercial sale.order document body'
SALE_WRAPPER_KEY = 'barani_commercial.report_saleorder'
SALE_WRAPPER_NAME = 'BARANI Commercial Quotation / Sales Order wrapper'
PF_WRAPPER_KEY = 'barani_commercial.report_saleorder_proforma'
PF_WRAPPER_NAME = 'BARANI Commercial Pro-forma wrapper'

SALE_REPORT_NAME = 'Quotation / Order — 2026+'
PF_REPORT_NAME = 'PRO-FORMA — 2026+'
SALE_REPORT_KEY = SALE_WRAPPER_KEY
PF_REPORT_KEY = PF_WRAPPER_KEY
PAPERFORMAT_NAME = 'BARANI Commercial A4 7mm'
SOURCE_VAT_PAPERFORMAT_NAME = 'BARANI VAT A4 7mm'
RECEIVING_IBAN_DISPLAY = '__RECEIVING_IBAN_DISPLAY__'
RECEIVING_IBAN_CANON = '__RECEIVING_IBAN_COMPACT__'
RECEIVING_BIC_CANON = '__RECEIVING_BIC__'

SALE_PRINT_REPORT_NAME_EXPR = "('Quotation - ' if object.state in ('draft','sent') else 'Sales Order - ') + (object.name or '')"
PF_PRINT_REPORT_NAME_EXPR = "'Pro-Forma - ' + (object.name or '')"

LAYOUT_ARCH = '''<t t-name="barani_commercial.external_layout_standard_titled">
  <t t-if="not o"><t t-set="o" t-value="doc"/></t>
  <t t-if="not company">
    <t t-if="o and o.company_id"><t t-set="company" t-value="o.company_id.sudo()"/></t>
    <t t-else=""><t t-set="company" t-value="res_company"/></t>
  </t>
  <div t-attf-class="header o_company_#{company.id}_layout" t-att-style="report_header_style">
    <div style="position:relative; height:41px;">
      <div style="float:left; width:35%; height:41px; line-height:41px; position:relative; z-index:10;">
        <img t-if="company.logo" t-att-src="image_data_uri(company.logo)" style="max-height: 41px; vertical-align:middle;" alt="Logo"/>
      </div>
      <div t-if="o and o._name == 'sale.order'" name="barani_doc_title" style="position:absolute; left:0; right:0; top:0; height:41px; line-height:41px; text-align:center; z-index:15;">
        <span style="font-size:15pt; font-weight:bold; white-space:nowrap; vertical-align:middle;" t-esc="barani_doc_title"/>
      </div>
      <div t-if="o and o._name == 'sale.order' and o.name" style="position:absolute; right:0; top:0; height:41px; line-height:41px; text-align:right; max-width:45%; z-index:15;">
        <span style="font-size:13pt; font-weight:bold; white-space:nowrap; vertical-align:middle;"><t t-esc="barani_doc_title"/>: <span t-field="o.name"/></span>
      </div>
      <div name="barani_top_title_divider" style="position:absolute; left:0; right:0; bottom:0; border-bottom:1px solid black; z-index:40;"/>
      <div style="clear:both;"/>
    </div>
    <div class="row" style="margin-top:2px;">
      <div class="col-6" name="company_address" style="font-size:10pt; line-height:1.25;">
        <ul class="list-unstyled" style="margin-bottom:2px;">
          <li t-if="company.is_company_details_empty"><t t-esc="company.partner_id" t-options="{&quot;widget&quot;: &quot;contact&quot;, &quot;fields&quot;: [&quot;address&quot;, &quot;name&quot;], &quot;no_marker&quot;: true}"/></li>
          <li t-else=""><t t-esc="company.company_details"/></li>
          <li t-if="forced_vat"><t t-esc="company.country_id.vat_label or 'Tax ID'"/>: <span t-esc="forced_vat"/></li>
        </ul>
      </div>
      <div class="col-6" name="company_registration" style="font-size:10pt; line-height:1.25;">
        <ul class="list-unstyled" style="margin-bottom:2px;">
          <li t-if="company.company_registry">ID: <span t-esc="company.company_registry"/></li>
          <li t-if="company.vat">Tax ID: <span t-esc="company.vat[2:] if (company.vat[:2] == 'SK') else company.vat"/></li>
          <li t-if="company.vat">VAT: <span t-esc="company.vat"/></li>
          <li t-if="company.vat">EORI: <span t-esc="company.vat"/></li>
        </ul>
      </div>
    </div>
    <div name="barani_seller_buyer_divider" style="border-bottom:1px solid black; width:100%; margin:1px 0 0 0;"/>
  </div>

  <div t-attf-class="article o_report_layout_standard o_company_#{company.id}_layout {{  'o_report_layout_background' if company.layout_background in ['Geometric', 'Custom']  else  '' }}" t-attf-style="background-image: url({{ 'data:image/png;base64,%s' % company.layout_background_image.decode('utf-8') if company.layout_background_image and company.layout_background == 'Custom' else '/base/static/img/bg_background_template.jpg' if company.layout_background == 'Geometric' else ''}});" t-att-data-oe-model="o and o._name" t-att-data-oe-id="o and o.id" t-att-data-oe-lang="o and o.env.context.get('lang')">
    <t t-out="0"/>
  </div>

  <div t-attf-class="footer o_standard_footer o_company_#{company.id}_layout">
    <div class="text-center" style="border-top: 1px solid black; font-size:8pt; line-height:1.1; padding-top:2px;">
      <ul class="list-inline" style="margin:0 0 1px 0; padding:0;">
        <div t-field="company.report_footer"/>
      </ul>
      <div class="text-muted"><span class="page"/> of <span class="topage"/></div>
    </div>
  </div>
</t>'''
BODY_ARCH = '''<t t-name="barani_commercial.report_saleorder_document">
  <t t-set="doc" t-value="doc.with_context(lang=(doc.partner_id.lang or user.lang))"/>
  <t t-set="o" t-value="doc"/>
  <t t-set="barani_doc_title" t-value="'Pro-Forma Invoice' if barani_is_proforma else ('Quotation' if doc.state in ('draft', 'sent') else 'Sales Order')"/>
  <t t-set="forced_vat" t-value="o.fiscal_position_id.foreign_vat"/>
  <t t-call="barani_commercial.external_layout_standard_titled" t-lang="doc.partner_id.lang or user.lang">
    <style>
      .barani_commercial_doc { font-size: 10pt; line-height: 1.25; } .barani_addr_block { margin-top: -1px; margin-bottom: 0; } .barani_info_block { padding-top: 4px; margin-bottom:8px; }
      .barani_commercial_table { table-layout: fixed; width: 100%; font-size: 10pt; line-height: 1.2; }
      .barani_commercial_table th, .barani_commercial_table td { padding: 2px 3px; vertical-align: top; overflow: hidden; }
      .barani_commercial_table .text-nowrap { white-space: nowrap; }
      #total table.table-sm td.text-end { padding-right: 10px; }
      .barani_footer_band { padding-right: 10px; }
      .barani_addr_block .col-6 { min-width: 0; box-sizing: border-box; word-wrap: break-word; overflow-wrap: break-word; }
      .barani_addr_block .col-6:first-child { padding-right: 18px; }
      .barani_addr_block .col-6:last-child { padding-left: 18px; }
    </style>

    <div class="row barani_commercial_doc barani_addr_block">
      <div class="col-6">
        <strong>Customer</strong>
        <div t-field="o.partner_id" t-options="{&quot;widget&quot;: &quot;contact&quot;, &quot;fields&quot;: [&quot;address&quot;, &quot;name&quot;], &quot;no_marker&quot;: true}"/>
        <t t-set="barani_customer_partner" t-value="o.partner_id.commercial_partner_id or o.partner_id"/>
        <t t-set="barani_customer_phone" t-value="o.partner_id.phone or o.partner_id.mobile or barani_customer_partner.phone or barani_customer_partner.mobile"/>
        <t t-set="barani_customer_email" t-value="o.partner_id.email or barani_customer_partner.email"/>
        <div t-if="barani_customer_phone" name="barani_customer_tel_line" class="mt-1">Tel: <span t-esc="barani_customer_phone"/></div>
        <div t-if="barani_customer_email" name="barani_customer_email_line">Email: <span t-esc="barani_customer_email"/></div>
        <div t-if="barani_customer_partner.company_registry or o.partner_id.company_registry" class="mt-1">ID: <span t-esc="barani_customer_partner.company_registry or o.partner_id.company_registry"/></div>
        <div t-if="barani_customer_partner.vat or o.partner_id.vat" class="mt-1">
          <t t-if="o.company_id.account_fiscal_country_id.vat_label" t-esc="o.company_id.account_fiscal_country_id.vat_label"/>
          <t t-else="">Tax ID</t>: <span t-esc="barani_customer_partner.vat or o.partner_id.vat"/>
        </div>
      </div>
      <div class="col-6" t-if="o.partner_shipping_id and (o.partner_shipping_id != o.partner_id)">
        <strong>Shipping Address</strong>
        <div t-field="o.partner_shipping_id" t-options="{&quot;widget&quot;: &quot;contact&quot;, &quot;fields&quot;: [&quot;address&quot;, &quot;name&quot;], &quot;no_marker&quot;: true}"/>
        <t t-set="barani_shipping_partner" t-value="o.partner_shipping_id"/>
        <t t-set="barani_shipping_parent" t-value="barani_shipping_partner.commercial_partner_id or barani_shipping_partner"/>
        <t t-set="barani_shipping_phone" t-value="barani_shipping_partner.phone or barani_shipping_partner.mobile or barani_shipping_parent.phone or barani_shipping_parent.mobile"/>
        <t t-set="barani_shipping_email" t-value="barani_shipping_partner.email or barani_shipping_parent.email"/>
        <div t-if="barani_shipping_phone" name="barani_shipping_tel_line" class="mt-1">Tel: <span t-esc="barani_shipping_phone"/></div>
        <div t-if="barani_shipping_email" name="barani_shipping_email_line">Email: <span t-esc="barani_shipping_email"/></div>
      </div>
    </div>

    <div class="page barani_commercial_doc">
      <div id="informations" class="row mt-3 barani_info_block">
        <div class="col-2 mb-2" name="doc_date">
          <strong><t t-esc="'Pro-forma Date' if barani_is_proforma else ('Quotation Date' if o.state in ('draft', 'sent') else 'Order Date')"/></strong>
          <p class="m-0"><span t-field="o.date_order" t-options="{&quot;widget&quot;: &quot;date&quot;}"/></p>
        </div>
        <div class="col-2 mb-2" t-if="o.validity_date and not barani_is_proforma" name="validity_date">
          <strong>Valid Until</strong><p class="m-0" t-field="o.validity_date"/>
        </div>
        <div class="col-2 mb-2" t-if="o.client_order_ref" name="customer_ref">
          <strong>Customer Ref.</strong><p class="m-0" t-field="o.client_order_ref"/>
        </div>
        <div class="col-4 mb-2" t-if="o.payment_term_id" name="payment_terms" style="padding-right:12px;">
          <strong>Payment Terms</strong><p class="m-0" t-field="o.payment_term_id.name"/>
        </div>
        <div class="col-2 mb-2" name="payment_method">
          <strong>Payment Method</strong><p class="m-0">Wire transfer</p>
        </div>
      </div>

      <t t-set="display_discount" t-value="any(l.discount for l in o.order_line)"/>
      <table class="table table-sm o_main_table barani_commercial_table" name="sale_line_table">
        <colgroup>
          <col style="width:32%"/>
          <col style="width:8%"/>
          <col name="barani_coo_col_final" style="width:5%"/>
          <col style="width:6.5%"/>
          <col name="barani_unit_col_wide" style="width:7%"/>
          <col style="width:8%"/>
          <col t-if="display_discount" style="width:5.5%"/>
          <col name="barani_commercial_vat_rate_col_final" style="width:5.5%"/>
          <col style="width:7.5%"/>
          <col style="width:10%"/>
        </colgroup>
        <thead>
          <tr>
            <th name="th_description" class="text-start"><span>Description</span></th>
            <th name="th_hscode" class="text-start"><span>HS Code</span></th>
            <th name="th_coo" class="text-center"><span>COO</span></th>
            <th name="th_quantity" class="text-end"><span>Qty</span></th>
            <th name="th_uom" class="text-start"><span>Unit</span></th>
            <th name="th_priceunit" class="text-end"><span>Unit Price</span></th>
            <th name="th_discount" t-if="display_discount" class="text-end"><span>Disc.</span></th>
            <th name="th_vatrate" class="text-end"><span>VAT Rate</span></th>
            <th name="th_vatamount" class="text-end"><span>VAT</span></th>
            <th name="th_vatbase" class="text-end"><span>VAT Base</span></th>
          </tr>
        </thead>
        <tbody class="sale_tbody">
          <t t-foreach="o.order_line" t-as="line">
            <tr t-if="line.display_type not in ('line_section','line_note')">
              <td name="td_name"><span t-field="line.name" t-options="{&quot;widget&quot;: &quot;text&quot;}"/></td>
              <td name="td_hscode" class="text-start"><span t-if="line.product_id.hs_code" t-field="line.product_id.hs_code"/></td>
              <td name="td_coo" class="text-center"><span t-if="line.product_id.country_of_origin" t-field="line.product_id.country_of_origin.code"/></td>
              <td name="td_qty" class="text-end"><span t-field="line.product_uom_qty"/></td>
              <td name="td_unit" class="text-start"><span t-field="line.product_uom" groups="uom.group_uom"/></td>
              <td name="td_priceunit" class="text-end"><span class="text-nowrap" name="barani_unit_price_currency"><span t-field="line.price_unit" t-options="{&quot;widget&quot;: &quot;float&quot;, &quot;precision&quot;: 2}"/> <span t-esc="o.currency_id.symbol"/></span></td>
              <td name="td_discount" t-if="display_discount" class="text-end"><span class="text-nowrap" name="barani_discount_percent_cell"><span t-field="line.discount" t-options="{&quot;widget&quot;: &quot;float&quot;, &quot;precision&quot;: 1}"/> %</span></td>
              <td name="td_vatrate" class="text-end"><span class="text-nowrap" t-esc="', '.join(line.tax_id.mapped('description'))"/></td>
              <td name="td_vatamount" class="text-end"><span class="text-nowrap" t-esc="line.price_total - line.price_subtotal" t-options="{&quot;widget&quot;: &quot;monetary&quot;, &quot;display_currency&quot;: o.currency_id}"/></td>
              <td name="td_vatbase" class="text-end o_price_total"><span class="text-nowrap" t-field="line.price_subtotal"/></td>
            </tr>
            <tr t-if="line.display_type == 'line_section'" class="bg-200 fw-bold o_line_section">
              <td t-att-colspan="'10' if display_discount else '9'"><span t-field="line.name" t-options="{&quot;widget&quot;: &quot;text&quot;}"/></td>
            </tr>
            <tr t-if="line.display_type == 'line_note'" class="fst-italic o_line_note">
              <td t-att-colspan="'10' if display_discount else '9'"><span t-field="line.name" t-options="{&quot;widget&quot;: &quot;text&quot;}"/></td>
            </tr>
          </t>

          <tr class="border-black o_total fw-bold">
            <td class="text-end" t-att-colspan="'7' if display_discount else '6'"><span>Totals</span></td>
            <td class="text-end"><span>VAT</span></td>
            <td class="text-end"><span t-esc="o.amount_tax" t-options="{&quot;widget&quot;: &quot;monetary&quot;, &quot;display_currency&quot;: o.currency_id}"/></td>
            <td class="text-end"><span t-esc="o.amount_untaxed" t-options="{&quot;widget&quot;: &quot;monetary&quot;, &quot;display_currency&quot;: o.currency_id}"/></td>
          </tr>
        </tbody>
      </table>

      <div name="barani_notes_totals_table" style="display:table; width:100%; table-layout:fixed; margin-top:3px;">
        <div name="barani_notes_cell" style="display:table-cell; width:57%; vertical-align:top; font-size:10pt; line-height:1.25; padding:0 12px 0 0;">
          <t t-set="barani_line_real" t-value="o.order_line.filtered(lambda l: l.display_type not in ('line_section','line_note'))"/>
          <t t-set="barani_line_vat_sum" t-value="sum(barani_line_real.mapped('price_total')) - sum(barani_line_real.mapped('price_subtotal'))"/>
          <p t-if="(barani_line_vat_sum - o.amount_tax) &gt; 0.005 or (o.amount_tax - barani_line_vat_sum) &gt; 0.005" class="text-muted" style="font-size:10pt; margin:0 0 6px 0;">VAT is rounded globally; the VAT total follows Odoo's official tax rounding. Sum of displayed line VAT amounts: <span t-esc="barani_line_vat_sum" t-options="{&quot;widget&quot;: &quot;monetary&quot;, &quot;display_currency&quot;: o.currency_id}"/>.</p>
          <t t-set="barani_incoterm_code" t-value="o.incoterm.code or '' if o.incoterm else ''"/>
          <t t-set="barani_incoterm_name" t-value="o.incoterm.name or '' if o.incoterm else ''"/>
          <t t-set="barani_incoterm_display" t-value="barani_incoterm_code + ((' (' + barani_incoterm_name + ')') if (barani_incoterm_name and barani_incoterm_name != barani_incoterm_code) else '')"/>
          <div name="barani_incoterms_line" style="margin:0 0 4px 0; font-size:10pt; line-height:1.25;">
            <strong>INCOTERMS:</strong> <span name="barani_incoterms_code_name" t-esc="barani_incoterm_display if o.incoterm else 'Not specified'"/>
          </div>
          <div t-if="o.fiscal_position_id" name="barani_fiscal_position_note" style="margin:0 0 4px 0; font-size:10pt; line-height:1.25;">
            <strong>Fiscal position:</strong> <span t-field="o.fiscal_position_id.name"/>
          </div>
          <div t-if="not is_html_empty(o.fiscal_position_id.note)" name="barani_fiscal_position_note_text" style="margin:0 0 4px 0; font-size:10pt; line-height:1.25;">
            <span t-field="o.fiscal_position_id.note"/>
          </div>
        </div>
        <div id="total" name="barani_totals_cell" style="display:table-cell; width:43%; vertical-align:top;">
          <table class="table table-sm">
            <tr>
              <td>Total excl. VAT</td>
              <td class="text-end"><span t-esc="o.amount_untaxed" t-options="{&quot;widget&quot;: &quot;monetary&quot;, &quot;display_currency&quot;: o.currency_id}"/></td>
            </tr>
            <tr>
              <td>Total VAT</td>
              <td class="text-end"><span t-esc="o.amount_tax" t-options="{&quot;widget&quot;: &quot;monetary&quot;, &quot;display_currency&quot;: o.currency_id}"/></td>
            </tr>
            <tr class="border-black">
              <td><strong>Total incl. VAT</strong></td>
              <td class="text-end"><strong><span t-esc="o.amount_total" t-options="{&quot;widget&quot;: &quot;monetary&quot;, &quot;display_currency&quot;: o.currency_id}"/></strong></td>
            </tr>
            <tr>
              <td>Currency</td>
              <td class="text-end"><span t-esc="o.currency_id.name or 'EUR'"/></td>
            </tr>
          </table>
        </div>
      </div>

      <div t-if="not is_html_empty(o.note)" name="comment" style="margin-top:12px; font-size:10pt; line-height:1.25;">
        <strong>Notes</strong>
        <div name="barani_order_note_text" style="margin-top:2px;" t-field="o.note"/>
      </div>

      <p class="text-muted" style="font-size:8pt; margin-top:6px;">COO = Country of Origin</p>

      <t t-set="barani_pdf_payment_ref" t-value="o.name or ''"/>
      <t t-set="barani_payment_bank" t-value="o.company_id.partner_id.bank_ids.filtered(lambda b: (b.acc_number or '').replace(' ', '') == '__RECEIVING_IBAN_COMPACT__' and ((b.bank_id.bic or '').replace(' ', '') == '__RECEIVING_BIC__'))[:1]"/>
      <t t-set="barani_receiving_bank_ok" t-value="bool(barani_payment_bank)"/>
      <t t-set="barani_bank_record" t-value="barani_payment_bank.bank_id if (barani_receiving_bank_ok and barani_payment_bank.bank_id) else False"/>
      <t t-set="barani_bank_has_address" t-value="barani_bank_record and (barani_bank_record.street or barani_bank_record.city or barani_bank_record.country)"/>
      <div name="barani_bank_transfer_band" t-if="barani_receiving_bank_ok or barani_pdf_payment_ref" style="display:table; width:100%; table-layout:fixed; background-color:#E79C9C; font-size:9pt; line-height:1.2;">
        <div name="barani_bank_details_cell" class="barani_footer_band" style="display:table-cell; width:75%; text-align:left; vertical-align:top; background-color:#E79C9C; padding:3px 6px;" t-if="barani_receiving_bank_ok">
          <div><strong>Bank transfer:</strong></div>
          <div><span>IBAN: </span><span t-field="barani_payment_bank.acc_number"/><span> | SWIFT/BIC: </span><span t-field="barani_payment_bank.bank_id.bic"/></div>
          <div t-if="barani_bank_record and (barani_bank_record.name or barani_bank_has_address)">
            <t t-if="barani_bank_record.name"><span>Bank: </span><span t-field="barani_bank_record.name"/></t>
            <t t-if="barani_bank_record.name and barani_bank_has_address"><span> | </span></t>
            <t t-if="barani_bank_has_address">
              <t t-set="barani_bank_city_line" t-value="(barani_bank_record.zip or '') + (' ' if (barani_bank_record.zip and barani_bank_record.city) else '') + (barani_bank_record.city or '')"/>
              <t t-set="barani_bank_address_text" t-value="(barani_bank_record.street or '') + ((', ' + barani_bank_city_line) if (barani_bank_city_line and barani_bank_record.street) else (barani_bank_city_line if barani_bank_city_line and not barani_bank_record.street else '')) + ((', ' + barani_bank_record.country.name) if (barani_bank_record.country and ((barani_bank_record.street or '') or barani_bank_city_line)) else (barani_bank_record.country.name if barani_bank_record.country else ''))"/>
              <span>Bank address: </span><span name="barani_bank_address_clean" t-esc="barani_bank_address_text"/>
            </t>
          </div>
        </div>
        <div name="barani_payment_ref_cell" class="barani_footer_band" t-if="barani_pdf_payment_ref" t-att-style="'display:table-cell; width:25%; text-align:right; vertical-align:top; background-color:#E79C9C; padding:3px 6px;' if barani_receiving_bank_ok else 'display:table-cell; width:100%; text-align:right; vertical-align:top; background-color:#E79C9C; padding:3px 6px;'"><span><strong>Payment Ref.:</strong><br/></span><span t-esc="barani_pdf_payment_ref[1:] if barani_pdf_payment_ref[:1] == 'Q' else barani_pdf_payment_ref"/></div>
      </div>

      <t t-set="barani_issued_by" t-value="o.user_id.name if o.user_id else (o.create_uid.name if o.create_uid else '')"/>
      <div class="row mt-4" name="barani_issued_by_slot"><div class="col-12 text-end" style="padding-right:33%; font-size:10pt;"><span><strong>Prepared by / Issued by:</strong> </span><span t-esc="barani_issued_by"/></div></div>
    </div>
  </t>
</t>'''
SALE_WRAPPER_ARCH = '<t t-name="barani_commercial.report_saleorder">\n  <t t-call="web.html_container">\n    <t t-foreach="docs" t-as="doc">\n      <t t-set="barani_is_proforma" t-value="False"/>\n      <t t-set="barani_show_payment_band" t-value="False"/>\n      <t t-call="barani_commercial.report_saleorder_document" t-lang="doc.partner_id.lang or user.lang"/>\n    </t>\n  </t>\n</t>'
PF_WRAPPER_ARCH = '<t t-name="barani_commercial.report_saleorder_proforma">\n  <t t-call="web.html_container">\n    <t t-foreach="docs" t-as="doc">\n      <t t-set="barani_is_proforma" t-value="True"/>\n      <t t-set="barani_show_payment_band" t-value="True"/>\n      <t t-call="barani_commercial.report_saleorder_document" t-lang="doc.partner_id.lang or user.lang"/>\n    </t>\n  </t>\n</t>'

View = env['ir.ui.view'].sudo()
Report = env['ir.actions.report'].sudo()
Paper = env['report.paperformat'].sudo()
Param = env['ir.config_parameter'].sudo()
Model = env['ir.model'].sudo()
Field = env['ir.model.fields'].sudo()
Company = env['res.company'].sudo()
Group = env['res.groups'].sudo()
IMD = env['ir.model.data'].sudo()
Tax = env['account.tax'].sudo().with_context(active_test=False)

NL = chr(10)
lines = []
lines.append(ACTION_NAME)
lines.append('APPLY=%s CONFIRM=%s' % (APPLY, CONFIRM))
lines.append('Scope: new standalone BARANI sale.order print options only; existing Odoo/DDS/Studio actions and templates untouched.')
lines.append('')

sale_model = Model.search([('model', '=', 'sale.order')], limit=1)
if not sale_model:
    lines.append('ERROR: ir.model sale.order not found. Is Sales installed?')
    raise UserError(NL.join(lines)[:90000])

# Read-only snapshot of live stock actions to make the no-touch boundary explicit.
lines.append('NO-TOUCH BASELINE')
for rid in [281, 282]:
    rr = Report.browse(rid)
    if rr.exists():
        lines.append('  action id=%s name=%r model=%s report_name=%s paper=%s' % (rid, rr.name, rr.model, rr.report_name, rr.paperformat_id.name if rr.paperformat_id else ''))
    else:
        lines.append('  action id=%s not found on this DB; no-touch boundary still applies by report_name.' % rid)
lines.append('')

# Template self-checks.
all_arch = LAYOUT_ARCH + BODY_ARCH + SALE_WRAPPER_ARCH + PF_WRAPPER_ARCH
self_error = False
checks = [
    ['layout standalone t-name', 'barani_commercial.external_layout_standard_titled' in LAYOUT_ARCH],
    ['body standalone t-name', 'barani_commercial.report_saleorder_document' in BODY_ARCH],
    ['sale wrapper uses web.html_container only as PDF shell', 'web.html_container' in SALE_WRAPPER_ARCH],
    ['PF wrapper uses web.html_container only as PDF shell', 'web.html_container' in PF_WRAPPER_ARCH],
    ['no stock sale body t-call', 'sale.report_saleorder_document' not in all_arch],
    ['no stock pro-forma t-call', 'sale.report_saleorder_pro_forma' not in all_arch],
    ['no web.external_layout t-call', 'web.external_layout' not in all_arch],
    ['no patched account tax totals t-call', 'account.document_tax_totals' not in all_arch],
    ['no explicit DDS field prefix', 'dds_' not in all_arch],
    ['no Studio field prefix', 'x_studio_' not in all_arch and '.x_' not in all_arch],
    ['no BRN field prefix', 'brn_' not in all_arch],
    ['no account.move-only invoice_line_ids', 'invoice_line_ids' not in all_arch],
    ['no account.move-only move_type fork', 'move_type' not in all_arch],
    ['no account.move-only amount_residual/Balance Due', 'amount_residual' not in all_arch],
    ['no account.move-only invoice_date_due/Due Date', 'invoice_date_due' not in all_arch],
    ['no account.move-only invoice_incoterm_id', 'invoice_incoterm_id' not in all_arch],
    ['no account.move-only invoice_user_id', 'invoice_user_id' not in all_arch],
    ['no account.move-only INTRASTAT field', 'intrastat' not in all_arch],
    ['no account.move-only structured payment_reference', 'payment_reference' not in all_arch],
    ['no account.move-only invoice_origin/Source', 'invoice_origin' not in all_arch],
    ['no down-payment fork residue', 'is_downpayment' not in all_arch and 'barani_dp_' not in all_arch and 'bvt_' not in all_arch],
    ['HS code included', 'product_id.hs_code' in BODY_ARCH],
    ['COO code included', 'country_of_origin.code' in BODY_ARCH],
    ['customer VAT/registry use commercial partner fallback', 'barani_customer_partner' in BODY_ARCH and 'commercial_partner_id' in BODY_ARCH],
    ['invoice bordered o_main_table cloned', 'o_main_table' in BODY_ARCH],
    ['conditional discount column cloned', '<col t-if="display_discount"' in BODY_ARCH],
    ['per-line VAT and VAT Base columns cloned', 'th_vatamount' in BODY_ARCH and 'th_vatbase' in BODY_ARCH],
    ['centered title via barani_doc_title', 'barani_doc_title' in LAYOUT_ARCH and 'text-align:center' in LAYOUT_ARCH],
    ['EORI retained in seller header', 'EORI' in LAYOUT_ARCH],
    ['company.report_footer footer cloned', 'company.report_footer' in LAYOUT_ARCH],
    ['INCOTERMS line cloned', 'INCOTERMS:' in BODY_ARCH],
    ['upper red Incoterm metadata removed', '<strong>Incoterm</strong>' not in BODY_ARCH and 'name="incoterm"' not in BODY_ARCH and 'name=&quot;incoterm&quot;' not in BODY_ARCH],
    ['only lower INCOTERMS display remains', BODY_ARCH.count('INCOTERMS:') == 1 and 'name="barani_incoterms_line"' in BODY_ARCH],
    ['COO legend cloned', 'COO = Country of Origin' in BODY_ARCH],
    ['Issued-by line cloned', 'Prepared by / Issued by' in BODY_ARCH],
    ['sale field mapping applied', 'order_line' in BODY_ARCH and 'product_uom_qty' in BODY_ARCH and 'o.date_order' in BODY_ARCH],
    ['PF flags passed via QWeb t-set variables', 'doc.env.context.get' not in all_arch and 't-set="barani_is_proforma"' in all_arch and 't-set="barani_show_payment_band"' in all_arch],
    ['bank band present in body', 'barani_bank_transfer_band' in BODY_ARCH],
    ['bank band shows on all three (no show_payment_band gate)', 'barani_show_payment_band' not in BODY_ARCH],
    ['confirmed receiving IBAN/BIC guard in QWeb', RECEIVING_IBAN_CANON in BODY_ARCH and RECEIVING_BIC_CANON in BODY_ARCH],
    ['tax labels use Label on Invoices', "tax_id.mapped('description')" in BODY_ARCH],
    ['inline totals only', 'amount_untaxed' in BODY_ARCH and 'amount_tax' in BODY_ARCH and 'amount_total' in BODY_ARCH],
]
lines.append('TEMPLATE SELF-CHECK')
for chk in checks:
    ok = chk[1]
    lines.append('  %s: %s' % (chk[0], 'PASS' if ok else 'FAIL'))
    if not ok:
        self_error = True
if self_error:
    lines.append('ERROR: template self-check failed. Refusing.')
    raise UserError(NL.join(lines)[:90000])
lines.append('')

# Field preflight for fields the template references directly.
field_checks = [
    ['product.product', 'hs_code'],
    ['product.product', 'country_of_origin'],
    ['res.country', 'code'],
    ['sale.order', 'date_order'],
    ['sale.order', 'validity_date'],
    ['sale.order', 'client_order_ref'],
    ['sale.order', 'incoterm'],
    ['sale.order', 'payment_term_id'],
    ['sale.order', 'fiscal_position_id'],
    ['sale.order', 'user_id'],
    ['sale.order', 'note'],
    ['sale.order', 'currency_id'],
    ['sale.order', 'amount_untaxed'],
    ['sale.order', 'amount_tax'],
    ['sale.order', 'amount_total'],
    ['sale.order', 'partner_shipping_id'],
    ['sale.order.line', 'product_uom_qty'],
    ['sale.order.line', 'product_uom'],
    ['sale.order.line', 'price_unit'],
    ['sale.order.line', 'price_subtotal'],
    ['sale.order.line', 'price_total'],
    ['sale.order.line', 'discount'],
    ['sale.order.line', 'display_type'],
    ['sale.order.line', 'name'],
    ['sale.order.line', 'tax_id'],
    ['account.fiscal.position', 'foreign_vat'],
    ['account.fiscal.position', 'note'],
    ['res.company', 'vat'],
    ['res.company', 'company_registry'],
    ['res.company', 'logo'],
    ['res.company', 'report_footer'],
    ['res.company', 'account_fiscal_country_id'],
    ['res.partner', 'commercial_partner_id'],
    ['res.partner', 'company_registry'],
    ['res.partner', 'vat'],
    ['account.tax', 'description'],
    ['res.partner.bank', 'acc_number'],
    ['res.partner.bank', 'bank_id'],
    ['res.bank', 'bic'],
    ['res.bank', 'name'],
    ['res.bank', 'street'],
    ['res.bank', 'zip'],
    ['res.bank', 'city'],
    ['res.bank', 'country'],
]
missing_field = False
lines.append('FIELD PREFLIGHT')
for fc in field_checks:
    cnt = Field.search_count([('model', '=', fc[0]), ('name', '=', fc[1])])
    lines.append('  %s.%s: %s' % (fc[0], fc[1], 'PASS' if cnt else 'MISSING'))
    if not cnt:
        missing_field = True
if missing_field:
    lines.append('ERROR: one or more template field references are missing. Rerun the v3 field-provenance probe and adjust the template before applying.')
    raise UserError(NL.join(lines)[:90000])
lines.append('')

# Strict sale-tax label preflight. The commercial report mirrors VAT-family
# display by printing account.tax.description (Label on Invoices), not tax.name.
empty_tax_count = 0
empty_tax_samples = []
tax_count = 0
for tx in Tax.search([('type_tax_use', 'in', ['sale', 'all'])], order='id'):
    tax_count = tax_count + 1
    if not tx.description:
        empty_tax_count = empty_tax_count + 1
        if len(empty_tax_samples) < 12:
            empty_tax_samples.append('id=%s name=%r type=%s active=%s' % (tx.id, tx.name, tx.type_tax_use, tx.active))
lines.append('STRICT SALE TAX-LABEL PREFLIGHT')
lines.append('  checked sale/all taxes=%s; empty Label on Invoices=%s' % (tax_count, empty_tax_count))
for sample_tax in empty_tax_samples:
    lines.append('  EMPTY: %s' % sample_tax)
if empty_tax_count:
    lines.append('ERROR: one or more sale/all taxes have empty Label on Invoices. Refusing because the VAT Rate column uses tax.description.')
    raise UserError(NL.join(lines)[:90000])
lines.append('PASS: mapped(description) tax-rate cell is safe on current sale/all taxes.')
lines.append('')

# Resolve report visibility groups. Q/SO/PF are sales documents, so regular
# sales users must see the buttons; Billing is retained for accounting/admin use.
group_ids = []
group_labels = []
for gx in [
    ['sales_team', 'group_sale_salesman', 'Sales/User'],
    ['sales_team', 'group_sale_salesman_all_leads', 'Sales/User: All Documents'],
    ['sales_team', 'group_sale_manager', 'Sales/Administrator'],
    ['account', 'group_account_invoice', 'Billing'],
]:
    gxd = IMD.search([('module', '=', gx[0]), ('name', '=', gx[1]), ('model', '=', 'res.groups')], limit=1)
    if gxd:
        gg = Group.browse(gxd.res_id)
        if gg.exists():
            if gg.id not in group_ids:
                group_ids.append(gg.id)
                group_labels.append('%s.%s id=%s name=%s (%s)' % (gx[0], gx[1], gg.id, gg.name, gx[2]))
lines.append('REPORT VISIBILITY GROUPS')
if group_ids:
    lines.append('  groups_id will be set to: %s' % group_ids)
    for gl in group_labels:
        lines.append('  resolved: %s' % gl)
else:
    lines.append('  WARNING: no Sales/Billing groups resolved; reports will not be group-restricted.')
lines.append('')

# Receiving bank guard. The PF footer band renders only this account and no fallback.
match_count = 0
match_details = []
for c in Company.search([]):
    for b in c.partner_id.bank_ids:
        canon = (b.acc_number or '').replace(' ', '')
        bic_canon = (b.bank_id.bic or '').replace(' ', '') if b.bank_id else ''
        if canon == RECEIVING_IBAN_CANON and bic_canon == RECEIVING_BIC_CANON:
            match_count = match_count + 1
            match_details.append('company_id=%s company=%s bank_account_id=%s acc=%s bic=%s bank=%s' % (c.id, c.name, b.id, b.acc_number or '', b.bank_id.bic or '', b.bank_id.name or ''))
lines.append('RECEIVING BANK PREFLIGHT')
lines.append('  expected IBAN=%s canonical=%s BIC=%s' % (RECEIVING_IBAN_DISPLAY, RECEIVING_IBAN_CANON, RECEIVING_BIC_CANON))
lines.append('  matching company bank accounts found=%s' % match_count)
for md in match_details:
    lines.append('  %s' % md)
if match_count != 1:
    lines.append('ERROR: expected exactly one receiving bank match with expected BIC. Refusing to install PF payment band with fallback behavior.')
    raise UserError(NL.join(lines)[:90000])
lines.append('PASS: confirmed receiving bank exists exactly once with expected BIC. PF band uses no fallback.')
lines.append('')

# Discover existing BARANI-owned artifacts.
layout_views = View.search([('key', '=', LAYOUT_VIEW_KEY)])
body_views = View.search([('key', '=', BODY_VIEW_KEY)])
sale_wrappers = View.search([('key', '=', SALE_WRAPPER_KEY)])
pf_wrappers = View.search([('key', '=', PF_WRAPPER_KEY)])
sale_reports = Report.search([('report_name', '=', SALE_REPORT_KEY)])
pf_reports = Report.search([('report_name', '=', PF_REPORT_KEY)])
papers = Paper.search([('name', '=', PAPERFORMAT_NAME)])

lines.append('DISCOVERY')
lines.append('  layout views key=%s: %s' % (LAYOUT_VIEW_KEY, len(layout_views)))
lines.append('  body views key=%s: %s' % (BODY_VIEW_KEY, len(body_views)))
lines.append('  sale wrappers key=%s: %s' % (SALE_WRAPPER_KEY, len(sale_wrappers)))
lines.append('  PF wrappers key=%s: %s' % (PF_WRAPPER_KEY, len(pf_wrappers)))
lines.append('  sale reports report_name=%s: %s' % (SALE_REPORT_KEY, len(sale_reports)))
lines.append('  PF reports report_name=%s: %s' % (PF_REPORT_KEY, len(pf_reports)))
lines.append('  paperformats name=%r: %s' % (PAPERFORMAT_NAME, len(papers)))

if len(layout_views) > 1 or len(body_views) > 1 or len(sale_wrappers) > 1 or len(pf_wrappers) > 1 or len(sale_reports) > 1 or len(pf_reports) > 1 or len(papers) > 1:
    lines.append('ERROR: duplicate BARANI commercial artifact found. Resolve manually before applying.')
    raise UserError(NL.join(lines)[:90000])

collision = False
for vv in layout_views + body_views + sale_wrappers + pf_wrappers:
    if vv.type != 'qweb':
        collision = True
        lines.append('COLLISION: view id=%s key=%s type=%s is not qweb.' % (vv.id, vv.key, vv.type))
    if vv.inherit_id:
        collision = True
        lines.append('COLLISION: view id=%s key=%s inherits %s; expected standalone.' % (vv.id, vv.key, vv.inherit_id.id))
for rr in sale_reports:
    if not (rr.model == 'sale.order' and rr.report_type == 'qweb-pdf' and rr.report_name == SALE_REPORT_KEY and rr.report_file == SALE_REPORT_KEY):
        collision = True
        lines.append('COLLISION: sale report identity mismatch id=%s model=%s type=%s report_name=%s report_file=%s' % (rr.id, rr.model, rr.report_type, rr.report_name, rr.report_file))
for rr in pf_reports:
    if not (rr.model == 'sale.order' and rr.report_type == 'qweb-pdf' and rr.report_name == PF_REPORT_KEY and rr.report_file == PF_REPORT_KEY):
        collision = True
        lines.append('COLLISION: PF report identity mismatch id=%s model=%s type=%s report_name=%s report_file=%s' % (rr.id, rr.model, rr.report_type, rr.report_name, rr.report_file))
if papers:
    paper_users = Report.search([('paperformat_id', '=', papers.id)])
    for pu in paper_users:
        if pu.report_name not in [SALE_REPORT_KEY, PF_REPORT_KEY]:
            collision = True
            lines.append('COLLISION: paperformat %r is used by non-BARANI-commercial report id=%s name=%r report_name=%s' % (PAPERFORMAT_NAME, pu.id, pu.name, pu.report_name))
if collision:
    lines.append('ABORTING: collision/ownership check failed.')
    raise UserError(NL.join(lines)[:90000])
lines.append('PASS: duplicate/collision/ownership checks passed.')
lines.append('')

# Paperformat clone plan.
source_paper = Paper.search([('name', '=', SOURCE_VAT_PAPERFORMAT_NAME)], limit=1)
if source_paper:
    margin_top = source_paper.margin_top
    margin_bottom = source_paper.margin_bottom
    margin_left = source_paper.margin_left
    margin_right = source_paper.margin_right
    header_spacing = source_paper.header_spacing
    dpi = source_paper.dpi
    source_desc = 'source VAT paperformat id=%s name=%r' % (source_paper.id, source_paper.name)
else:
    margin_top = 40.0
    margin_bottom = 18.0
    margin_left = 7.0
    margin_right = 7.0
    header_spacing = 35.0
    dpi = 90
    source_desc = 'fallback BARANI VAT geometry constants'
lines.append('PAPERFORMAT PLAN')
lines.append('  %s' % source_desc)
lines.append('  margins T/B/L/R=%s/%s/%s/%s header_spacing=%s dpi=%s' % (margin_top, margin_bottom, margin_left, margin_right, header_spacing, dpi))
lines.append('')

lines.append('PLAN')
lines.append('  - create/update dedicated paperformat %r' % PAPERFORMAT_NAME)
lines.append('  - create/update standalone layout key=%s' % LAYOUT_VIEW_KEY)
lines.append('  - create/update standalone body key=%s' % BODY_VIEW_KEY)
lines.append('  - create/update standalone wrapper key=%s' % SALE_WRAPPER_KEY)
lines.append('  - create/update standalone PF wrapper key=%s' % PF_WRAPPER_KEY)
lines.append('  - create/update report action %r on sale.order, visible to Sales users/managers + Billing where resolvable' % SALE_REPORT_NAME)
lines.append('  - create/update report action %r on sale.order, visible to Sales users/managers + Billing where resolvable' % PF_REPORT_NAME)
lines.append('  - use one shared sale.order body for Q/SO/PF; bank band prints on Q, SO, and PF; upper Incoterm metadata row is removed and only the lower INCOTERMS block remains')
lines.append('  - do not touch action 281 / 282 or stock sale.report_saleorder_document')
lines.append('  - store BARANI commercial ids in %s' % IDS_PARAMETER_KEY)
lines.append('')

if not APPLY:
    lines.append('DRY RUN COMPLETE: no writes performed.')
    lines.append('Set APPLY=True and CONFIRM=%s to apply.' % CONFIRM_TOKEN)
    raise UserError(NL.join(lines)[:90000])
if CONFIRM != CONFIRM_TOKEN:
    lines.append('ERROR: APPLY=True but CONFIRM does not match %s. Refusing.' % CONFIRM_TOKEN)
    raise UserError(NL.join(lines)[:90000])

try:
    env.cr.execute('SAVEPOINT sp_barani_commercial_install')

    paper_vals = {
        'name': PAPERFORMAT_NAME,
        'format': 'A4',
        'orientation': 'Portrait',
        'margin_top': margin_top,
        'margin_bottom': margin_bottom,
        'margin_left': margin_left,
        'margin_right': margin_right,
        'header_spacing': header_spacing,
        'header_line': False,
        'dpi': dpi,
    }
    if papers:
        paper = papers
        paper.write(paper_vals)
        lines.append('PASS: updated paperformat id=%s.' % paper.id)
    else:
        paper = Paper.create(paper_vals)
        lines.append('PASS: created paperformat id=%s.' % paper.id)

    # Create/update views. Backups are one-time per artifact key.
    view_specs = [
        [layout_views, LAYOUT_VIEW_NAME, LAYOUT_VIEW_KEY, LAYOUT_ARCH, 'layout'],
        [body_views, BODY_VIEW_NAME, BODY_VIEW_KEY, BODY_ARCH, 'body'],
        [sale_wrappers, SALE_WRAPPER_NAME, SALE_WRAPPER_KEY, SALE_WRAPPER_ARCH, 'sale_wrapper'],
        [pf_wrappers, PF_WRAPPER_NAME, PF_WRAPPER_KEY, PF_WRAPPER_ARCH, 'pf_wrapper'],
    ]
    made_views = []
    for vs in view_specs:
        existing = vs[0]
        vname = vs[1]
        vkey = vs[2]
        varch = vs[3]
        label = vs[4]
        backup_key = 'barani.commercial_report.backup.%s.arch' % label
        backup_marker = 'barani.commercial_report.backup.%s.marker' % label
        if existing:
            vv = existing
            if not Param.get_param(backup_marker, ''):
                Param.set_param(backup_key, vv.arch_db or '')
                Param.set_param(backup_marker, '1')
                lines.append('PASS: stored one-time backup for %s view in %s.' % (label, backup_key))
            else:
                lines.append('NOTE: backup marker already exists for %s; not overwriting backup.' % label)
            vv.write({'name': vname, 'key': vkey, 'type': 'qweb', 'arch_db': varch, 'inherit_id': False})
            lines.append('PASS: updated %s view id=%s key=%s.' % (label, vv.id, vkey))
        else:
            vv = View.create({'name': vname, 'key': vkey, 'type': 'qweb', 'arch_db': varch, 'inherit_id': False})
            lines.append('PASS: created %s view id=%s key=%s.' % (label, vv.id, vkey))
        made_views.append(vv)

    sale_report_vals = {
        'name': SALE_REPORT_NAME,
        'model': 'sale.order',
        'report_type': 'qweb-pdf',
        'report_name': SALE_REPORT_KEY,
        'report_file': SALE_REPORT_KEY,
        'binding_model_id': sale_model.id,
        'binding_type': 'report',
        'paperformat_id': paper.id,
        'print_report_name': SALE_PRINT_REPORT_NAME_EXPR,
    }
    if group_ids:
        sale_report_vals['groups_id'] = [(6, 0, group_ids)]
    if sale_reports:
        sale_report = sale_reports
        sale_report.write(sale_report_vals)
        lines.append('PASS: updated sale report action id=%s.' % sale_report.id)
    else:
        sale_report = Report.create(sale_report_vals)
        lines.append('PASS: created sale report action id=%s.' % sale_report.id)

    pf_report_vals = {
        'name': PF_REPORT_NAME,
        'model': 'sale.order',
        'report_type': 'qweb-pdf',
        'report_name': PF_REPORT_KEY,
        'report_file': PF_REPORT_KEY,
        'binding_model_id': sale_model.id,
        'binding_type': 'report',
        'paperformat_id': paper.id,
        'print_report_name': PF_PRINT_REPORT_NAME_EXPR,
    }
    if group_ids:
        pf_report_vals['groups_id'] = [(6, 0, group_ids)]
    if pf_reports:
        pf_report = pf_reports
        pf_report.write(pf_report_vals)
        lines.append('PASS: updated PF report action id=%s.' % pf_report.id)
    else:
        pf_report = Report.create(pf_report_vals)
        lines.append('PASS: created PF report action id=%s.' % pf_report.id)

    Param.set_param(IDS_PARAMETER_KEY, '%s,%s,%s,%s,%s,%s,%s' % (made_views[1].id, sale_report.id, pf_report.id, paper.id, made_views[0].id, made_views[2].id, made_views[3].id))
    lines.append('PASS: stored ids body,sale_report,pf_report,paper,layout,sale_wrapper,pf_wrapper in %s.' % IDS_PARAMETER_KEY)

    # Flush queued writes to the database BEFORE invalidating the cache.
    # v2.4 invalidated first; on the update path (existing views) the arch_db writes
    # are only queued, so invalidating first made the read-back flush fail with
    # "Could not find all values of ir.ui.view(...) to flush them". Flushing first
    # executes the writes inside the savepoint, then invalidation is safe.
    try:
        env.flush_all()
        env.invalidate_all()
    except AttributeError:
        View.flush_model()
        Report.flush_model()
        Paper.flush_model()
        env.cache.invalidate()
    lines.append('PASS: flushed pending writes, then invalidated ORM cache (order fixed).')

    # Read-back verification.
    check_layout = View.browse(made_views[0].id)
    check_body = View.browse(made_views[1].id)
    check_sale_wrapper = View.browse(made_views[2].id)
    check_pf_wrapper = View.browse(made_views[3].id)
    check_sale_report = Report.browse(sale_report.id)
    check_pf_report = Report.browse(pf_report.id)
    check_arch = (check_layout.arch_db or '') + (check_body.arch_db or '') + (check_sale_wrapper.arch_db or '') + (check_pf_wrapper.arch_db or '')
    if check_layout.inherit_id or check_body.inherit_id or check_sale_wrapper.inherit_id or check_pf_wrapper.inherit_id:
        raise Exception('one or more BARANI commercial views are inherited; expected standalone')
    if 'sale.report_saleorder_document' in check_arch or 'web.external_layout' in check_arch or 'account.document_tax_totals' in check_arch:
        raise Exception('forbidden t-call/reference found in BARANI commercial arch')
    if 'invoice_line_ids' in check_arch or 'move_type' in check_arch or 'amount_residual' in check_arch:
        raise Exception('account.move-only field leaked into BARANI commercial arch after write')
    if 'o_main_table' not in (check_body.arch_db or ''):
        raise Exception('invoice o_main_table layout missing from sale body after write')
    if 'product_id.hs_code' not in (check_body.arch_db or '') or 'country_of_origin.code' not in (check_body.arch_db or ''):
        raise Exception('HS/COO code fields missing from sale body')
    if RECEIVING_IBAN_CANON not in (check_body.arch_db or '') or RECEIVING_BIC_CANON not in (check_body.arch_db or '') or 'barani_bank_transfer_band' not in (check_body.arch_db or ''):
        raise Exception('PF payment bank band guard missing from sale body')
    if 'doc.env.context.get' in check_arch:
        raise Exception('record-context PF flags found in BARANI commercial arch; expected QWeb t-set variables')
    if "tax_id.mapped('description')" not in (check_body.arch_db or ''):
        raise Exception('VAT Rate column is not using account.tax.description')
    if not (check_sale_report.report_name == SALE_REPORT_KEY and check_sale_report.report_file == SALE_REPORT_KEY and check_sale_report.paperformat_id.id == paper.id):
        raise Exception('sale report action read-back failed')
    if not (check_pf_report.report_name == PF_REPORT_KEY and check_pf_report.report_file == PF_REPORT_KEY and check_pf_report.paperformat_id.id == paper.id):
        raise Exception('PF report action read-back failed')
    if group_ids:
        for gids_check in group_ids:
            if gids_check not in check_sale_report.groups_id.ids or gids_check not in check_pf_report.groups_id.ids:
                raise Exception('report action groups_id read-back failed')
    # Exact-equality read-back (stronger than markers): the stored arch_db must match
    # the installer arch byte-for-byte for every view. Catches any silent normalization
    # or partial write the marker checks above would miss. Any mismatch rolls back.
    rb_layout = check_layout.arch_db or ''
    rb_body = check_body.arch_db or ''
    rb_sale_wrapper = check_sale_wrapper.arch_db or ''
    rb_pf_wrapper = check_pf_wrapper.arch_db or ''
    lines.append('READ-BACK ARCH LENGTHS (stored/expected): layout=%s/%s body=%s/%s sale_wrapper=%s/%s pf_wrapper=%s/%s.' % (len(rb_layout), len(LAYOUT_ARCH), len(rb_body), len(BODY_ARCH), len(rb_sale_wrapper), len(SALE_WRAPPER_ARCH), len(rb_pf_wrapper), len(PF_WRAPPER_ARCH)))
    if rb_layout != LAYOUT_ARCH:
        raise Exception('read-back layout arch does not exactly equal installer layout arch')
    if rb_body != BODY_ARCH:
        raise Exception('read-back body arch does not exactly equal installer body arch')
    if rb_sale_wrapper != SALE_WRAPPER_ARCH:
        raise Exception('read-back sale wrapper arch does not exactly equal installer sale wrapper arch')
    if rb_pf_wrapper != PF_WRAPPER_ARCH:
        raise Exception('read-back PF wrapper arch does not exactly equal installer PF wrapper arch')
    lines.append('PASS: exact arch equality confirmed for layout, body, sale wrapper, and PF wrapper.')
    lines.append('PASS: read-back verification passed.')

    env.cr.execute('RELEASE SAVEPOINT sp_barani_commercial_install')
    lines.append('INSTALL COMPLETE.')
    lines.append('TEST: as a regular salesperson, Sales Manager, and Billing user if possible, verify Print -> %r and Print -> %r on one draft quotation and one confirmed sale order. The output now clones the VAT invoice layout (centered title, bordered 10-column table with VAT + VAT Base, INCOTERMS/fiscal notes, COO legend, Issued-by line, bank band on all three). Test the Pro-forma first: confirm the title reads "Pro-Forma Invoice", the red bank band shows IBAN + SWIFT/BIC, and the upper red Incoterm cell is absent while the lower INCOTERMS line remains.' % (SALE_REPORT_NAME, PF_REPORT_NAME))
    lines.append('HYGIENE: reset APPLY=False / CONFIRM="", or archive/delete this server action.')
except Exception as e_apply:
    try:
        env.cr.execute('ROLLBACK TO SAVEPOINT sp_barani_commercial_install')
        env.cr.execute('RELEASE SAVEPOINT sp_barani_commercial_install')
        lines.append('PASS: rolled back savepoint after failure.')
    except Exception as e_rb:
        lines.append('ROLLBACK PROBLEM: %s' % str(e_rb)[:500])
    lines.append('INSTALL FAILED: %s' % str(e_apply)[:1500])
    raise UserError(NL.join(lines)[:90000])

text = NL.join(lines)
Param.set_param(OUTPUT_PARAMETER_KEY, text)
param = Param.search([('key', '=', OUTPUT_PARAMETER_KEY)], limit=1)
action = {'type': 'ir.actions.act_window', 'name': ACTION_NAME, 'res_model': 'ir.config_parameter', 'view_mode': 'form', 'res_id': param.id, 'target': 'current'}
