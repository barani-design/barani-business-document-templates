# ============================================================================
# ACTION NAME : BARANI DELIVERY NOTE REPORT INSTALLER — DN L1 QR-only DDS-free
# MODEL       : Module (ir.module.module) or any model; selected records ignored.
# ACTION TO DO: Execute Python Code
# RUN BY      : Run APPLY=False first; then APPLY=True + CONFIRM='INSTALL_DELIVERY_NOTE_2026'.
# PURPOSE     : Additive standalone Delivery Note print option using the BARANI
#               RI/DPI 2026+ visual language. Does not modify Odoo stock delivery
#               templates, sale-order reports, quotation reports, or existing buttons.
#
# WHAT IT CREATES / UPDATES:
#   - standalone QWeb body view: barani_delivery.report_delivery_note_2026
#   - standalone custom layout view: barani_delivery.external_layout_delivery_2026
#   - report action on stock.picking: Delivery Note (DN) — 2026+
#   - dedicated paperformat: BARANI Delivery A4 7mm
#
# DN L1 PLAN:
#   - QR codes are kept ONLY on the Delivery Note and are generated from
#     product_id.barcode. No Q/SO/PF report is touched.
#   - Flat native stock.move table for L1. Kit grouping is deferred to DN L2
#     after real picking samples prove the sale_line/BoM grouping relation.
#   - No DDS Update Delivered Quantity replacement wizard; production confirmed
#     this DDS feature is not used.
#   - No accounting/tax/product/inventory data writes. No dds_ or brn_ fields.
#   - EORI is deliberately not printed from VAT. Add only after a real native
#     EORI field/source is confirmed.
#
# SAFE_EVAL: no import/def/with/eval/exec/open in executable script.
# ============================================================================

APPLY = False
CONFIRM = ''

DELIVERY_VIEW_KEY = 'barani_delivery.report_delivery_note_2026'
DELIVERY_VIEW_NAME = 'BARANI Delivery Note 2026 report body DN L1 QR-only DDS-free'
LAYOUT_VIEW_KEY = 'barani_delivery.external_layout_delivery_2026'
LAYOUT_VIEW_NAME = 'BARANI Delivery external layout 2026 (logo + right title)'
REPORT_NAME = 'Delivery Note (DN) — 2026+'
PAPERFORMAT_NAME = 'BARANI Delivery A4 7mm'
IDS_PARAMETER_KEY = 'barani.delivery_note_2026.ids'
OUTPUT_PARAMETER_KEY = 'barani.delivery_note_2026.install.last_run'
ARCH_BACKUP_KEY = 'barani.delivery_note_2026.pre_update_arch_backup'
ARCH_BACKUP_MARKER_KEY = 'barani.delivery_note_2026.pre_update_arch_backup.marker'
LAYOUT_BACKUP_KEY = 'barani.delivery_note_2026.pre_update_layout_arch_backup'
LAYOUT_BACKUP_MARKER_KEY = 'barani.delivery_note_2026.pre_update_layout_arch_backup.marker'
GROUP_STOCK_XMLID = 'stock.group_stock_user'
GROUP_SALES_XMLID = 'sales_team.group_sale_manager'
BOTTOM_MARGIN = 18.0

PRINT_REPORT_NAME_EXPR = "'DN ' + (object.name or '')"

