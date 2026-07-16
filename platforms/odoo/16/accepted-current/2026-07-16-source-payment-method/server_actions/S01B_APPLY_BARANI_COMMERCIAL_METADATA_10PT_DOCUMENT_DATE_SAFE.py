# ============================================================================
# ACTION NAME : S01B APPLY — BARANI commercial metadata 10pt + Document Date SAFE
# MODEL       : Module (ir.module.module) recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
#
# PURPOSE
#   - Restore the commercial metadata block to the document's standard 10pt font.
#   - Remove the 8.5pt dense-case reduction.
#   - Use the agreed label "Document Date" consistently on Q/SO/PF.
#   - Rebalance only the densest seven-field width map for 10pt text.
#
# WRITES
#   barani_commercial.report_saleorder_document only.
#
# NO TOUCH
#   Customer Ref. wrap rule, VAT/RI/DPI, business records, report actions,
#   Print menus, Preview, paperformats, Delivery Note, stored Payment References,
#   product-table widths, taxes, totals, or DDS fields.
# ============================================================================

APPLY = False
CONFIRM = ''
CONFIRM_TOKEN = 'APPLY_BARANI_COMMERCIAL_METADATA_10PT_DOCUMENT_DATE_S01B'

S00_MARKER = 'barani.source_method.s00.restore.marker'
S01_MARKER = 'barani.source_method.s01.commercial.marker'
S01A_MARKER = 'barani.source_method.s01a.customer_ref_wrap.marker'
MARKER = 'barani.source_method.s01b.metadata_10pt.marker'
OUTPUT_KEY = 'barani.source_method.s01b.output'

COMM_KEY = 'barani_commercial.report_saleorder_document'
NL = chr(10)

Param = env['ir.config_parameter'].sudo()
View = env['ir.ui.view'].sudo().with_context(lang=None, active_test=False)

FONT_OLD = '#informations.barani_commercial_meta { display:flex; flex-wrap:nowrap; width:100%; font-size:9.5pt; line-height:1.15; }'
FONT_NEW = '#informations.barani_commercial_meta { display:flex; flex-wrap:nowrap; width:100%; font-size:10pt; line-height:1.15; }'

DENSE_FONT_OLD = '#informations.barani_meta_7 { font-size:8.5pt; }'
DENSE_FONT_NEW = '#informations.barani_meta_7 { font-size:10pt; }'

DATE_LABEL_OLD = '''          <strong><t t-esc="'Pro-Forma Date' if barani_is_proforma else ('Quotation Date' if o.state in ('draft', 'sent', 'cancel') else 'Order Date')"/></strong>'''
DATE_LABEL_NEW = '''          <strong>Document Date</strong>'''

WIDTHS_OLD = '''      #informations.barani_meta_7 &gt; div[name="doc_date"] { flex:0 0 12.5%; max-width:12.5%; width:12.5%; }
      #informations.barani_meta_7 &gt; div[name="validity_date"] { flex:0 0 10%; max-width:10%; width:10%; }
      #informations.barani_meta_7 &gt; div[name="customer_ref"] { flex:0 0 11%; max-width:11%; width:11%; }
      #informations.barani_meta_7 &gt; div[name="payment_terms"] { flex:0 0 21%; max-width:21%; width:21%; }
      #informations.barani_meta_7 &gt; div[name="source"] { flex:0 0 12%; max-width:12%; width:12%; }
      #informations.barani_meta_7 &gt; div[name="barani_payment_reference_info"] { flex:0 0 17.5%; max-width:17.5%; width:17.5%; }
      #informations.barani_meta_7 &gt; div[name="payment_method"] { flex:0 0 16%; max-width:16%; width:16%; }'''

WIDTHS_NEW = '''      #informations.barani_meta_7 &gt; div[name="doc_date"] { flex:0 0 13%; max-width:13%; width:13%; }
      #informations.barani_meta_7 &gt; div[name="validity_date"] { flex:0 0 12.5%; max-width:12.5%; width:12.5%; }
      #informations.barani_meta_7 &gt; div[name="customer_ref"] { flex:0 0 12%; max-width:12%; width:12%; }
      #informations.barani_meta_7 &gt; div[name="payment_terms"] { flex:0 0 20%; max-width:20%; width:20%; }
      #informations.barani_meta_7 &gt; div[name="source"] { flex:0 0 12%; max-width:12%; width:12%; }
      #informations.barani_meta_7 &gt; div[name="barani_payment_reference_info"] { flex:0 0 16.5%; max-width:16.5%; width:16.5%; }
      #informations.barani_meta_7 &gt; div[name="payment_method"] { flex:0 0 14%; max-width:14%; width:14%; }'''

