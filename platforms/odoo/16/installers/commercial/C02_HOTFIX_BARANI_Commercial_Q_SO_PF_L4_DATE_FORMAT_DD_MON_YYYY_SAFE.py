# ============================================================================
# ACTION NAME : C02 HOTFIX — BARANI Commercial Q/SO/PF L4 date format SAFE
# MODEL       : Module (ir.module.module) recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
# PURPOSE     : Updates BARANI commercial Q/SO/PF date rendering from locale /
#               browser-style numeric dates to fixed English uppercase
#               DD MON YYYY format.
#
# TARGET FORMAT:
#   06/30/2026 -> 30 JUN 2026
#   07/30/2026 -> 30 JUL 2026
#   06/09/2026 -> 09 JUN 2026
#   06/04/2026 -> 04 JUN 2026
#
# SCOPE:
#   - barani_commercial.report_saleorder_document ONLY
#       * Quotation / Order / Pro-Forma date from sale.order.date_order
#       * Valid Until from sale.order.validity_date
#
# NO TOUCH:
#   - RI/DPI/VAT QWeb views.
#   - Business records.
#   - Payment references.
#   - Legal document numbers.
#   - Report actions, wrappers, external layouts, paperformats.
#   - Stock Odoo, DDS, Studio, DN/PickOps, Intrastat.
#
# SAFETY:
#   - APPLY=False default.
#   - Requires B01 L4 restore point.
#   - One-time backup for the commercial body view only.
#   - Base-language QWeb write.
#   - Marker-based stored read-back.
# ============================================================================

APPLY = False
CONFIRM = ''
CONFIRM_TOKEN = 'INSTALL_BARANI_COMMERCIAL_Q_SO_PF_L4_DATE_FORMAT_C02'
PAGE = 1

BODY_KEY = 'barani_commercial.report_saleorder_document'
RP_MARKER = 'barani.l4.restore_point.marker'
BK_MARKER = 'barani.l4.c02.date_format.comm.backup.marker'
BK_BODY = 'barani.l4.c02.date_format.comm.backup.body.arch'
OUT_KEY = 'barani.l4.c02.date_format.comm.output'
OLD_COMBINED_MARKER = 'barani.l4.date_format.c02_d03.backup.marker'
NL = chr(10)

MONTHS_QWEB = '<t t-set="barani_date_months" t-value="(\'JAN\',\'FEB\',\'MAR\',\'APR\',\'MAY\',\'JUN\',\'JUL\',\'AUG\',\'SEP\',\'OCT\',\'NOV\',\'DEC\')"/>'

Param = env['ir.config_parameter'].sudo()
View = env['ir.ui.view'].sudo().with_context(lang=None)
Field = env['ir.model.fields'].sudo()

lines = []
lines.append('C02 HOTFIX — BARANI Commercial Q/SO/PF L4 date format SAFE')
lines.append('APPLY=%s CONFIRM_OK=%s PAGE=%s' % (APPLY, CONFIRM == CONFIRM_TOKEN, PAGE))
lines.append('Target examples: 06/30/2026 -> 30 JUN 2026; 06/09/2026 -> 09 JUN 2026.')
lines.append('Scope: commercial Q/SO/PF body view only; RI/DPI/VAT untouched.')
lines.append('')

problems = 0
if Param.get_param(RP_MARKER) != '1':
    lines.append('FAIL: B01 L4 restore point marker missing. Run B01 first.')
    problems = problems + 1

if Param.get_param(OLD_COMBINED_MARKER) == '1':
    lines.append('WARN: prior combined C02+D03 marker exists. This commercial-only action will not undo any RI/DPI/VAT date-format changes already applied.')

body_rs = View.search([('key', '=', BODY_KEY), ('type', '=', 'qweb')], limit=2)
if len(body_rs) != 1:
    lines.append('FAIL: commercial body views found=%s expected=1' % len(body_rs))
    problems = problems + 1

field_checks = [
    ('sale.order', 'date_order'),
    ('sale.order', 'validity_date'),
]
lines.append('FIELD PREFLIGHT')
for fc in field_checks:
    f = Field.search([('model', '=', fc[0]), ('name', '=', fc[1])], limit=1)
    lines.append('  %s.%s: %s' % (fc[0], fc[1], 'PASS' if f else 'FAIL'))
    if not f:
        problems = problems + 1

if problems:
    raise UserError(NL.join(lines)[:90000])

body = body_rs[0]
old_arch = body.arch_db or ''
new_arch = old_arch

lines.append('')
lines.append('DISCOVERY')
lines.append('  commercial body id=%s key=%s len=%s write_date=%s inherit_id=%s' % (
    body.id, BODY_KEY, len(old_arch), body.write_date, bool(body.inherit_id)
))

# ---------------------------------------------------------------------------
# Insert fixed English month tuple once near the sale.order alias.
# ---------------------------------------------------------------------------
if 'barani_date_months' in new_arch:
    pass
else:
    o_marker = '<t t-set="o" t-value="doc"/>'
    if o_marker in new_arch:
        new_arch = new_arch.replace(o_marker, o_marker + NL + '  ' + MONTHS_QWEB, 1)
    else:
        lines.append('FAIL: commercial o/doc marker for date month tuple not found.')
        problems = problems + 1

