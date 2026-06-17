# ============================================================================
# ACTION NAME : BARANI Picking Operations 2026+ FINAL installer v4.0 APPLY-SAFE
# RUN BY      : DRY_RUN=True first; then DRY_RUN=False + CONFIRM='INSTALL_BARANI_PICKING_OPERATIONS_2026_FINAL'.
# PURPOSE     : Cumulative clean installer for Picking Operations — 2026+.
# WRITE SCOPE : BARANI-owned QWeb views, report action, paperformat, config params only.
# DDS/BRN     : No dds_ or brn_ dependencies. No business data writes.
# RECONCILED  : v4 package re-homed to repo taxonomy; safe v3 apply/readback logic retained.
# ============================================================================
ACTION_NAME='BARANI Picking Operations 2026+ FINAL installer v4.0 APPLY-SAFE'
DRY_RUN=True
CONFIRM=''
CONFIRM_TOKEN='INSTALL_BARANI_PICKING_OPERATIONS_2026_FINAL'
OUTPUT_MODE='paged'
PAGE=1
PAGE_SIZE=15000
OUTPUT_PARAMETER_KEY='barani.picking_operations_2026.final_installer.last_run'
BODY_KEY='barani_delivery.report_picking_operations_2026'; LAYOUT_KEY='barani_delivery.external_layout_picking_operations_2026'; REPORT_NAME='Picking Operations — 2026+'; PAPER_NAME='BARANI Picking Operations A4 7mm'; IDS_PARAMETER_KEY='barani.picking_operations_2026.ids'
BODY_ARCH='<t t-name="barani_delivery.report_picking_operations_2026">\n  <t t-call="web.html_container">\n    <t t-foreach="docs" t-as="o">\n      <t t-set="lang" t-value="(o.partner_id.lang or user.lang)"/>\n      <t t-call="barani_delivery.external_layout_picking_operations_2026" t-lang="lang">\n        <t t-set="o" t-value="o.with_context(lang=lang)"/>\n        <t t-set="barani_pickops_v43_marker" t-value="\'notes_contact_prepared_by_no_grouping_v43|pickops_remove_duplicate_doc_number_v44_addrlabels_31\'"/>\n        <style>\n          .barani_pick_ops_doc { font-size:10pt; line-height:1.22; }\n          .barani_pick_ops_meta { margin:6px 0 8px 0; }\n          .barani_pick_ops_table { table-layout:fixed; width:100%; font-size:9pt; line-height:1.12; }\n          .barani_pick_ops_table th { padding:2px 3px; vertical-align:top; color:#ed1c24; border-bottom:1px solid #444; }\n          .barani_pick_ops_table td { padding:2px 3px; vertical-align:top; border-bottom:1px solid #ddd; overflow:hidden; }\n          .barani_pick_ops_product { overflow-wrap:anywhere; word-wrap:break-word; }\n          .barani_pick_ops_small { font-size:7.5pt; line-height:1.05; color:#666; }\n          .barani_pick_ops_barcode { max-width:100%; height:32px; }\n          .barani_pick_ops_serial_barcode { max-width:100%; height:32px; }\n          .barani_pick_ops_doc_barcode { max-width:230px; height:45px; }\n          .barani_pick_ops_warn { margin-top:4px; font-size:8.5pt; line-height:1.15; color:#8a5a00; }\n          .barani_pick_ops_note_row td { font-size:8.5pt; line-height:1.15; font-style:italic; background-color:#fafafa; color:#333; }\n          .barani_pick_ops_general_notes { font-size:8.5pt; line-height:1.15; margin:4px 0 3px 0; }\n          .barani_pick_ops_general_notes p { margin:0 0 2px 0; }\n          .barani_pick_ops_general_notes div { margin:0 0 2px 0; }\n          .barani_pick_ops_prepared { font-size:8.5pt; line-height:1.15; margin:4px 0 2px 0; }\n          .barani_pick_ops_addr_title { color:#ed1c24; font-weight:bold; }\n        </style>\n\n        <div class="page barani_pick_ops_doc">\n          <div class="row" style="margin-bottom:6px;">\n            <div class="col-7">\n              <strong class="barani_pick_ops_addr_title">Delivery Address:</strong>\n              <div t-field="o.partner_id" t-options="{&quot;widget&quot;: &quot;contact&quot;, &quot;fields&quot;: [&quot;address&quot;, &quot;name&quot;], &quot;no_marker&quot;: true}"/>\n              <div t-if="o.partner_id.phone or o.partner_id.mobile"><span>Tel: </span><span t-esc="o.partner_id.phone or o.partner_id.mobile"/></div>\n              <div t-if="o.partner_id.email"><span>Email: </span><span t-esc="o.partner_id.email"/></div>\n              <t t-set="barani_pickops_id_partner" t-value="o.partner_id if o.partner_id.company_registry else o.partner_id.commercial_partner_id"/>\n              <t t-set="barani_pickops_vat_partner" t-value="o.partner_id if o.partner_id.vat else o.partner_id.commercial_partner_id"/>\n              <div t-if="barani_pickops_id_partner and barani_pickops_id_partner.company_registry"><span>ID: </span><span t-esc="barani_pickops_id_partner.company_registry"/></div>\n              <div t-if="barani_pickops_vat_partner and barani_pickops_vat_partner.vat"><span>VAT: </span><span t-esc="barani_pickops_vat_partner.vat"/></div>\n            </div>\n            <div class="col-5 text-end">\n              <img t-if="o.name" class="barani_pick_ops_doc_barcode" t-att-src="\'/report/barcode/?barcode_type=%s&amp;value=%s&amp;width=%s&amp;height=%s&amp;humanreadable=1\' % (\'Code128\', o.name, 520, 80)"/>\n            </div>\n          </div>\n\n          <div class="row barani_pick_ops_meta">\n            <div class="col-3"><strong>Order:</strong><br/><span t-esc="o.origin or (o.sale_id.name if o.sale_id else \'\')"/></div>\n            <div class="col-3"><strong>Status:</strong><br/><span t-field="o.state"/></div>\n            <div class="col-3"><strong>Scheduled Date:</strong><br/><span t-field="o.scheduled_date"/></div>\n            <div class="col-3"><strong>Source Location:</strong><br/><span t-field="o.location_id.display_name"/></div>\n          </div>\n\n          <table class="table table-sm barani_pick_ops_table" name="barani_picking_operations_2026_table">\n            <colgroup>\n              <col name="barani_pick_ops_product_col_v43" style="width:34%"/>\n              <col style="width:8%"/>\n              <col name="barani_pick_ops_from_col_v43" style="width:15%"/>\n              <col name="barani_pick_ops_lot_barcode_col_v43" style="width:23%"/>\n              <col name="barani_pick_ops_product_barcode_col_v43" style="width:20%"/>\n            </colgroup>\n            <thead>\n              <tr>\n                <th class="text-start">Product</th>\n                <th class="text-end">Qty</th>\n                <th class="text-start">From</th>\n                <th class="text-center">Lot / Serial Barcode</th>\n                <th class="text-center">Product Barcode</th>\n              </tr>\n            </thead>\n            <tbody>\n              <t t-if="o.sale_id">\n                <t t-foreach="o.sale_id.order_line" t-as="barani_sol">\n                  <tr t-if="barani_sol.display_type == \'line_note\' and barani_sol.name" class="barani_pick_ops_note_row">\n                    <td colspan="5"><span t-field="barani_sol.name" t-options="{&quot;widget&quot;: &quot;text&quot;}"/></td>\n                  </tr>\n                  <t t-if="not barani_sol.display_type">\n                    <t t-foreach="o.move_ids_without_package" t-as="move">\n                      <t t-if="move.sale_line_id and move.sale_line_id.id == barani_sol.id and move.state != \'cancel\' and move.product_id">\n                        <t t-if="move.move_line_ids">\n                          <t t-foreach="move.move_line_ids" t-as="ml">\n                            <t t-set="barani_line_qty" t-value="(ml.qty_done or 0.0) if ((ml.qty_done or 0.0) &gt; 0.0) else (ml.reserved_uom_qty or 0.0)"/>\n                            <t t-set="barani_line_lot" t-value="ml.lot_id.name if ml.lot_id else \'\'"/>\n                            <tr>\n                              <td class="barani_pick_ops_product">\n                                <span t-field="ml.product_id.display_name"/>\n                                <div t-if="ml.product_id.default_code" class="barani_pick_ops_small">Internal Ref: <span t-field="ml.product_id.default_code"/></div>\n                              </td>\n                              <td class="text-end"><span t-esc="barani_line_qty" t-options="{&quot;widget&quot;: &quot;float&quot;, &quot;precision&quot;: 2}"/> <span t-field="ml.product_uom_id"/></td>\n                              <td><span t-field="ml.location_id.display_name"/></td>\n                              <td class="text-center">\n                                <t t-if="barani_line_lot">\n                                  <img class="barani_pick_ops_serial_barcode" t-att-src="\'/report/barcode/?barcode_type=%s&amp;value=%s&amp;width=%s&amp;height=%s&amp;humanreadable=1\' % (\'Code128\', barani_line_lot, 300, 70)"/>\n                                  <div class="barani_pick_ops_small"><span t-esc="barani_line_lot"/></div>\n                                </t>\n                                <t t-elif="ml.product_id.tracking != \'none\'"><span class="barani_pick_ops_small">Not assigned</span></t>\n                              </td>\n                              <td class="text-center">\n                                <img t-if="ml_index == 0 and ml.product_id.barcode" class="barani_pick_ops_barcode" t-att-src="\'/report/barcode/?barcode_type=%s&amp;value=%s&amp;width=%s&amp;height=%s&amp;humanreadable=1\' % (\'Code128\', ml.product_id.barcode, 300, 70)"/>\n                                <div t-if="ml_index == 0 and ml.product_id.barcode" class="barani_pick_ops_small"><span t-field="ml.product_id.barcode"/></div>\n                              </td>\n                            </tr>\n                          </t>\n                        </t>\n                        <t t-if="not move.move_line_ids">\n                          <tr>\n                            <td class="barani_pick_ops_product">\n                              <span t-field="move.product_id.display_name"/>\n                              <div t-if="move.product_id.default_code" class="barani_pick_ops_small">Internal Ref: <span t-field="move.product_id.default_code"/></div>\n                            </td>\n                            <td class="text-end"><span t-field="move.product_uom_qty"/> <span t-field="move.product_uom"/></td>\n                            <td><span t-field="move.location_id.display_name"/></td>\n                            <td class="text-center"><t t-if="move.product_id.tracking != \'none\'"><span class="barani_pick_ops_small">Not assigned</span></t></td>\n                            <td class="text-center">\n                              <img t-if="move.product_id.barcode" class="barani_pick_ops_barcode" t-att-src="\'/report/barcode/?barcode_type=%s&amp;value=%s&amp;width=%s&amp;height=%s&amp;humanreadable=1\' % (\'Code128\', move.product_id.barcode, 300, 70)"/>\n                              <div t-if="move.product_id.barcode" class="barani_pick_ops_small"><span t-field="move.product_id.barcode"/></div>\n                            </td>\n                          </tr>\n                        </t>\n                      </t>\n                    </t>\n                  </t>\n                </t>\n              </t>\n\n              <t t-foreach="o.move_ids_without_package" t-as="move">\n                <t t-if="((not o.sale_id) or (not move.sale_line_id) or (move.sale_line_id.order_id and o.sale_id and move.sale_line_id.order_id.id != o.sale_id.id)) and move.state != \'cancel\' and move.product_id">\n                  <t t-if="move.move_line_ids">\n                    <t t-foreach="move.move_line_ids" t-as="ml">\n                      <t t-set="barani_line_qty" t-value="(ml.qty_done or 0.0) if ((ml.qty_done or 0.0) &gt; 0.0) else (ml.reserved_uom_qty or 0.0)"/>\n                      <t t-set="barani_line_lot" t-value="ml.lot_id.name if ml.lot_id else \'\'"/>\n                      <tr>\n                        <td class="barani_pick_ops_product">\n                          <span t-field="ml.product_id.display_name"/>\n                          <div t-if="ml.product_id.default_code" class="barani_pick_ops_small">Internal Ref: <span t-field="ml.product_id.default_code"/></div>\n                        </td>\n                        <td class="text-end"><span t-esc="barani_line_qty" t-options="{&quot;widget&quot;: &quot;float&quot;, &quot;precision&quot;: 2}"/> <span t-field="ml.product_uom_id"/></td>\n                        <td><span t-field="ml.location_id.display_name"/></td>\n                        <td class="text-center">\n                          <t t-if="barani_line_lot">\n                            <img class="barani_pick_ops_serial_barcode" t-att-src="\'/report/barcode/?barcode_type=%s&amp;value=%s&amp;width=%s&amp;height=%s&amp;humanreadable=1\' % (\'Code128\', barani_line_lot, 300, 70)"/>\n                            <div class="barani_pick_ops_small"><span t-esc="barani_line_lot"/></div>\n                          </t>\n                          <t t-elif="ml.product_id.tracking != \'none\'"><span class="barani_pick_ops_small">Not assigned</span></t>\n                        </td>\n                        <td class="text-center">\n                          <img t-if="ml_index == 0 and ml.product_id.barcode" class="barani_pick_ops_barcode" t-att-src="\'/report/barcode/?barcode_type=%s&amp;value=%s&amp;width=%s&amp;height=%s&amp;humanreadable=1\' % (\'Code128\', ml.product_id.barcode, 300, 70)"/>\n                          <div t-if="ml_index == 0 and ml.product_id.barcode" class="barani_pick_ops_small"><span t-field="ml.product_id.barcode"/></div>\n                        </td>\n                      </tr>\n                    </t>\n                  </t>\n                  <t t-if="not move.move_line_ids">\n                    <tr>\n                      <td class="barani_pick_ops_product">\n                        <span t-field="move.product_id.display_name"/>\n                        <div t-if="move.product_id.default_code" class="barani_pick_ops_small">Internal Ref: <span t-field="move.product_id.default_code"/></div>\n                      </td>\n                      <td class="text-end"><span t-field="move.product_uom_qty"/> <span t-field="move.product_uom"/></td>\n                      <td><span t-field="move.location_id.display_name"/></td>\n                      <td class="text-center"><t t-if="move.product_id.tracking != \'none\'"><span class="barani_pick_ops_small">Not assigned</span></t></td>\n                      <td class="text-center">\n                        <img t-if="move.product_id.barcode" class="barani_pick_ops_barcode" t-att-src="\'/report/barcode/?barcode_type=%s&amp;value=%s&amp;width=%s&amp;height=%s&amp;humanreadable=1\' % (\'Code128\', move.product_id.barcode, 300, 70)"/>\n                        <div t-if="move.product_id.barcode" class="barani_pick_ops_small"><span t-field="move.product_id.barcode"/></div>\n                      </td>\n                    </tr>\n                  </t>\n                </t>\n              </t>\n            </tbody>\n          </table>\n\n          <t t-set="barani_pickops_missing_tracked" t-value="False"/>\n          <t t-foreach="o.move_ids_without_package" t-as="barani_warn_move">\n            <t t-if="barani_warn_move.product_id and barani_warn_move.product_id.tracking != \'none\' and not barani_warn_move.move_line_ids">\n              <t t-set="barani_pickops_missing_tracked" t-value="True"/>\n            </t>\n          </t>\n          <div class="barani_pick_ops_warn" t-if="barani_pickops_missing_tracked">\n            ⚠ Some tracked products have no assigned lot/serial lines. Click <strong>Check Availability</strong> before printing the final picking list.\n          </div>\n          <div class="barani_pick_ops_warn" t-if="o.state not in (\'assigned\', \'done\')">\n            ⚠ This transfer is not Ready/Done. Reservations or serial numbers may be incomplete.\n          </div>\n\n          <div name="barani_pickops_general_notes" t-if="o.sale_id and not is_html_empty(o.sale_id.note)" class="barani_pick_ops_general_notes">\n            <strong>Notes:</strong>\n            <div style="margin-top:2px;" t-field="o.sale_id.note"/>\n          </div>\n\n          <t t-set="barani_issued_by_user" t-value="o.create_uid if (o.create_uid and o.create_uid.name != \'OdooBot\') else (o.sale_id.create_uid if (o.sale_id and o.sale_id.create_uid and o.sale_id.create_uid.name != \'OdooBot\') else (o.sale_id.user_id if (o.sale_id and o.sale_id.user_id and o.sale_id.user_id.name != \'OdooBot\') else o.create_uid))"/>\n          <div name="barani_pickops_prepared_by" class="barani_pick_ops_prepared" t-if="barani_issued_by_user">\n            <strong>Prepared by / Issued by:</strong> <span t-esc="barani_issued_by_user.name"/>\n          </div>\n        </div>\n      </t>\n    </t>\n  </t>\n</t>'
LAYOUT_ARCH='<t t-name="barani_delivery.external_layout_picking_operations_2026">\n    <t t-if="not o" t-set="o" t-value="doc"/>\n    <t t-if="not company">\n        <t t-if="company_id"><t t-set="company" t-value="company_id"/></t>\n        <t t-elif="o and o.company_id"><t t-set="company" t-value="o.company_id.sudo()"/></t>\n        <t t-else="else"><t t-set="company" t-value="res_company"/></t>\n    </t>\n    <div t-attf-class="header o_company_#{company.id}_layout" t-att-style="report_header_style">\n        <div style="position:relative; height:41px;">\n            <div style="float:left; width:35%; height:41px; line-height:41px; position:relative; z-index:10;">\n                <img t-if="company.logo" t-att-src="image_data_uri(company.logo)" style="max-height:41px; vertical-align:middle;" alt="Logo"/>\n            </div>\n            <div t-if="o and o._name == \'stock.picking\'" name="barani_pick_ops_doc_title_right" style="position:absolute; right:0; top:0; height:41px; line-height:41px; text-align:right; max-width:55%; z-index:15;">\n                <span style="font-size:13pt; font-weight:bold; white-space:nowrap; vertical-align:middle;">Picking Operations: <span t-field="o.name"/></span>\n            </div>\n            <div name="barani_top_title_divider" style="position:absolute; left:0; right:0; bottom:0; border-bottom:1px solid black; z-index:40;"/>\n            <div style="clear:both;"/>\n        </div>\n        <div class="row" style="margin-top:2px;">\n            <div class="col-6" name="company_address" style="font-size:10pt; line-height:1.25;">\n                <ul class="list-unstyled" style="margin-bottom:2px;">\n                    <li t-if="company.is_company_details_empty"><t t-esc="company.partner_id" t-options="{&quot;widget&quot;: &quot;contact&quot;, &quot;fields&quot;: [&quot;address&quot;, &quot;name&quot;], &quot;no_marker&quot;: true}"/></li>\n                    <li t-else=""><t t-esc="company.company_details"/></li>\n                </ul>\n            </div>\n            <div class="col-6" name="company_registration" style="font-size:10pt; line-height:1.25; padding-left:18px;">\n                <ul class="list-unstyled" style="margin-bottom:2px;">\n                    <li t-if="company.company_registry">ID: <span t-esc="company.company_registry"/></li>\n                    <li t-if="company.vat">Tax ID: <span t-esc="company.vat[2:] if (company.vat[:2] == \'SK\') else company.vat"/></li>\n                    <li t-if="company.vat">VAT: <span t-esc="company.vat"/></li>\n                </ul>\n            </div>\n        </div>\n        <div name="barani_pick_ops_divider" style="border-bottom:1px solid black; width:100%; margin:1px 0 0 0;"/>\n    </div>\n\n    <div t-attf-class="article o_report_layout_standard o_company_#{company.id}_layout {{ \'o_report_layout_background\' if company.layout_background in [\'Geometric\', \'Custom\'] else \'\' }}" t-attf-style="background-image: url({{ \'data:image/png;base64,%s\' % company.layout_background_image.decode(\'utf-8\') if company.layout_background_image and company.layout_background == \'Custom\' else \'/base/static/img/bg_background_template.jpg\' if company.layout_background == \'Geometric\' else \'\' }});" t-att-data-oe-model="o and o._name" t-att-data-oe-id="o and o.id" t-att-data-oe-lang="o and o.env.context.get(\'lang\')">\n        <t t-out="0"/>\n    </div>\n\n    <div t-attf-class="footer o_standard_footer o_company_#{company.id}_layout">\n        <div class="text-center" style="border-top:1px solid black; font-size:8pt; line-height:1.1; padding-top:2px;">\n            <ul class="list-inline" style="margin:0 0 1px 0; padding:0;"><div t-field="company.report_footer"/></ul>\n            <div t-if="report_type == \'pdf\'" class="text-muted"><span class="page"/> of <span class="topage"/></div>\n            <div t-if="report_type == \'pdf\' and display_name_in_footer" class="text-muted"><span t-field="o.name"/></div>\n        </div>\n    </div>\n</t>'