LAYOUT_ARCH = '<t t-name="barani_delivery.external_layout_delivery_2026">\n    <t t-if="not o" t-set="o" t-value="doc"/>\n    <t t-if="not company">\n        <t t-if="company_id"><t t-set="company" t-value="company_id"/></t>\n        <t t-elif="o and o.company_id"><t t-set="company" t-value="o.company_id.sudo()"/></t>\n        <t t-else="else"><t t-set="company" t-value="res_company"/></t>\n    </t>\n    <div t-attf-class="header o_company_#{company.id}_layout" t-att-style="report_header_style">\n        <div style="position:relative; height:41px;">\n            <div style="float:left; width:35%; height:41px; line-height:41px; position:relative; z-index:10;">\n                <img t-if="company.logo" t-att-src="image_data_uri(company.logo)" style="max-height:41px; vertical-align:middle;" alt="Logo"/>\n            </div>\n            <div t-if="o and o._name == \'stock.picking\'" name="barani_delivery_doc_title_right" style="position:absolute; right:0; top:0; height:41px; line-height:41px; text-align:right; max-width:55%; z-index:15;">\n                <span style="font-size:13pt; font-weight:bold; white-space:nowrap; vertical-align:middle;">Delivery Note: <span t-field="o.name"/></span>\n            </div>\n            <div name="barani_top_title_divider" style="position:absolute; left:0; right:0; bottom:0; border-bottom:1px solid black; z-index:40;"/>\n            <div style="clear:both;"/>\n        </div>\n        <div class="row" style="margin-top:2px;">\n            <div class="col-6" name="company_address" style="font-size:10pt; line-height:1.25;">\n                <ul class="list-unstyled" style="margin-bottom:2px;">\n                    <li t-if="company.is_company_details_empty"><t t-esc="company.partner_id" t-options=\'{"widget": "contact", "fields": ["address", "name"], "no_marker": true}\'/></li>\n                    <li t-else=""><t t-esc="company.company_details"/></li>\n                </ul>\n            </div>\n            <div class="col-6" name="company_registration" style="font-size:10pt; line-height:1.25; padding-left:18px;">\n                <ul class="list-unstyled" style="margin-bottom:2px;">\n                    <li t-if="company.company_registry">ID: <span t-esc="company.company_registry"/></li>\n                    <li t-if="company.vat">Tax ID: <span t-esc="company.vat[2:] if (company.vat[:2] == \'SK\') else company.vat"/></li>\n                    <li t-if="company.vat">VAT: <span t-esc="company.vat"/></li>\n                </ul>\n            </div>\n        </div>\n        <div name="barani_seller_buyer_divider" style="border-bottom:1px solid black; width:100%; margin:1px 0 0 0;"/>\n    </div>\n\n    <div t-attf-class="article o_report_layout_standard o_company_#{company.id}_layout {{ \'o_report_layout_background\' if company.layout_background in [\'Geometric\', \'Custom\'] else \'\' }}" t-attf-style="background-image: url({{ \'data:image/png;base64,%s\' % company.layout_background_image.decode(\'utf-8\') if company.layout_background_image and company.layout_background == \'Custom\' else \'/base/static/img/bg_background_template.jpg\' if company.layout_background == \'Geometric\' else \'\' }});" t-att-data-oe-model="o and o._name" t-att-data-oe-id="o and o.id" t-att-data-oe-lang="o and o.env.context.get(\'lang\')">\n        <t t-out="0"/>\n    </div>\n\n    <div t-attf-class="footer o_standard_footer o_company_#{company.id}_layout">\n        <div class="text-center" style="border-top:1px solid black; font-size:8pt; line-height:1.1; padding-top:2px;">\n            <ul class="list-inline" style="margin:0 0 1px 0; padding:0;"><div t-field="company.report_footer"/></ul>\n            <div t-if="report_type == \'pdf\'" class="text-muted"><span class="page"/> of <span class="topage"/></div>\n            <div t-if="report_type == \'pdf\' and display_name_in_footer" class="text-muted"><span t-field="o.name"/></div>\n        </div>\n    </div>\n</t>'

