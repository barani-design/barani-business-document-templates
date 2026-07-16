# ============================================================================
# ACTION NAME : S02 APPLY — BARANI RI/DPI/CN Source + Payment Method alignment SAFE
# MODEL       : Module (ir.module.module) recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
#
# PURPOSE
#   - Normalize the visible Source to the shared SO chain number when exactly
#     one linked Sales Order is available (fallback: invoice_origin).
#   - Rename Preferred Payment Method to Payment Method.
#   - Keep Wire transfer.
#   - Preserve the historical source-derived Payment Reference fallback.
#
# WRITES
#   barani_vat.report_invoice_document_vat only.
#
# NO TOUCH
#   Stored Payment References, invoices, Sales Orders, taxes, totals, report
#   actions, Print menus, Preview routing, paperformats, or DDS fields.
# ============================================================================

APPLY = False
CONFIRM = ''
CONFIRM_TOKEN = 'APPLY_BARANI_VAT_SOURCE_PAYMENT_METHOD_ALIGNMENT_S02'

S00_MARKER = 'barani.source_method.s00.restore.marker'
S01_MARKER = 'barani.source_method.s01.commercial.marker'
MARKER = 'barani.source_method.s02.vat.marker'
OUTPUT_KEY = 'barani.source_method.s02.output'
PREFIX = 'barani.source_method.s00.restore.'

VAT_KEY = 'barani_vat.report_invoice_document_vat'
NL = chr(10)

Param = env['ir.config_parameter'].sudo()
View = env['ir.ui.view'].sudo().with_context(lang=None, active_test=False)
Field = env['ir.model.fields'].sudo()