lines=[]
lines.append(ACTION_NAME)
lines.append('DRY_RUN=%s | CONFIRM=%r | PAGE=%s PAGE_SIZE=%s' % (DRY_RUN, CONFIRM, PAGE, PAGE_SIZE))
lines.append('No business data writes.')
Param=env['ir.config_parameter'].sudo(); View=env['ir.ui.view'].sudo(); Report=env['ir.actions.report'].sudo(); Paper=env['report.paperformat'].sudo(); Model=env['ir.model'].sudo()
blocked=False; planned=[]; cache_method=''

lines.append('TEST 0 - manual SQL savepoint recovery + ORM cache invalidation')
try:
    env.cr.execute('SAVEPOINT barani_installer_t0')
    env.cr.execute('SELECT 1')
    env.cr.execute('RELEASE SAVEPOINT barani_installer_t0')
    lines.append('  PASS: SAVEPOINT recovery works.')
    try:
        env.invalidate_all()
        cache_method='env.invalidate_all'
    except Exception:
        try:
            env['ir.ui.view'].clear_caches()
            cache_method='ir.ui.view.clear_caches'
        except Exception:
            cache_method='cache invalidation unavailable'
    lines.append('  cache method=%s' % cache_method)
except Exception as e:
    blocked=True
    lines.append('  FAIL: savepoint/cache test failed: %s' % e)
