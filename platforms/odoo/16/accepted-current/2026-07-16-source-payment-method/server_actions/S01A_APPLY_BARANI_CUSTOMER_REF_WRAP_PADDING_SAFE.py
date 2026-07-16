# ============================================================================
# ACTION NAME : S01A APPLY — BARANI Customer Ref. wrap + right padding SAFE
# MODEL       : Module (ir.module.module) recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
#
# PURPOSE
#   Keep the commercial metadata on one row, but allow only the Customer Ref.
#   value to wrap inside its own column. Add right padding so wrapped text cannot
#   visually touch or flow into Payment Terms.
#
# WRITES
#   barani_commercial.report_saleorder_document only.
#
# NO TOUCH
#   Width maps, VAT/RI/DPI, business records, report actions, Print menus,
#   Preview, paperformats, Delivery Note, stored Payment References, or DDS.
# ============================================================================

APPLY = False
CONFIRM = ''
CONFIRM_TOKEN = 'APPLY_BARANI_CUSTOMER_REF_WRAP_PADDING_S01A'

S00_MARKER = 'barani.source_method.s00.restore.marker'
S01_MARKER = 'barani.source_method.s01.commercial.marker'
MARKER = 'barani.source_method.s01a.customer_ref_wrap.marker'
OUTPUT_KEY = 'barani.source_method.s01a.output'

COMM_KEY = 'barani_commercial.report_saleorder_document'
NL = chr(10)

Param = env['ir.config_parameter'].sudo()
View = env['ir.ui.view'].sudo().with_context(lang=None, active_test=False)

CSS_OLD = '''      #informations.barani_commercial_meta strong,
      #informations.barani_commercial_meta p,
      #informations.barani_commercial_meta span { white-space:nowrap; }'''

CSS_NEW = '''      #informations.barani_commercial_meta strong { white-space:nowrap; }
      #informations.barani_commercial_meta p,
      #informations.barani_commercial_meta span { white-space:nowrap; }
      /* S01A: Customer Ref. is unbounded in Odoo; wrap it only inside its own cell. */
      #informations.barani_commercial_meta &gt; div[name="customer_ref"] {
        padding-right:14px;
      }
      #informations.barani_commercial_meta &gt; div[name="customer_ref"] p,
      #informations.barani_commercial_meta &gt; div[name="customer_ref"] span {
        display:block;
        white-space:normal !important;
        word-wrap:break-word;
        word-break:break-word;
        overflow-wrap:break-word;
        line-height:1.1;
      }'''

lines = []
lines.append('S01A APPLY — BARANI Customer Ref. wrap + right padding SAFE')
lines.append('APPLY=%s CONFIRM_OK=%s' % (APPLY, CONFIRM == CONFIRM_TOKEN))
lines.append('Commercial Q/SO/PF CSS only; metadata width maps and business records untouched.')
lines.append('')

problems = 0

if Param.get_param(S00_MARKER) != '1':
    lines.append('FAIL: S00 restore marker missing.')
    problems = problems + 1
else:
    lines.append('PRECHECK S00 marker: PASS')

if Param.get_param(S01_MARKER) != '1':
    lines.append('FAIL: S01 commercial marker missing. Apply/verify S01 first.')
    problems = problems + 1
else:
    lines.append('PRECHECK S01 marker: PASS')

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
    if body.inherit_id:
        problems = problems + 1

old_arch = body.arch_db or '' if body else ''
already_done = (
    'S01A: Customer Ref. is unbounded in Odoo' in old_arch
    and 'padding-right:14px' in old_arch
    and 'white-space:normal !important' in old_arch
    and 'word-wrap:break-word' in old_arch
)

if Param.get_param(MARKER) == '1':
    if already_done:
        lines.append('NO-OP: S01A marker exists and Customer Ref. wrap read-back markers are complete.')
        raise UserError(NL.join(lines)[:90000])
    lines.append('FAIL: S01A marker exists but wrap state is incomplete.')
    problems = problems + 1
elif already_done:
    lines.append('FAIL: wrap markers exist while S01A marker is absent; partial state.')
    problems = problems + 1

if problems:
    lines.append('')
    lines.append('ERROR: %s preflight problem(s); no writes performed.' % problems)
    raise UserError(NL.join(lines)[:90000])

count = old_arch.count(CSS_OLD)
lines.append('')
lines.append('PATCH PREFLIGHT')
lines.append('  global nowrap CSS old-marker count=%s' % count)
if count != 1:
    problems = problems + 1

new_arch = old_arch.replace(CSS_OLD, CSS_NEW, 1) if count == 1 else old_arch

checks = [
    ('Customer Ref. cell exists', '<div class="mb-2" t-if="barani_has_customer_ref" name="customer_ref">' in new_arch),
    ('Customer Ref. right padding present', 'div[name="customer_ref"] {' in new_arch and 'padding-right:14px' in new_arch),
    ('Customer Ref. value wrap override present', 'white-space:normal !important' in new_arch),
    ('long-token break fallback present', 'word-wrap:break-word' in new_arch and 'word-break:break-word' in new_arch),
    ('all other metadata remains nowrap', '#informations.barani_commercial_meta p,' in new_arch and '#informations.barani_commercial_meta span { white-space:nowrap; }' in new_arch),
    ('single metadata row retained', 'flex-wrap:nowrap' in new_arch),
    ('7-field width map unchanged', 'barani_meta_7' in new_arch and 'div[name="customer_ref"] { flex:0 0 11%' in new_arch),
    ('6-field Customer Ref. map unchanged', 'barani_meta_6c' in new_arch and 'div[name="customer_ref"] { flex:0 0 13%' in new_arch),
    ('Source retained', 'barani_source_so' in new_arch and '<strong>Source</strong>' in new_arch),
    ('Payment Method retained', '<strong>Payment Method</strong>' in new_arch and '>Wire transfer<' in new_arch),
    ('Payment Reference fallback retained', 'barani_vs or \'N/A\'' in new_arch),
    ('product-table markers retained', 'barani_discount_col_fixed' in new_arch and 'barani_commercial_vat_rate_col_final' in new_arch),
    ('no DDS dependency', 'dds_' not in new_arch.lower()),
]
for label, ok in checks:
    lines.append('  %s: %s' % (label, 'PASS' if ok else 'FAIL'))
    if not ok:
        problems = problems + 1

lines.append('')
lines.append('PLAN')
lines.append('  update commercial QWeb id=%s only' % body.id)
lines.append('  allow Customer Ref. value to wrap inside its own existing column')
lines.append('  add 14px right padding before Payment Terms')
lines.append('  keep one metadata row and all width maps unchanged')
lines.append('  no VAT/RI/DPI, report-routing, Preview, paperformat, or business-record changes')

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
lines.append('S01A COMPLETE: Customer Ref. wrap + right padding applied; exact read-back PASS.')
text = NL.join(lines)[:90000]
Param.set_param(OUTPUT_KEY, text)
out = Param.search([('key', '=', OUTPUT_KEY)], limit=1)
action = {
    'type': 'ir.actions.act_window',
    'name': 'S01A BARANI Customer Ref. wrap result',
    'res_model': 'ir.config_parameter',
    'view_mode': 'form',
    'res_id': out.id,
    'target': 'current',
}
