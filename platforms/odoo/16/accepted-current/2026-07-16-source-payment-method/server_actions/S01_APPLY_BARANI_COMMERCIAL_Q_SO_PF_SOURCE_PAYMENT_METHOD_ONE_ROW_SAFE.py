# ============================================================================
# ACTION NAME : S01 APPLY — BARANI Q/SO/PF Source + Payment Method one-row SAFE
# MODEL       : Module (ir.module.module) recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
#
# PURPOSE
#   - Add Source to Q/SO/PF metadata using the Sales Order chain number.
#   - Rename Preferred Payment Method to Payment Method.
#   - Keep Wire transfer.
#   - Keep all metadata on one row with explicit no-wrap width maps.
#
# WRITES
#   barani_commercial.report_saleorder_document only.
#
# NO TOUCH
#   VAT/RI/DPI, business records, report actions, Print menus, Preview,
#   paperformats, Delivery Note, stored Payment References, or DDS fields.
# ============================================================================

APPLY = False
CONFIRM = ''
CONFIRM_TOKEN = 'APPLY_BARANI_COMMERCIAL_SOURCE_PAYMENT_METHOD_ONE_ROW_S01'

S00_MARKER = 'barani.source_method.s00.restore.marker'
MARKER = 'barani.source_method.s01.commercial.marker'
OUTPUT_KEY = 'barani.source_method.s01.output'
PREFIX = 'barani.source_method.s00.restore.'

COMM_KEY = 'barani_commercial.report_saleorder_document'
NL = chr(10)

Param = env['ir.config_parameter'].sudo()
View = env['ir.ui.view'].sudo().with_context(lang=None, active_test=False)