# ---------------------------------------------------------------------------
# Document date: Quotation Date / Order Date / Pro-Forma Date.
# Uses context_timestamp for the datetime sale.order.date_order, then prints
# DD MON YYYY with fixed English month abbreviations.
# ---------------------------------------------------------------------------
doc_date_old = '<p class="m-0"><span t-field="o.date_order" t-options="{&quot;widget&quot;: &quot;date&quot;}"/></p>'
doc_date_new = '''<t t-set="barani_doc_date_local" t-value="context_timestamp(o.date_order) if o.date_order else False"/><t t-set="barani_doc_date_display" t-value="('%02d %s %04d' % (barani_doc_date_local.day, barani_date_months[barani_doc_date_local.month - 1], barani_doc_date_local.year)) if barani_doc_date_local else ''"/><p class="m-0"><span t-esc="barani_doc_date_display"/></p>'''
if 'barani_doc_date_display' in new_arch:
    pass
elif doc_date_old in new_arch:
    new_arch = new_arch.replace(doc_date_old, doc_date_new, 1)
else:
    doc_pos = new_arch.find('name="doc_date"')
    p_start = new_arch.find('<p class="m-0"', doc_pos)
    p_end_self = new_arch.find('/>', p_start)
    p_end_full = new_arch.find('</p>', p_start)
    div_end = new_arch.find('</div>', p_start)
    if doc_pos != -1 and p_start != -1 and div_end != -1 and p_start < div_end:
        replace_end = -1
        if p_end_full != -1 and p_end_full < div_end:
            replace_end = p_end_full + 4
        elif p_end_self != -1 and p_end_self < div_end:
            replace_end = p_end_self + 2
        if replace_end != -1:
            new_arch = new_arch[:p_start] + doc_date_new + new_arch[replace_end:]
        else:
            lines.append('FAIL: commercial doc date <p> end marker not found.')
            problems = problems + 1
    else:
        lines.append('FAIL: commercial doc date marker not found.')
        problems = problems + 1

# ---------------------------------------------------------------------------
# Valid Until: sale.order.validity_date is a date, so no timezone conversion.
# ---------------------------------------------------------------------------
valid_old = '<strong>Valid Until</strong><p class="m-0" t-field="o.validity_date"/>'
valid_new = '''<strong>Valid Until</strong><t t-set="barani_valid_until_date" t-value="o.validity_date"/><t t-set="barani_valid_until_display" t-value="('%02d %s %04d' % (barani_valid_until_date.day, barani_date_months[barani_valid_until_date.month - 1], barani_valid_until_date.year)) if barani_valid_until_date else ''"/><p class="m-0"><span t-esc="barani_valid_until_display"/></p>'''
if 'barani_valid_until_display' in new_arch:
    pass
elif valid_old in new_arch:
    new_arch = new_arch.replace(valid_old, valid_new, 1)
else:
    valid_pos = new_arch.find('name="validity_date"')
    p_start2 = new_arch.find('<p class="m-0"', valid_pos)
    p_end_self2 = new_arch.find('/>', p_start2)
    p_end_full2 = new_arch.find('</p>', p_start2)
    div_end2 = new_arch.find('</div>', p_start2)
    if valid_pos != -1 and p_start2 != -1 and div_end2 != -1 and p_start2 < div_end2:
        replace_end2 = -1
        if p_end_full2 != -1 and p_end_full2 < div_end2:
            replace_end2 = p_end_full2 + 4
        elif p_end_self2 != -1 and p_end_self2 < div_end2:
            replace_end2 = p_end_self2 + 2
        if replace_end2 != -1:
            new_arch = new_arch[:p_start2] + '<t t-set="barani_valid_until_date" t-value="o.validity_date"/><t t-set="barani_valid_until_display" t-value="(\'%02d %s %04d\' % (barani_valid_until_date.day, barani_date_months[barani_valid_until_date.month - 1], barani_valid_until_date.year)) if barani_valid_until_date else \'\'"/><p class="m-0"><span t-esc="barani_valid_until_display"/></p>' + new_arch[replace_end2:]
        else:
            lines.append('FAIL: commercial Valid Until <p> end marker not found.')
            problems = problems + 1
    else:
        lines.append('FAIL: commercial Valid Until date marker not found.')
        problems = problems + 1