DELIVERY_ARCH = '<t t-name="barani_delivery.report_delivery_note_2026">\n  <t t-call="web.html_container">\n    <t t-foreach="docs" t-as="o">\n      <t t-set="lang" t-value="(o.partner_id.lang or user.lang)"/>\n      <t t-call="barani_delivery.external_layout_delivery_2026" t-lang="lang">\n        <t t-set="o" t-value="o.with_context(lang=lang)"/>\n        <style>\n          .barani_delivery_doc { font-size:10pt; line-height:1.25; }\n          .barani_addr_block .barani_addr_cell { min-width:0; box-sizing:border-box; word-wrap:break-word; overflow-wrap:break-word; }\n          .barani_addr_block .barani_customer_cell { padding-left:0; padding-right:0; }\n          .barani_addr_block .barani_customer_cell.barani_has_shipping { padding-right:18px; }\n          .barani_addr_block .barani_shipping_cell { padding-left:18px; padding-right:0; }\n          .barani_delivery_table { table-layout:fixed; width:100%; font-size:9.5pt; line-height:1.2; }\n          .barani_delivery_table th, .barani_delivery_table td { padding:2px 3px; vertical-align:top; overflow:hidden; }\n          .barani_delivery_table .text-nowrap { white-space:nowrap; }\n          .barani_qr_img { width:42px; height:42px; }\n        </style>\n\n        <t t-set="barani_customer" t-value="o.sale_id.partner_invoice_id if (o.sale_id and o.sale_id.partner_invoice_id) else (o.sale_id.partner_id if (o.sale_id and o.sale_id.partner_id) else o.partner_id)"/>\n        <t t-set="barani_shipping" t-value="o.partner_id"/>\n        <t t-set="barani_has_shipping" t-value="barani_shipping and barani_customer and barani_shipping != barani_customer"/>\n\n        <div class="row barani_delivery_doc barani_addr_block" style="margin-top:0; margin-bottom:0;">\n          <div t-att-class="\'col-6 barani_addr_cell barani_customer_cell barani_has_shipping\' if barani_has_shipping else \'col-6 barani_addr_cell barani_customer_cell\'">\n            <strong>Customer</strong>\n            <div t-field="barani_customer" t-options=\'{"widget": "contact", "fields": ["address", "name"], "no_marker": true}\'/>\n            <div t-if="barani_customer.phone or barani_customer.mobile" class="mt-1">Tel: <span t-esc="barani_customer.phone or barani_customer.mobile"/></div>\n            <div t-if="barani_customer.company_registry" class="mt-1">ID: <span t-field="barani_customer.company_registry"/></div>\n            <div t-if="barani_customer.vat" class="mt-1">VAT: <span t-field="barani_customer.vat"/></div>\n          </div>\n          <div class="col-6 barani_addr_cell barani_shipping_cell" t-if="barani_has_shipping">\n            <strong>Shipping Address</strong>\n            <div t-field="barani_shipping" t-options=\'{"widget": "contact", "fields": ["address", "name"], "no_marker": true}\'/>\n            <div t-if="barani_shipping.phone or barani_shipping.mobile" class="mt-1">Tel: <span t-esc="barani_shipping.phone or barani_shipping.mobile"/></div>\n          </div>\n        </div>\n\n        <div class="page barani_delivery_doc">\n          <div id="informations" class="row mt-3" style="padding-top:4px; margin-bottom:8px;">\n            <div class="col-2 mb-2" t-if="o.scheduled_date"><strong>Scheduled Date</strong><p class="m-0" t-field="o.scheduled_date"/></div>\n            <div class="col-2 mb-2" t-if="o.date_done"><strong>Done Date</strong><p class="m-0" t-field="o.date_done"/></div>\n            <div class="col-2 mb-2" t-if="o.origin"><strong>Source Order</strong><p class="m-0" t-field="o.origin"/></div>\n            <div class="col-2 mb-2" t-if="o.picking_type_id"><strong>Operation</strong><p class="m-0" t-field="o.picking_type_id.name"/></div>\n            <div class="col-2 mb-2"><strong>Status</strong><p class="m-0"><span t-field="o.state"/></p></div>\n          </div>\n\n          <table class="table table-sm o_main_table barani_delivery_table" name="barani_delivery_line_table">\n            <colgroup>\n              <col style="width:7%"/>\n              <col style="width:37%"/>\n              <col style="width:9%"/>\n              <col style="width:6%"/>\n              <col style="width:13%"/>\n              <col style="width:9%"/>\n              <col style="width:9%"/>\n              <col style="width:10%"/>\n            </colgroup>\n            <thead>\n              <tr>\n                <th class="text-center"><span>QR</span></th>\n                <th class="text-start"><span>Description</span></th>\n                <th class="text-start"><span>HS Code</span></th>\n                <th class="text-center"><span>COO</span></th>\n                <th class="text-start"><span>Lot / Serial</span></th>\n                <th class="text-end"><span>Ordered</span></th>\n                <th class="text-end"><span>Delivered</span></th>\n                <th class="text-start"><span>Unit</span></th>\n              </tr>\n            </thead>\n            <tbody>\n              <t t-foreach="o.move_ids_without_package" t-as="move">\n                <tr t-if="move.product_id and move.state != \'cancel\' and (move.product_uom_qty or move.quantity_done)">\n                  <td class="text-center">\n                    <img t-if="move.product_id.barcode" class="barani_qr_img" t-att-src="\'/report/barcode/?barcode_type=%s&amp;value=%s&amp;width=%s&amp;height=%s\' % (\'QR\', move.product_id.barcode, 140, 140)"/>\n                  </td>\n                  <td>\n                    <strong t-if="move.product_id.default_code">[<span t-field="move.product_id.default_code"/>] </strong><span t-esc="move.description_picking or move.product_id.display_name"/>\n                    <div t-if="move.product_id.barcode" class="text-muted" style="font-size:8pt;">Barcode: <span t-field="move.product_id.barcode"/></div>\n                  </td>\n                  <td class="text-start"><span t-if="move.product_id.hs_code" t-field="move.product_id.hs_code"/></td>\n                  <td class="text-center"><span t-if="move.product_id.country_of_origin" t-field="move.product_id.country_of_origin.code"/></td>\n                  <td class="text-start"><span t-esc="\', \'.join(move.move_line_ids.filtered(lambda ml: ml.lot_id).mapped(\'lot_id.name\'))"/></td>\n                  <td class="text-end"><span t-field="move.product_uom_qty"/></td>\n                  <td class="text-end"><span t-field="move.quantity_done"/></td>\n                  <td class="text-start"><span t-field="move.product_uom" groups="uom.group_uom"/></td>\n                </tr>\n              </t>\n            </tbody>\n          </table>\n\n          <p class="text-muted" style="font-size:8pt; margin-top:6px;">COO = Country of Origin. QR codes encode the product barcode for delivery-note scanning only.</p>\n\n          <div name="barani_delivery_receipt_band" style="display:table; width:100%; table-layout:fixed; background-color:#E79C9C; font-size:9pt; line-height:1.2; margin-top:12px;">\n            <div style="display:table-cell; width:33.33%; text-align:left; vertical-align:top; padding:6px;"><strong>Received by:</strong></div>\n            <div style="display:table-cell; width:33.33%; text-align:center; vertical-align:top; padding:6px;"><strong>Date:</strong></div>\n            <div style="display:table-cell; width:33.33%; text-align:right; vertical-align:top; padding:6px;"><strong>Signature:</strong></div>\n          </div>\n\n          <div class="mt-3" style="font-size:9pt;">\n            <strong>Prepared by / Issued by:</strong> <span t-field="o.create_uid.name"/>\n          </div>\n        </div>\n      </t>\n    </t>\n  </t>\n</t>'