lines.append('')

lines.append('TEMPLATE SELF-CHECK')
checks=[('final v4.3+v4.4+31+33 marker','notes_contact_prepared_by_no_grouping_v43|pickops_remove_duplicate_doc_number_v44' in BODY_ARCH and 'barani_pickops_id_partner' in BODY_ARCH and '#ed1c24' in BODY_ARCH and '#B00020' not in BODY_ARCH),('layout t-name','t-name="barani_delivery.external_layout_picking_operations_2026"' in LAYOUT_ARCH),('exploded rows retained','move.move_line_ids' in BODY_ARCH),('duplicate doc block absent','font-size:24pt; font-weight:bold; margin:5px 0 8px 0' not in BODY_ARCH),('barcode columns retained','Lot / Serial Barcode' in BODY_ARCH and 'Product Barcode' in BODY_ARCH),('no DN grouping','barani_dn_l2_kit_parent_line' not in BODY_ARCH),('no DDS/brn','dds_' not in BODY_ARCH+LAYOUT_ARCH and 'brn_' not in BODY_ARCH+LAYOUT_ARCH),('no invoice money fields','Unit Price' not in BODY_ARCH and 'VAT Base' not in BODY_ARCH and 'IBAN' not in BODY_ARCH),('no lambda','lambda ' not in BODY_ARCH)]
bad=[]; scan=BODY_ARCH+LAYOUT_ARCH; pos=0
while True:
    idx=scan.find('t-field="',pos)
    if idx<0: break
    start=idx+len('t-field="'); end=scan.find('"',start); expr=scan[start:end] if end>=0 else 'UNTERMINATED'
    if '.' not in expr: bad.append(expr)
    pos=end+1 if end>=0 else len(scan)