# ---------------------------------------------------------------------------
# Self checks.
# ---------------------------------------------------------------------------
checks = [
    ('standalone BARANI commercial body root', new_arch.startswith('<t t-name="' + BODY_KEY + '"')),
    ('date month tuple present', 'barani_date_months' in new_arch and 'JAN' in new_arch and 'DEC' in new_arch),
    ('document date formatted', 'barani_doc_date_display' in new_arch and 'context_timestamp(o.date_order)' in new_arch),
    ('Valid Until formatted', 'barani_valid_until_display' in new_arch),
    ('no date widget on date_order', 't-field="o.date_order"' not in new_arch),
    ('no direct validity_date t-field', 't-field="o.validity_date"' not in new_arch),
    ('date labels retained', ('Quotation Date' in new_arch or 'Order Date' in new_arch or 'Pro-Forma Date' in new_arch or 'Pro-forma Date' in new_arch) and 'Valid Until' in new_arch),
    ('Payment Reference retained', 'Payment Reference' in new_arch),
    ('Preferred Payment Method retained', 'Preferred Payment Method' in new_arch),
    ('fixed discount column retained', 'barani_discount_col_fixed' in new_arch),
    ('numeric VAT marker retained', 'barani_numeric_vat_rate_tax.amount' in new_arch),
    ('commercial no stock sale body', 'sale.report_saleorder_document' not in new_arch),
    ('commercial no web.external_layout', 'web.external_layout' not in new_arch),
    ('commercial no account document tax totals', 'account.document_tax_totals' not in new_arch),
    ('commercial no DDS prefix', 'dds_' not in new_arch),
    ('commercial no Studio custom path', '.x_studio_' not in new_arch),
    ('commercial no BRN prefix', 'brn_' not in new_arch),
]
lines.append('')
lines.append('TEMPLATE SELF-CHECK')
for ck in checks:
    lines.append('  %s: %s' % (ck[0], 'PASS' if ck[1] else 'FAIL'))
    if not ck[1]:
        problems = problems + 1

marker = Param.get_param(BK_MARKER)
bk_present = bool(Param.search([('key', '=', BK_BODY)], limit=1))
if marker and not bk_present:
    lines.append('BACKUP FAIL: marker present but C02 commercial backup missing.')
    problems = problems + 1
elif (not marker) and bk_present:
    lines.append('BACKUP FAIL: orphan C02 commercial date-format backup exists.')
    problems = problems + 1
else:
    lines.append('BACKUP state=%s' % ('COMPLETE_PRESERVED' if marker else 'ABSENT_READY'))

if problems:
    lines.append('')
    lines.append('ERROR: %s preflight problem(s). Refusing before writes.' % problems)
    raise UserError(NL.join(lines)[:90000])

write_needed = (new_arch != old_arch)
lines.append('')
lines.append('PLAN')
lines.append('  update commercial body view id=%s only' % body.id)
lines.append('  write_needed=%s old_len=%s new_len=%s delta=%s' % (
    write_needed, len(old_arch), len(new_arch), len(new_arch) - len(old_arch)
))
lines.append('  format: DD MON YYYY using fixed English month abbreviations')
lines.append('  RI/DPI/VAT views, report actions, wrappers, layouts, paperformats and business records untouched')

if (not APPLY) or CONFIRM != CONFIRM_TOKEN:
    lines.append('')
    lines.append('DRY RUN COMPLETE: no writes performed.')
    lines.append('Set APPLY=True and CONFIRM=INSTALL_BARANI_COMMERCIAL_Q_SO_PF_L4_DATE_FORMAT_C02 to apply.')
    raise UserError(NL.join(lines)[:90000])

if not marker:
    Param.set_param(BK_BODY, old_arch)
    Param.set_param(BK_MARKER, '1')
    if (Param.search([('key', '=', BK_BODY)], limit=1).value or '') != old_arch:
        raise UserError('C02 commercial date-format backup read-back failed; rollback.')
    lines.append('PASS: one-time C02 commercial date-format backup stored.')
else:
    lines.append('PASS: existing C02 commercial date-format backup preserved.')

if write_needed:
    body.write({'arch_db': new_arch})

env.flush_all()
View.invalidate_model(['arch_db'])
now = View.browse(body.id).arch_db or ''

readback_checks = [
    ('stored month tuple', 'barani_date_months' in now),
    ('stored document date display', 'barani_doc_date_display' in now),
    ('stored Valid Until display', 'barani_valid_until_display' in now),
    ('stored no date_order t-field', 't-field="o.date_order"' not in now),
    ('stored no validity_date t-field', 't-field="o.validity_date"' not in now),
    ('stored no RI/DPI/VAT key in body', 'barani_vat.report_invoice_document_vat' not in now),
]
rb_fail = 0
for rb in readback_checks:
    if not rb[1]:
        rb_fail = rb_fail + 1
        lines.append('READ-BACK MARKER FAIL: %s' % rb[0])
if rb_fail:
    raise UserError((NL.join(lines) + NL + 'READ-BACK MARKER FAIL count=%s; rollback.' % rb_fail)[:90000])

lines.append('C02 COMPLETE: commercial Q/SO/PF date format updated to DD MON YYYY; read-back markers PASS.')
lines.append('TEST: reprint one Quotation, one Sales Order, and one Pro-Forma; verify examples such as 09 JUN 2026 and 30 JUL 2026.')
text = NL.join(lines)[:90000]
Param.set_param(OUT_KEY, text)
p = Param.search([('key', '=', OUT_KEY)], limit=1)
action = {
    'type': 'ir.actions.act_window',
    'name': 'C02 commercial date-format result',
    'res_model': 'ir.config_parameter',
    'view_mode': 'form',
    'res_id': p.id,
    'target': 'current',
}