SOURCE_OLD = '        <t t-set="barani_pdf_payment_ref" t-value="barani_payment_ref_upper.replace(\'A\', \'\').replace(\'B\', \'\').replace(\'C\', \'\').replace(\'D\', \'\').replace(\'E\', \'\').replace(\'F\', \'\').replace(\'G\', \'\').replace(\'H\', \'\').replace(\'I\', \'\').replace(\'J\', \'\').replace(\'K\', \'\').replace(\'L\', \'\').replace(\'M\', \'\').replace(\'N\', \'\').replace(\'O\', \'\').replace(\'P\', \'\').replace(\'Q\', \'\').replace(\'R\', \'\').replace(\'S\', \'\').replace(\'T\', \'\').replace(\'U\', \'\').replace(\'V\', \'\').replace(\'W\', \'\').replace(\'X\', \'\').replace(\'Y\', \'\').replace(\'Z\', \'\').replace(\'/\', \'\').replace(\'-\', \'\').replace(\' \', \'\').replace(\'_\', \'\').replace(\'.\', \'\').replace(\':\', \'\').replace(\';\', \'\').replace(\',\', \'\').replace(\'#\', \'\').replace(\'(\', \'\').replace(\')\', \'\').replace(\'[\', \'\').replace(\']\', \'\').replace(\'{\', \'\').replace(\'}\', \'\')"/>'
SOURCE_NEW = '        <t t-set="barani_pdf_payment_ref" t-value="barani_payment_ref_upper.replace(\'A\', \'\').replace(\'B\', \'\').replace(\'C\', \'\').replace(\'D\', \'\').replace(\'E\', \'\').replace(\'F\', \'\').replace(\'G\', \'\').replace(\'H\', \'\').replace(\'I\', \'\').replace(\'J\', \'\').replace(\'K\', \'\').replace(\'L\', \'\').replace(\'M\', \'\').replace(\'N\', \'\').replace(\'O\', \'\').replace(\'P\', \'\').replace(\'Q\', \'\').replace(\'R\', \'\').replace(\'S\', \'\').replace(\'T\', \'\').replace(\'U\', \'\').replace(\'V\', \'\').replace(\'W\', \'\').replace(\'X\', \'\').replace(\'Y\', \'\').replace(\'Z\', \'\').replace(\'/\', \'\').replace(\'-\', \'\').replace(\' \', \'\').replace(\'_\', \'\').replace(\'.\', \'\').replace(\':\', \'\').replace(\';\', \'\').replace(\',\', \'\').replace(\'#\', \'\').replace(\'(\', \'\').replace(\')\', \'\').replace(\'[\', \'\').replace(\']\', \'\').replace(\'{\', \'\').replace(\'}\', \'\')"/>\n        <t t-set="barani_source_orders" t-value="o.invoice_line_ids.mapped(\'sale_line_ids.order_id\')"/>\n        <t t-set="barani_source_order_name" t-value="barani_source_orders[0].name if len(barani_source_orders) == 1 else (o.invoice_origin or \'\')"/>\n        <t t-set="barani_source_display" t-value="barani_source_order_name if barani_source_order_name[:2] == \'SO\' else ((\'SO\' + barani_source_order_name[1:]) if barani_source_order_name[:1] == \'Q\' and \',\' not in barani_source_order_name and \';\' not in barani_source_order_name else barani_source_order_name)"/>'
WIDTH_OLD = '          #informations.barani_info_block &gt; div[name="origin"] { flex: 0 0 13.5%; max-width: 13.5%; width: 13.5%; }\n          #informations.barani_info_block &gt; div[name="payment_reference"] { flex: 0 0 17.5%; max-width: 17.5%; width: 17.5%; }\n          #informations.barani_info_block &gt; div[name="payment_method"] { flex: 0 0 32.5%; max-width: 32.5%; width: 32.5%; }'
WIDTH_NEW = '          #informations.barani_info_block &gt; div[name="origin"] { flex: 0 0 15%; max-width: 15%; width: 15%; }\n          #informations.barani_info_block &gt; div[name="payment_reference"] { flex: 0 0 18%; max-width: 18%; width: 18%; }\n          #informations.barani_info_block &gt; div[name="payment_method"] { flex: 0 0 30.5%; max-width: 30.5%; width: 30.5%; }'
ORIGIN_OLD = '            <div class="col-2 mb-2" t-if="o.invoice_origin" name="origin">\n              <strong>Source</strong><p class="m-0" t-field="o.invoice_origin"/>\n            </div>'
ORIGIN_NEW = '            <div class="col-2 mb-2" t-if="barani_source_display" name="origin">\n              <strong>Source</strong><p class="m-0"><span t-esc="barani_source_display"/></p>\n            </div>'
METHOD_OLD = '              <strong>Preferred Payment Method</strong><p class="m-0">Wire transfer</p>'
METHOD_NEW = '              <strong>Payment Method</strong><p class="m-0">Wire transfer</p>'

lines = []
lines.append('S02 APPLY — BARANI RI/DPI/CN Source + Payment Method alignment SAFE')
lines.append('APPLY=%s CONFIRM_OK=%s' % (APPLY, CONFIRM == CONFIRM_TOKEN))
lines.append('VAT/RI/DPI/Credit Note body only; stored references and accounting untouched.')
lines.append('')

problems = 0

if Param.get_param(S00_MARKER) != '1':
    lines.append('FAIL: S00 restore point marker missing.')
    problems = problems + 1
else:
    lines.append('PRECHECK S00 marker: PASS')

if Param.get_param(S01_MARKER) != '1':
    lines.append('FAIL: S01 commercial alignment marker missing. Apply/verify S01 first.')
    problems = problems + 1
else:
    lines.append('PRECHECK S01 marker: PASS')

sale_line_field = Field.search([
    ('model', '=', 'account.move.line'),
    ('name', '=', 'sale_line_ids'),
], limit=1)
lines.append('PRECHECK account.move.line.sale_line_ids: %s' % ('PASS' if sale_line_field else 'FAIL'))
if not sale_line_field:
    problems = problems + 1

backup_id = int(Param.get_param(PREFIX + 'view.vat.id') or '0')
backup_arch = Param.get_param(PREFIX + 'view.vat.arch') or ''

rs = View.search([('key', '=', VAT_KEY), ('type', '=', 'qweb')], limit=2)
if len(rs) != 1:
    lines.append('FAIL: VAT QWeb found=%s expected=1' % len(rs))
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
    'barani_source_display' in old_arch
    and 'barani_source_orders' in old_arch
    and '<strong>Payment Method</strong>' in old_arch
    and 'Preferred Payment Method' not in old_arch
    and 't-esc="barani_source_display"' in old_arch
)