checks.append(('all t-field dotted', not bad))
for label,ok in checks:
    lines.append('  %s: %s'%(label,'PASS' if ok else 'FAIL'))
    if not ok: blocked=True
stock_model=Model.search([('model','=','stock.picking')],limit=1)
if not stock_model: blocked=True
body=View.search([('key','=',BODY_KEY),('type','=','qweb')]); layout=View.search([('key','=',LAYOUT_KEY),('type','=','qweb')]); report=Report.search([('report_name','=',BODY_KEY),('model','=','stock.picking')]); paper=Paper.search([('name','=',PAPER_NAME)],limit=1)
lines.append('DISCOVERY')
for label,recs in [('body',body),('layout',layout),('report',report)]:
    ids=''
    for r in recs: ids += (',' if ids else '')+str(r.id)
    lines.append('  %s count=%s ids=%s'%(label,len(recs),ids))
    if len(recs)>1: blocked=True
planned=[('paper',paper.id if paper else 0),('layout',layout.id if len(layout)==1 else 0),('body',body.id if len(body)==1 else 0),('report',report.id if len(report)==1 else 0),('config_parameter',0)]
lines.append('WRITE PLAN')
if blocked: lines.append('  BLOCKED: resolve errors above; no writes.')
else:
    for target,rec_id in planned: lines.append('  PLAN target=%s id=%s'%(target,rec_id))