View = env['ir.ui.view'].sudo()
Report = env['ir.actions.report'].sudo()
Model = env['ir.model'].sudo()
Param = env['ir.config_parameter'].sudo()
Paper = env['report.paperformat'].sudo()
Ref = env.ref
lines = []
lines.append('BARANI DELIVERY NOTE REPORT INSTALLER — DN L1 QR-only DDS-free')
lines.append('APPLY=%s CONFIRM=%s' % (APPLY, CONFIRM))
lines.append('Scope: additive standalone stock.picking report; sale/Q/SO/PF and existing delivery-slip reports untouched.')
lines.append('body arch length=%s chars | layout arch length=%s chars' % (len(DELIVERY_ARCH), len(LAYOUT_ARCH)))
lines.append('')

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
            env.invalidate_all(); cache_inv_method = 'env.invalidate_all'
        except Exception:
            try:
                env.cache.invalidate(); cache_inv_method = 'env.cache.invalidate'
            except Exception:
                cache_inv_method = ''
        if cache_inv_method:
            env.cr.execute('SELECT 1')
            manual_sp_ok = True
            lines.append('PASS: SAVEPOINT recovery works; cache method=%s' % cache_inv_method)
except Exception as e0:
    lines.append('FATAL TEST 0: %s' % str(e0)[:500])
if not manual_sp_ok:
    raise UserError('\n'.join(lines)[:90000])
lines.append('')