if Param.get_param(MARKER) == '1':
    if already_done:
        lines.append('NO-OP: S02 marker exists and VAT read-back markers are complete.')
        raise UserError(NL.join(lines)[:90000])
    lines.append('FAIL: S02 marker exists but VAT state is incomplete.')
    problems = problems + 1
elif already_done:
    lines.append('FAIL: VAT patch markers exist while S02 marker is absent; partial state.')
    problems = problems + 1

if not already_done and old_arch != backup_arch:
    lines.append('FAIL: current VAT QWeb bytes differ from the S00 restore baseline.')
    problems = problems + 1

if problems:
    lines.append('')
    lines.append('ERROR: %s preflight problem(s); no writes performed.' % problems)
    raise UserError(NL.join(lines)[:90000])

new_arch = old_arch
replacements = [
    ('source variables', SOURCE_OLD, SOURCE_NEW),
    ('invoice metadata widths', WIDTH_OLD, WIDTH_NEW),
    ('Source display block', ORIGIN_OLD, ORIGIN_NEW),
    ('Payment Method label', METHOD_OLD, METHOD_NEW),
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
    ('exact linked sale-order source lookup present', "mapped('sale_line_ids.order_id')" in new_arch),
    ('single-source guard present', 'len(barani_source_orders) == 1' in new_arch),
    ('SO-normalized source expression present', "('SO' + barani_source_order_name[1:])" in new_arch),
    ('multi-source fallback guard present', "',' not in barani_source_order_name" in new_arch and "';' not in barani_source_order_name" in new_arch),
    ('Source display uses normalized value', 't-esc="barani_source_display"' in new_arch),
    ('Payment Method label present', '<strong>Payment Method</strong>' in new_arch),
    ('Preferred label removed', 'Preferred Payment Method' not in new_arch),
    ('Wire transfer retained', '>Wire transfer<' in new_arch),
    ('Source width increased', 'div[name="origin"] { flex: 0 0 15%' in new_arch),
    ('historical Payment Reference fallback retained', 'barani_pdf_payment_ref' in new_arch and 'barani_payment_ref_raw' in new_arch),
    ('credit-note original reference retained', 'barani_credit_original_payment_ref' in new_arch and 'Original Payment Reference' in new_arch),
    ('down-payment logic retained', 'barani_down_payment_reconciliation_table' in new_arch),
    ('fixed discount column retained', 'barani_discount_col_fixed' in new_arch),
    ('numeric VAT marker retained', 'barani_vat_rate_col_final' in new_arch),
    ('no DDS dependency', 'dds_' not in new_arch.lower()),
]
for label, ok in checks:
    lines.append('  %s: %s' % (label, 'PASS' if ok else 'FAIL'))
    if not ok:
        problems = problems + 1

lines.append('')
lines.append('PLAN')
lines.append('  update VAT/RI/DPI/Credit Note body id=%s only' % body.id)
lines.append('  old_len=%s new_len=%s delta=%s' % (len(old_arch), len(new_arch), len(new_arch) - len(old_arch)))
lines.append('  visible Source example: Q/126/00157 -> SO/126/00157')
lines.append('  multiple-source origins remain unmodified rather than choosing an arbitrary SO')
lines.append('  stored Payment References, source fields, invoices, totals, and accounting untouched')
lines.append('  report actions, Print menus, HTML Preview action, and paperformats untouched')

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
lines.append('S02 COMPLETE: RI/DPI/CN Source + Payment Method alignment applied; exact read-back PASS.')
text = NL.join(lines)[:90000]
Param.set_param(OUTPUT_KEY, text)
out = Param.search([('key', '=', OUTPUT_KEY)], limit=1)
action = {
    'type': 'ir.actions.act_window',
    'name': 'S02 BARANI VAT Source / Payment Method result',
    'res_model': 'ir.config_parameter',
    'view_mode': 'form',
    'res_id': out.id,
    'target': 'current',
}