SOURCE_OLD = '  <t t-set="barani_source_suffix" t-value="barani_name_raw[1:] if barani_name_raw[:1] == \'Q\' else barani_name_raw"/>'
SOURCE_NEW = '  <t t-set="barani_source_suffix" t-value="barani_name_raw[1:] if barani_name_raw[:1] == \'Q\' else barani_name_raw"/>\n  <t t-set="barani_source_so" t-value="barani_name_raw if barani_name_raw[:2] == \'SO\' else ((\'SO\' + barani_source_suffix) if barani_source_suffix else \'N/A\')"/>'
STYLE_OLD = '      .barani_addr_block .barani_shipping_cell { padding-left: 18px; padding-right: 0; } .barani_addr_heading { font-weight:bold; }'
STYLE_NEW = '      .barani_addr_block .barani_shipping_cell { padding-left: 18px; padding-right: 0; } .barani_addr_heading { font-weight:bold; }\n      /* S01: single-row commercial metadata map with Source and compact Payment Method. */\n      #informations.barani_commercial_meta { display:flex; flex-wrap:nowrap; width:100%; font-size:9.5pt; line-height:1.15; }\n      #informations.barani_commercial_meta &gt; div { min-width:0; padding-left:0; padding-right:7px; box-sizing:border-box; overflow:hidden; }\n      #informations.barani_commercial_meta &gt; div:last-child { padding-right:0; }\n      #informations.barani_commercial_meta strong,\n      #informations.barani_commercial_meta p,\n      #informations.barani_commercial_meta span { white-space:nowrap; }\n      #informations.barani_meta_7 { font-size:8.5pt; }\n      #informations.barani_meta_7 &gt; div[name="doc_date"] { flex:0 0 12.5%; max-width:12.5%; width:12.5%; }\n      #informations.barani_meta_7 &gt; div[name="validity_date"] { flex:0 0 10%; max-width:10%; width:10%; }\n      #informations.barani_meta_7 &gt; div[name="customer_ref"] { flex:0 0 11%; max-width:11%; width:11%; }\n      #informations.barani_meta_7 &gt; div[name="payment_terms"] { flex:0 0 21%; max-width:21%; width:21%; }\n      #informations.barani_meta_7 &gt; div[name="source"] { flex:0 0 12%; max-width:12%; width:12%; }\n      #informations.barani_meta_7 &gt; div[name="barani_payment_reference_info"] { flex:0 0 17.5%; max-width:17.5%; width:17.5%; }\n      #informations.barani_meta_7 &gt; div[name="payment_method"] { flex:0 0 16%; max-width:16%; width:16%; }\n      #informations.barani_meta_6v &gt; div[name="doc_date"] { flex:0 0 13.5%; max-width:13.5%; width:13.5%; }\n      #informations.barani_meta_6v &gt; div[name="validity_date"] { flex:0 0 11.5%; max-width:11.5%; width:11.5%; }\n      #informations.barani_meta_6v &gt; div[name="payment_terms"] { flex:0 0 22.5%; max-width:22.5%; width:22.5%; }\n      #informations.barani_meta_6v &gt; div[name="source"] { flex:0 0 13.5%; max-width:13.5%; width:13.5%; }\n      #informations.barani_meta_6v &gt; div[name="barani_payment_reference_info"] { flex:0 0 18%; max-width:18%; width:18%; }\n      #informations.barani_meta_6v &gt; div[name="payment_method"] { flex:0 0 21%; max-width:21%; width:21%; }\n      #informations.barani_meta_6c &gt; div[name="doc_date"] { flex:0 0 14%; max-width:14%; width:14%; }\n      #informations.barani_meta_6c &gt; div[name="customer_ref"] { flex:0 0 13%; max-width:13%; width:13%; }\n      #informations.barani_meta_6c &gt; div[name="payment_terms"] { flex:0 0 22%; max-width:22%; width:22%; }\n      #informations.barani_meta_6c &gt; div[name="source"] { flex:0 0 13.5%; max-width:13.5%; width:13.5%; }\n      #informations.barani_meta_6c &gt; div[name="barani_payment_reference_info"] { flex:0 0 18%; max-width:18%; width:18%; }\n      #informations.barani_meta_6c &gt; div[name="payment_method"] { flex:0 0 19.5%; max-width:19.5%; width:19.5%; }\n      #informations.barani_meta_5 &gt; div[name="doc_date"] { flex:0 0 16%; max-width:16%; width:16%; }\n      #informations.barani_meta_5 &gt; div[name="payment_terms"] { flex:0 0 24%; max-width:24%; width:24%; }\n      #informations.barani_meta_5 &gt; div[name="source"] { flex:0 0 15%; max-width:15%; width:15%; }\n      #informations.barani_meta_5 &gt; div[name="barani_payment_reference_info"] { flex:0 0 20%; max-width:20%; width:20%; }\n      #informations.barani_meta_5 &gt; div[name="payment_method"] { flex:0 0 25%; max-width:25%; width:25%; }'
META_OLD = '      <t t-set="barani_meta_optional_cols" t-value="(2 if (o.validity_date and not barani_is_proforma) else 0) + (2 if o.client_order_ref else 0)"/>\n      <t t-set="barani_meta_wide_class" t-value="\'col-4\' if barani_meta_optional_cols == 0 else (\'col-3\' if barani_meta_optional_cols == 2 else \'col-2\')"/>\n      <div id="informations" class="row mt-3 barani_info_block">\n        <div class="col-2 mb-2" name="doc_date">\n          <strong><t t-esc="\'Pro-Forma Date\' if barani_is_proforma else (\'Quotation Date\' if o.state in (\'draft\', \'sent\', \'cancel\') else \'Order Date\')"/></strong>\n          <t t-set="barani_doc_date_local" t-value="context_timestamp(o.date_order) if o.date_order else False"/><t t-set="barani_doc_date_display" t-value="(\'%02d %s %04d\' % (barani_doc_date_local.day, barani_date_months[barani_doc_date_local.month - 1], barani_doc_date_local.year)) if barani_doc_date_local else \'\'"/><p class="m-0"><span t-esc="barani_doc_date_display"/></p>\n        </div>\n        <div class="col-2 mb-2" t-if="o.validity_date and not barani_is_proforma" name="validity_date">\n          <strong>Valid Until</strong><t t-set="barani_valid_until_date" t-value="o.validity_date"/><t t-set="barani_valid_until_display" t-value="(\'%02d %s %04d\' % (barani_valid_until_date.day, barani_date_months[barani_valid_until_date.month - 1], barani_valid_until_date.year)) if barani_valid_until_date else \'\'"/><p class="m-0"><span t-esc="barani_valid_until_display"/></p>\n        </div>\n        <div class="col-2 mb-2" t-if="o.client_order_ref" name="customer_ref">\n          <strong>Customer Ref.</strong><p class="m-0" t-field="o.client_order_ref"/>\n        </div>\n        <div t-att-class="barani_meta_wide_class + \' mb-2\'" t-if="o.payment_term_id" name="payment_terms" style="padding-right:12px;">\n          <strong>Payment Terms</strong><t t-set="barani_payment_terms_raw" t-value="o.payment_term_id.name or \'\'"/><t t-set="barani_payment_terms_display" t-value="\'Immediate upon receipt\' if barani_payment_terms_raw in (\'Immediate Payment\', \'Immediate payment\', \'Immediate Upon Receipt\', \'Immediate upon receipt\') else barani_payment_terms_raw"/><p class="m-0"><span t-esc="barani_payment_terms_display"/></p>\n        </div>\n        <div class="col-2 mb-2" name="barani_payment_reference_info">\n          <strong>Payment Reference</strong><p class="m-0"><span t-esc="barani_vs or \'N/A\'"/></p>\n        </div>\n        <div t-att-class="barani_meta_wide_class + \' mb-2\'" name="payment_method" style="padding-right:12px;">\n          <strong>Preferred Payment Method</strong><p class="m-0">Wire transfer</p>\n        </div>\n      </div>'
META_NEW = '      <t t-set="barani_has_validity" t-value="bool(o.validity_date and not barani_is_proforma)"/>\n      <t t-set="barani_has_customer_ref" t-value="bool(o.client_order_ref)"/>\n      <t t-set="barani_meta_case" t-value="\'barani_meta_7\' if (barani_has_validity and barani_has_customer_ref) else (\'barani_meta_6v\' if barani_has_validity else (\'barani_meta_6c\' if barani_has_customer_ref else \'barani_meta_5\'))"/>\n      <div id="informations" t-att-class="\'row mt-3 barani_info_block barani_commercial_meta \' + barani_meta_case">\n        <div class="mb-2" name="doc_date">\n          <strong><t t-esc="\'Pro-Forma Date\' if barani_is_proforma else (\'Quotation Date\' if o.state in (\'draft\', \'sent\', \'cancel\') else \'Order Date\')"/></strong>\n          <t t-set="barani_doc_date_local" t-value="context_timestamp(o.date_order) if o.date_order else False"/><t t-set="barani_doc_date_display" t-value="(\'%02d %s %04d\' % (barani_doc_date_local.day, barani_date_months[barani_doc_date_local.month - 1], barani_doc_date_local.year)) if barani_doc_date_local else \'\'"/><p class="m-0"><span t-esc="barani_doc_date_display"/></p>\n        </div>\n        <div class="mb-2" t-if="barani_has_validity" name="validity_date">\n          <strong>Valid Until</strong><t t-set="barani_valid_until_date" t-value="o.validity_date"/><t t-set="barani_valid_until_display" t-value="(\'%02d %s %04d\' % (barani_valid_until_date.day, barani_date_months[barani_valid_until_date.month - 1], barani_valid_until_date.year)) if barani_valid_until_date else \'\'"/><p class="m-0"><span t-esc="barani_valid_until_display"/></p>\n        </div>\n        <div class="mb-2" t-if="barani_has_customer_ref" name="customer_ref">\n          <strong>Customer Ref.</strong><p class="m-0" t-field="o.client_order_ref"/>\n        </div>\n        <div class="mb-2" t-if="o.payment_term_id" name="payment_terms">\n          <strong>Payment Terms</strong><t t-set="barani_payment_terms_raw" t-value="o.payment_term_id.name or \'\'"/><t t-set="barani_payment_terms_display" t-value="\'Immediate upon receipt\' if barani_payment_terms_raw in (\'Immediate Payment\', \'Immediate payment\', \'Immediate Upon Receipt\', \'Immediate upon receipt\') else barani_payment_terms_raw"/><p class="m-0"><span t-esc="barani_payment_terms_display"/></p>\n        </div>\n        <div class="mb-2" name="source">\n          <strong>Source</strong><p class="m-0"><span t-esc="barani_source_so"/></p>\n        </div>\n        <div class="mb-2" name="barani_payment_reference_info">\n          <strong>Payment Reference</strong><p class="m-0"><span t-esc="barani_vs or \'N/A\'"/></p>\n        </div>\n        <div class="mb-2" name="payment_method">\n          <strong>Payment Method</strong><p class="m-0">Wire transfer</p>\n        </div>\n      </div>'