lines.append('TEMPLATE SELF-CHECK')
checks = [
    ('stock picking docs wrapper', 't-foreach="docs"' in DELIVERY_ARCH and 'web.html_container' in DELIVERY_ARCH),
    ('custom layout call', 'barani_delivery.external_layout_delivery_2026' in DELIVERY_ARCH),
    ('right-side title only', 'barani_delivery_doc_title_right' in LAYOUT_ARCH and 'barani_center_doc_title' not in LAYOUT_ARCH),
    ('EORI not spoofed from VAT', 'EORI:' not in LAYOUT_ARCH),
    ('address wrap/padding', 'barani_customer_cell' in DELIVERY_ARCH and 'barani_shipping_cell' in DELIVERY_ARCH and 'overflow-wrap' in DELIVERY_ARCH),
    ('product QR column for DN only', 'barcode_type=%s' in DELIVERY_ARCH and "'QR'" in DELIVERY_ARCH and 'move.product_id.barcode' in DELIVERY_ARCH),
    ('delivery table', 'barani_delivery_line_table' in DELIVERY_ARCH and 'Delivered' in DELIVERY_ARCH),
    ('HS/COO fields', 'hs_code' in DELIVERY_ARCH and 'country_of_origin' in DELIVERY_ARCH),
    ('receipt/signature band', 'barani_delivery_receipt_band' in DELIVERY_ARCH and 'Received by:' in DELIVERY_ARCH),
    ('no invoice-only money fields', 'Unit Price' not in DELIVERY_ARCH and 'Total incl. VAT' not in DELIVERY_ARCH and 'IBAN' not in DELIVERY_ARCH and 'Payment Ref' not in DELIVERY_ARCH),
    ('no DDS or brn dependencies', 'dds_' not in DELIVERY_ARCH and 'brn_' not in DELIVERY_ARCH and 'dds_' not in LAYOUT_ARCH and 'brn_' not in LAYOUT_ARCH),
]
self_error = False
for c in checks:
    lines.append('  %s: %s' % (c[0], 'PASS' if c[1] else 'FAIL'))
    if not c[1]:
        self_error = True
if self_error:
    lines.append('ERROR: template self-check failed.')
    raise UserError('\n'.join(lines)[:90000])
lines.append('')

lines.append('FIELD PREFLIGHT')
field_error = False
field_checks = [
    ('stock.picking', ['name','partner_id','scheduled_date','date_done','origin','picking_type_id','move_ids_without_package','state','company_id','sale_id','create_uid']),
    ('stock.move', ['product_id','description_picking','product_uom_qty','quantity_done','product_uom','move_line_ids','state']),
    ('stock.move.line', ['lot_id','product_id']),
    ('product.product', ['barcode','default_code','hs_code','country_of_origin']),
]
for fc in field_checks:
    model_name = fc[0]
    fields = fc[1]
    if model_name not in env:
        lines.append('  MODEL MISSING: %s' % model_name)
        field_error = True
    else:
        flds = env[model_name]._fields
        missing = []
        for fname in fields:
            if fname not in flds:
                missing.append(fname)
        if missing:
            lines.append('  %s: MISSING %s' % (model_name, ', '.join(missing)))
            field_error = True
        else:
            lines.append('  %s: PASS' % model_name)
if field_error:
    lines.append('ERROR: required fields missing. Run the read-only probe and adapt the template before installing.')
    raise UserError('\n'.join(lines)[:90000])
lines.append('')

picking_model = Model.search([('model', '=', 'stock.picking')], limit=1)
if not picking_model:
    lines.append('ERROR: ir.model stock.picking not found. Install Inventory first.')
    raise UserError('\n'.join(lines)[:90000])

existing_view = View.search([('key', '=', DELIVERY_VIEW_KEY)])
existing_layout = View.search([('key', '=', LAYOUT_VIEW_KEY)])
existing_report_by_name = Report.search([('name', '=', REPORT_NAME)])
existing_report_by_tech = Report.search([('report_name', '=', DELIVERY_VIEW_KEY), ('model', '=', 'stock.picking')])
existing_reports = existing_report_by_tech
for rr in existing_report_by_name:
    if rr.id not in existing_reports.ids:
        existing_reports = existing_reports | rr
existing_report = existing_reports
existing_paper = Paper.search([('name', '=', PAPERFORMAT_NAME)])
lines.append('DISCOVERY')
lines.append('  body views with key:      %s' % len(existing_view))
lines.append('  layout views with key:    %s' % len(existing_layout))
lines.append('  reports with technical:   %s' % len(existing_report_by_tech))
lines.append('  reports with name:        %s' % len(existing_report_by_name))
lines.append('  merged report candidates: %s' % len(existing_report))
lines.append('  papers with name:         %s' % len(existing_paper))

if len(existing_view) > 1 or len(existing_layout) > 1 or len(existing_report) > 1 or len(existing_paper) > 1:
    lines.append('ERROR: duplicate BARANI delivery artifacts found. Refusing.')
    raise UserError('\n'.join(lines)[:90000])

collision = False
if existing_view and (existing_view.type != 'qweb' or existing_view.inherit_id):
    collision = True; lines.append('COLLISION: body view is not standalone qweb.')