lines.append('APPLY PLAN')
if not blocked and not DRY_RUN and CONFIRM==CONFIRM_TOKEN:
    apply_sp='barani_pickops_final_install'
    try:
        env.cr.execute('SAVEPOINT ' + apply_sp)
        paper_vals={'name':PAPER_NAME,'format':'A4','orientation':'Portrait','margin_top':40.0,'margin_bottom':18.0,'margin_left':7.0,'margin_right':7.0,'header_spacing':35,'header_line':False,'dpi':90}
        if paper: paper.write(paper_vals)
        else: paper=Paper.create(paper_vals)
        if len(layout)==1: layout.write({'name':'BARANI Picking Operations external layout 2026','arch_db':LAYOUT_ARCH})
        else: layout=View.create({'name':'BARANI Picking Operations external layout 2026','key':LAYOUT_KEY,'type':'qweb','inherit_id':False,'arch_db':LAYOUT_ARCH})
        if len(body)==1: body.write({'name':'BARANI Picking Operations 2026 report body v4.4 internal pick list + address labels','arch_db':BODY_ARCH})
        else: body=View.create({'name':'BARANI Picking Operations 2026 report body v4.4 internal pick list + address labels','key':BODY_KEY,'type':'qweb','inherit_id':False,'arch_db':BODY_ARCH})
        stock_group=env.ref('stock.group_stock_user', raise_if_not_found=False)
        vals={'name':REPORT_NAME,'model':'stock.picking','report_type':'qweb-pdf','report_name':BODY_KEY,'report_file':BODY_KEY,'binding_model_id':stock_model.id,'binding_type':'report','paperformat_id':paper.id,'print_report_name':"'Picking Operations ' + (object.name or '')"}
        if stock_group: vals['groups_id']=[(6,0,[stock_group.id])]
        if len(report)==1: report.write(vals)
        else: report=Report.create(vals)
        Param.set_param(IDS_PARAMETER_KEY,'%s,%s,%s,%s'%(body.id,report.id,paper.id,layout.id))
        try:
            env.invalidate_all()
            cache_method='env.invalidate_all'
        except Exception:
            try:
                env['ir.ui.view'].clear_caches()
                cache_method='ir.ui.view.clear_caches'
            except Exception:
                cache_method='cache invalidation unavailable'
        lines.append('  cache method after write=%s' % cache_method)
        rb_ok=True
        rb_body=View.search([('key','=',BODY_KEY),('type','=','qweb')])
        rb_layout=View.search([('key','=',LAYOUT_KEY),('type','=','qweb')])
        rb_report=Report.search([('report_name','=',BODY_KEY),('model','=','stock.picking')])
        if len(rb_body)!=1 or rb_body.arch_db != BODY_ARCH: rb_ok=False; lines.append('  READBACK FAIL: PickOps body mismatch or count=%s' % len(rb_body))
        if len(rb_layout)!=1 or rb_layout.arch_db != LAYOUT_ARCH: rb_ok=False; lines.append('  READBACK FAIL: PickOps layout mismatch or count=%s' % len(rb_layout))
        if len(rb_report)!=1: rb_ok=False; lines.append('  READBACK FAIL: PickOps report count=%s' % len(rb_report))
        if rb_ok:
            env.cr.execute('RELEASE SAVEPOINT ' + apply_sp)
            lines.append('  APPLIED body=%s layout=%s report=%s paper=%s'%(body.id,layout.id,report.id,paper.id))
            lines.append('  READBACK: PASS for body/layout/report identity.')
            lines.append('  PASS: Picking Operations final installer complete.')
        else:
            env.cr.execute('ROLLBACK TO SAVEPOINT ' + apply_sp)
            env.cr.execute('RELEASE SAVEPOINT ' + apply_sp)
            blocked=True
            lines.append('  BLOCKED: post-write read-back failed; rolled back to savepoint.')
    except Exception as e:
        try:
            env.cr.execute('ROLLBACK TO SAVEPOINT ' + apply_sp)
            env.cr.execute('RELEASE SAVEPOINT ' + apply_sp)
        except Exception:
            pass
        blocked=True
        lines.append('  APPLY ERROR: %s' % e)