lines = []
lines.append('S01 APPLY — BARANI Q/SO/PF Source + Payment Method one-row SAFE')
lines.append('APPLY=%s CONFIRM_OK=%s' % (APPLY, CONFIRM == CONFIRM_TOKEN))
lines.append('Commercial Q/SO/PF body only; VAT/RI/DPI and business records untouched.')
lines.append('')

problems = 0

if Param.get_param(S00_MARKER) != '1':
    lines.append('FAIL: S00 restore point marker missing.')
    problems = problems + 1
else:
    lines.append('PRECHECK S00 marker: PASS')

backup_id = int(Param.get_param(PREFIX + 'view.commercial.id') or '0')
backup_arch = Param.get_param(PREFIX + 'view.commercial.arch') or ''

rs = View.search([('key', '=', COMM_KEY), ('type', '=', 'qweb')], limit=2)
if len(rs) != 1:
    lines.append('FAIL: commercial QWeb found=%s expected=1' % len(rs))
    problems = problems + 1
    body = View.browse([])
else:
    body = rs[0]
    lines.append(
        'DISCOVERY id=%s key=%s len=%s write_date=%s standalone=%s'
        % (body.id, body.key, len(body.arch_db or ''), body.write_date, not bool(body.inherit_id))
    )
    if body.id != backup_id or body.inherit_id:
        problems = problems + 1