if existing_layout and (existing_layout.type != 'qweb' or existing_layout.inherit_id):
    collision = True; lines.append('COLLISION: layout view is not standalone qweb.')
if existing_report and not (existing_report.model == 'stock.picking' and existing_report.report_type == 'qweb-pdf'):
    collision = True; lines.append('COLLISION: report identity mismatch.')
if existing_paper:
    paper_users = Report.search([('paperformat_id', '=', existing_paper.id)])
    other_users = 0
    for rr in paper_users:
        if not existing_report or rr.id != existing_report.id:
            other_users = other_users + 1
    if other_users:
        collision = True; lines.append('COLLISION: paperformat used by other report(s).')
if collision:
    raise UserError('\n'.join(lines)[:90000])
lines.append('PASS: duplicate/collision/ownership checks passed.')

stock_group = Ref(GROUP_STOCK_XMLID, raise_if_not_found=False)
sales_group = Ref(GROUP_SALES_XMLID, raise_if_not_found=False)
group_ids = []
if stock_group:
    group_ids.append(stock_group.id); lines.append('Stock/User group resolved: %s id=%s.' % (GROUP_STOCK_XMLID, stock_group.id))
else:
    lines.append('WARNING: stock group not found; report group restriction may be incomplete.')
if sales_group:
    group_ids.append(sales_group.id); lines.append('Sales/Administrator group resolved: %s id=%s.' % (GROUP_SALES_XMLID, sales_group.id))
lines.append('')

good_spacing = 35.0
good_top = 40.0
src_desc = 'fallback 40mm top / 35 spacing'
if env.company and env.company.paperformat_id:
    good_spacing = env.company.paperformat_id.header_spacing or good_spacing
    good_top = env.company.paperformat_id.margin_top or good_top
    src_desc = 'company default paper %r' % env.company.paperformat_id.name
lines.append('PAPERFORMAT PLAN')
lines.append('  source: %s' % src_desc)
lines.append('  margin_top=%s margin_bottom=%s margin_left=7 margin_right=7 header_spacing=%s dpi=90' % (good_top, BOTTOM_MARGIN, good_spacing))
lines.append('')
lines.append('PLAN')
lines.append('  - create/update standalone QWeb body view key=%s' % DELIVERY_VIEW_KEY)
lines.append('  - create/update standalone custom layout key=%s' % LAYOUT_VIEW_KEY)
lines.append('  - create/update ir.actions.report name=%r on stock.picking' % REPORT_NAME)
lines.append('  - add as separate Print option; stock/Odoo delivery reports untouched')
lines.append('  - QR codes render from product_id.barcode in the delivery-note line table only')
lines.append('  - DN L1 prints a flat native picking/move table; kit grouping is deferred to DN L2')
lines.append('  - no DDS Update Delivered Quantity replacement wizard is created')
lines.append('  - store ids in %s as body,report,paper,layout' % IDS_PARAMETER_KEY)
lines.append('')

if not APPLY:
    lines.append('DRY RUN COMPLETE: no writes performed.')
    lines.append("Set APPLY=True and CONFIRM='INSTALL_DELIVERY_NOTE_2026' to apply.")
    raise UserError('\n'.join(lines)[:90000])
if CONFIRM != 'INSTALL_DELIVERY_NOTE_2026':
    lines.append('ERROR: APPLY=True but CONFIRM is not INSTALL_DELIVERY_NOTE_2026. Refusing.')
    raise UserError('\n'.join(lines)[:90000])