lines = []
lines.append('S01B APPLY — BARANI commercial metadata 10pt + Document Date SAFE')
lines.append('APPLY=%s CONFIRM_OK=%s' % (APPLY, CONFIRM == CONFIRM_TOKEN))
lines.append('Commercial Q/SO/PF metadata typography and dense width map only.')
lines.append('')

problems = 0

for marker, label in [
    (S00_MARKER, 'S00'),
    (S01_MARKER, 'S01'),
    (S01A_MARKER, 'S01A'),
]:
    ok = Param.get_param(marker) == '1'
    lines.append('PRECHECK %s marker: %s' % (label, 'PASS' if ok else 'FAIL'))
    if not ok:
        problems = problems + 1

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
    FONT_NEW in old_arch
    and DENSE_FONT_NEW in old_arch
    and DATE_LABEL_NEW in old_arch
    and WIDTHS_NEW in old_arch
    and 'font-size:8.5pt' not in old_arch
)

if Param.get_param(MARKER) == '1':
    if already_done:
        lines.append('NO-OP: S01B marker exists and 10pt/Document Date read-back markers are complete.')
        raise UserError(NL.join(lines)[:90000])
    lines.append('FAIL: S01B marker exists but live state is incomplete.')
    problems = problems + 1
elif already_done:
    lines.append('FAIL: S01B markers exist while marker is absent; partial state.')
    problems = problems + 1

if problems:
    lines.append('')
    lines.append('ERROR: %s preflight problem(s); no writes performed.' % problems)
    raise UserError(NL.join(lines)[:90000])

replacements = [
    ('metadata base font 9.5pt -> 10pt', FONT_OLD, FONT_NEW),
    ('dense font 8.5pt -> 10pt', DENSE_FONT_OLD, DENSE_FONT_NEW),
    ('dynamic date label -> Document Date', DATE_LABEL_OLD, DATE_LABEL_NEW),
    ('dense seven-field width map', WIDTHS_OLD, WIDTHS_NEW),
]

new_arch = old_arch
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
    ('commercial metadata is standard 10pt', FONT_NEW in new_arch),
    ('dense seven-field case is also 10pt', DENSE_FONT_NEW in new_arch),
    ('8.5pt dense override removed', 'font-size:8.5pt' not in new_arch),
    ('9.5pt metadata override removed', FONT_OLD not in new_arch),
    ('Document Date label present', new_arch.count('<strong>Document Date</strong>') == 1),
    ('old dynamic date label removed', "'Pro-Forma Date' if barani_is_proforma" not in new_arch),
    ('dense widths sum to 100 percent', WIDTHS_NEW in new_arch),
    ('Customer Ref. wrap retained', 'white-space:normal !important' in new_arch and 'padding-right:14px' in new_arch),
    ('single metadata row retained', 'flex-wrap:nowrap' in new_arch),
    ('Source retained', 'barani_source_so' in new_arch and '<strong>Source</strong>' in new_arch),
    ('Payment Reference retained', '<strong>Payment Reference</strong>' in new_arch and "barani_vs or 'N/A'" in new_arch),
    ('Payment Method retained', '<strong>Payment Method</strong>' in new_arch and '>Wire transfer<' in new_arch),
    ('normal 5/6-field maps retained', 'barani_meta_6v' in new_arch and 'barani_meta_6c' in new_arch and 'barani_meta_5' in new_arch),
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
lines.append('  metadata font: 9.5pt/8.5pt -> standard 10pt')
lines.append('  visible date label: Document Date on Q/SO/PF')
lines.append('  rebalance only the seven-field map for normal-size text')
lines.append('  retain Customer Ref. wrap + 14px right padding')
lines.append('  no VAT/RI/DPI, routing, Preview, paperformat, business-record, or table changes')

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
lines.append('S01B COMPLETE: commercial metadata restored to 10pt and Document Date; exact read-back PASS.')
text = NL.join(lines)[:90000]
Param.set_param(OUTPUT_KEY, text)
out = Param.search([('key', '=', OUTPUT_KEY)], limit=1)
action = {
    'type': 'ir.actions.act_window',
    'name': 'S01B BARANI commercial metadata 10pt result',
    'res_model': 'ir.config_parameter',
    'view_mode': 'form',
    'res_id': out.id,
    'target': 'current',
}