old_arch = body.arch_db or '' if body else ''
already_done = (
    'barani_source_so' in old_arch
    and 'barani_commercial_meta' in old_arch
    and '<strong>Payment Method</strong>' in old_arch
    and 'Preferred Payment Method' not in old_arch
    and 'name="source"' in old_arch
)

if Param.get_param(MARKER) == '1':
    if already_done:
        lines.append('NO-OP: S01 marker exists and commercial read-back markers are complete.')
        raise UserError(NL.join(lines)[:90000])
    lines.append('FAIL: S01 marker exists but commercial state is incomplete.')
    problems = problems + 1
elif already_done:
    lines.append('FAIL: commercial patch markers exist while S01 marker is absent; partial state.')
    problems = problems + 1

if not already_done and old_arch != backup_arch:
    lines.append('FAIL: current commercial QWeb bytes differ from the S00 restore baseline.')
    problems = problems + 1

if problems:
    lines.append('')
    lines.append('ERROR: %s preflight problem(s); no writes performed.' % problems)
    raise UserError(NL.join(lines)[:90000])

new_arch = old_arch
replacements = [
    ('source variable', SOURCE_OLD, SOURCE_NEW),
    ('single-row metadata CSS', STYLE_OLD, STYLE_NEW),
    ('metadata block', META_OLD, META_NEW),
]