lines.append('APPLY DELIVERY NOTE REPORT')
try:
    env.cr.execute('SAVEPOINT sp_barani_delivery_2026_install')
    paper_vals = {'name': PAPERFORMAT_NAME, 'format': 'A4', 'orientation': 'Portrait', 'margin_top': good_top, 'margin_bottom': BOTTOM_MARGIN, 'margin_left': 7.0, 'margin_right': 7.0, 'header_spacing': good_spacing, 'header_line': False, 'dpi': 90}
    if existing_paper:
        paper = existing_paper; paper.write(paper_vals); lines.append('PASS: updated paperformat id=%s.' % paper.id)
    else:
        paper = Paper.create(paper_vals); lines.append('PASS: created paperformat id=%s.' % paper.id)

    if existing_layout:
        layout = existing_layout
        if not Param.get_param(LAYOUT_BACKUP_MARKER_KEY, ''):
            Param.set_param(LAYOUT_BACKUP_KEY, layout.arch_db or '')
            Param.set_param(LAYOUT_BACKUP_MARKER_KEY, '1')
            lines.append('PASS: stored one-time previous layout backup.')
        layout.write({'name': LAYOUT_VIEW_NAME, 'key': LAYOUT_VIEW_KEY, 'type': 'qweb', 'inherit_id': False, 'arch_db': LAYOUT_ARCH})
        lines.append('PASS: updated layout view id=%s.' % layout.id)
    else:
        layout = View.create({'name': LAYOUT_VIEW_NAME, 'key': LAYOUT_VIEW_KEY, 'type': 'qweb', 'arch_db': LAYOUT_ARCH})
        lines.append('PASS: created layout view id=%s.' % layout.id)

    if existing_view:
        body = existing_view
        if not Param.get_param(ARCH_BACKUP_MARKER_KEY, ''):
            Param.set_param(ARCH_BACKUP_KEY, body.arch_db or '')
            Param.set_param(ARCH_BACKUP_MARKER_KEY, '1')
            lines.append('PASS: stored one-time previous body backup.')
        body.write({'name': DELIVERY_VIEW_NAME, 'key': DELIVERY_VIEW_KEY, 'type': 'qweb', 'inherit_id': False, 'arch_db': DELIVERY_ARCH})
        lines.append('PASS: updated body view id=%s.' % body.id)
    else:
        body = View.create({'name': DELIVERY_VIEW_NAME, 'key': DELIVERY_VIEW_KEY, 'type': 'qweb', 'arch_db': DELIVERY_ARCH})
        lines.append('PASS: created body view id=%s.' % body.id)

    report_vals = {'name': REPORT_NAME, 'model': 'stock.picking', 'report_type': 'qweb-pdf', 'report_name': DELIVERY_VIEW_KEY, 'report_file': DELIVERY_VIEW_KEY, 'binding_model_id': picking_model.id, 'binding_type': 'report', 'paperformat_id': paper.id, 'print_report_name': PRINT_REPORT_NAME_EXPR}
    if group_ids:
        report_vals['groups_id'] = [(6, 0, group_ids)]
    if existing_report:
        report = existing_report; report.write(report_vals); lines.append('PASS: updated report id=%s.' % report.id)
    else:
        report = Report.create(report_vals); lines.append('PASS: created report id=%s.' % report.id)

    Param.set_param(IDS_PARAMETER_KEY, '%s,%s,%s,%s' % (body.id, report.id, paper.id, layout.id))
    if cache_inv_method == 'env.invalidate_all':
        env.invalidate_all()
    else:
        env.cache.invalidate()
    lines.append('PASS: stored ids and invalidated cache.')

    check_body = View.browse(body.id)
    check_layout = View.browse(layout.id)
    check_report = Report.browse(report.id)
    if check_body.key != DELIVERY_VIEW_KEY or 'barani_delivery_line_table' not in (check_body.arch_db or '') or 'barcode_type=%s' not in (check_body.arch_db or '') or 'EORI:' in (check_layout.arch_db or ''):
        raise Exception('body/layout read-back failed')
    if check_layout.key != LAYOUT_VIEW_KEY or 'barani_delivery_doc_title_right' not in (check_layout.arch_db or ''):
        raise Exception('layout read-back failed')
    if check_report.report_name != DELIVERY_VIEW_KEY or check_report.model != 'stock.picking' or check_report.paperformat_id.id != paper.id:
        raise Exception('report read-back failed')
    lines.append('PASS: read-back verification passed.')
    env.cr.execute('RELEASE SAVEPOINT sp_barani_delivery_2026_install')
    lines.append('INSTALL COMPLETE. Test: open a Delivery Order -> Print -> %r.' % REPORT_NAME)
    lines.append('HYGIENE: reset APPLY=False / CONFIRM="", or archive/delete this server action.')
except Exception as e_apply:
    try:
        env.cr.execute('ROLLBACK TO SAVEPOINT sp_barani_delivery_2026_install')
        env.cr.execute('RELEASE SAVEPOINT sp_barani_delivery_2026_install')
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
action = {'type': 'ir.actions.act_window', 'name': REPORT_NAME, 'res_model': 'ir.config_parameter', 'view_mode': 'form', 'res_id': param.id, 'target': 'current'}