elif DRY_RUN: lines.append('  DRY RUN: no writes performed.')
lines.append('SUMMARY planned_writes=%s | dry_run=%s | blocked=%s'%(len(planned),DRY_RUN,blocked))

full_output = '\n'.join(lines)
if blocked or DRY_RUN or CONFIRM != CONFIRM_TOKEN:
    if not blocked and (not DRY_RUN) and CONFIRM != CONFIRM_TOKEN:
        lines.append('BLOCKED: CONFIRM token mismatch. No writes performed.')
        full_output = '\n'.join(lines)
    total = len(full_output)
    start = (PAGE - 1) * PAGE_SIZE
    if start < 0:
        start = 0
    end = start + PAGE_SIZE
    page_text = full_output[start:end]
    more = 'YES' if end < total else 'NO'
    raise UserError('============ PAGED OUTPUT ============\nFULL = %s chars | PAGE %s | SHOWING %s-%s | MORE REMAINS: %s\n======================================\n' % (total, PAGE, start, min(end, total), more) + page_text)
else:
    Param.set_param(OUTPUT_PARAMETER_KEY, full_output)
    log_param = Param.search([('key', '=', OUTPUT_PARAMETER_KEY)], limit=1)
    action = {'type':'ir.actions.act_window','name':'BARANI installer output','res_model':'ir.config_parameter','view_mode':'form','res_id':log_param.id,'target':'current'}