lines.append('')
lines.append('PATCH PREFLIGHT')
for label, old, new in replacements:
    count = new_arch.count(old)
    lines.append('  %s old-marker count=%s' % (label, count))
    if count != 1:
        problems = problems + 1
    else:
        new_arch = new_arch.replace(old, new, 1)

checks = [
    ('Source variable present', 'barani_source_so' in new_arch),
    ('Source field present exactly once', new_arch.count('<div class="mb-2" name="source">') == 1),
    ('SO-normalized source expression present', "('SO' + barani_source_suffix)" in new_arch),
    ('Payment Method label present', '<strong>Payment Method</strong>' in new_arch),
    ('Preferred label removed', 'Preferred Payment Method' not in new_arch),
    ('Wire transfer retained', '>Wire transfer<' in new_arch),
    ('single-row nowrap marker present', 'flex-wrap:nowrap' in new_arch),
    ('dense 7-field map present', 'barani_meta_7' in new_arch and 'font-size:8.5pt' in new_arch),
    ('validity map present', 'barani_meta_6v' in new_arch),
    ('PF/customer-ref map present', 'barani_meta_6c' in new_arch),
    ('basic PF map present', 'barani_meta_5' in new_arch),
    ('old dynamic classes removed', 'barani_meta_optional_cols' not in new_arch and 'barani_meta_wide_class' not in new_arch),
    ('Payment Reference fallback retained', 'barani_vs or \'N/A\'' in new_arch),
    ('fixed discount column retained', 'barani_discount_col_fixed' in new_arch),
    ('numeric VAT marker retained', 'barani_commercial_vat_rate_col_final' in new_arch),
    ('ten table columns retained', new_arch.count('<col') >= 10),
    ('no DDS dependency', 'dds_' not in new_arch.lower()),
]
for label, ok in checks:
    lines.append('  %s: %s' % (label, 'PASS' if ok else 'FAIL'))
    if not ok:
        problems = problems + 1

lines.append('')
lines.append('PLAN')
lines.append('  update Q/SO/PF body id=%s only' % body.id)
lines.append('  old_len=%s new_len=%s delta=%s' % (len(old_arch), len(new_arch), len(new_arch) - len(old_arch)))
lines.append('  one metadata row; explicit width maps; labels/values do not wrap into adjacent columns')
lines.append('  Source display example: Q/126/00157 -> SO/126/00157')
lines.append('  Payment Method value remains Wire transfer')
lines.append('  VAT/RI/DPI, report actions, Preview, paperformats, and business records untouched')

if problems:
    lines.append('')
    lines.append('ERROR: %s patch problem(s); no writes performed.' % problems)
    raise UserError(NL.join(lines)[:90000])

if not APPLY or CONFIRM != CONFIRM_TOKEN:
    lines.append('')
    lines.append('DRY RUN — no writes performed.')
    lines.append('Apply with APPLY=True and CONFIRM=%s.' % CONFIRM_TOKEN)
    raise UserError(NL.join(lines)[:90000])

body.with_context(lang=None).write({'arch_db': new_arch})
View.clear_caches()

fresh = View.browse(body.id)
if (fresh.arch_db or '') != new_arch:
    raise UserError((NL.join(lines) + NL + 'READ-BACK FAILED; transaction rolled back.')[:90000])

Param.set_param(MARKER, '1')
lines.append('')
lines.append('S01 COMPLETE: Q/SO/PF Source + Payment Method one-row layout applied; exact read-back PASS.')
text = NL.join(lines)[:90000]
Param.set_param(OUTPUT_KEY, text)
out = Param.search([('key', '=', OUTPUT_KEY)], limit=1)
action = {
    'type': 'ir.actions.act_window',
    'name': 'S01 BARANI commercial Source / Payment Method result',
    'res_model': 'ir.config_parameter',
    'view_mode': 'form',
    'res_id': out.id,
    'target': 'current',
}
