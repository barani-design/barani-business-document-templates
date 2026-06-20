# ============================================================================
# ACTION NAME : BARANI COMMERCIAL Q/SO/PF TUNE L3 — core edge hardening SAFE
# MODEL       : Module (ir.module.module) recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
# CREATE AT   : Settings -> Technical -> Actions -> Server Actions.
# VISIBILITY  : Maintenance-only. Do not bind this tune into Sales/Accounting menus.
# PURPOSE     : Applies only the previously agreed/unambiguous commercial fixes:
#               1) payment band is PF-only (wrapper flag is finally consumed),
#               2) cancelled sale orders retain Quotation classification,
#               3) blank tax descriptions fall back safely to tax names,
#               4) unit price and VAT-rounding warning become currency-aware.
# SCOPE       : standalone BARANI commercial body + Q/SO report filename expression.
#               No stock Odoo/DDS/Studio templates, wrappers, paperformat or VAT views.
# PAGINATION  : PAGE/PAGE_SIZE retained; output normally fits one page.
# SAFETY      : APPLY=False by default. Exact marker/idempotency checks, one-time
#               backup, base-language arch write, exact read-back. Any failure raises
#               UserError before success and rolls back the transaction.
# safe_eval   : no import/def/lambda/comprehension/with/while/getattr/hasattr/
#               setattr/eval/exec/open/try. QWeb expressions are string data.
# ============================================================================

APPLY = False
CONFIRM = ''
APPLY_TOKEN = 'INSTALL_BARANI_COMMERCIAL_Q_SO_PF_TUNE_L3'
PAGE = 1
PAGE_SIZE = 16000

BODY_KEY = 'barani_commercial.report_saleorder_document'
SALE_REPORT_NAME = 'barani_commercial.report_saleorder'
OUTPUT_KEY = 'barani.commercial_report.tune_l3.output'
BK_MARKER = 'barani.commercial_report.tune_l3.backup.marker'
BK_BODY = 'barani.commercial_report.tune_l3.backup.body.arch'
BK_ACTION = 'barani.commercial_report.tune_l3.backup.sale_print_report_name'
NL = chr(10)

Param = env['ir.config_parameter'].sudo()
ViewB = env['ir.ui.view'].sudo().with_context(lang=None)
Rep = env['ir.actions.report'].sudo().with_context(lang=None)
Field = env['ir.model.fields'].sudo()

lines = []
lines.append('BARANI COMMERCIAL Q/SO/PF TUNE L3 — core edge hardening SAFE')
lines.append('APPLY=%s CONFIRM_OK=%s PAGE=%s' % (APPLY, CONFIRM == APPLY_TOKEN, PAGE))
lines.append('Policy: payment band PF-only; cancelled state remains Quotation.')
lines.append('')

problems = 0
body_views = ViewB.search([('key', '=', BODY_KEY), ('type', '=', 'qweb')], limit=2)
reports = Rep.search([('report_name', '=', SALE_REPORT_NAME)], limit=2)
if len(body_views) != 1:
    lines.append('BODY RESOLVE found=%s expected=1 -- ABORT' % len(body_views))
    problems = problems + 1
if len(reports) != 1:
    lines.append('REPORT RESOLVE found=%s expected=1 -- ABORT' % len(reports))
    problems = problems + 1
if problems:
    raise UserError(NL.join(lines)[:90000])

body = body_views[0]
report = reports[0]
old_arch = body.arch_db or ''
old_print = report.print_report_name or ''
lines.append('DISCOVERY')
lines.append('  body id=%s name=%s inherit_id=%s arch_len=%s write_date=%s' % (body.id, repr(body.name), bool(body.inherit_id), len(old_arch), body.write_date))
lines.append('  report id=%s name=%s print_report_name=%s' % (report.id, repr(report.name), repr(old_print)))
if body.inherit_id:
    lines.append('  FAIL: body is not standalone.')
    problems = problems + 1
if not old_arch.startswith('<t t-name="' + BODY_KEY + '"'):
    lines.append('  FAIL: body root t-name mismatch.')
    problems = problems + 1

# ---- Exact old/new markers ----
OLD_STATE = "('draft', 'sent')"
NEW_STATE = "('draft', 'sent', 'cancel')"
OLD_BAND = 't-if="barani_receiving_bank_ok or barani_pdf_payment_ref"'
NEW_BAND = 't-if="barani_show_payment_band and (barani_receiving_bank_ok or barani_pdf_payment_ref)"'
OLD_TAX = '<td name="td_vatrate" class="text-end"><span class="text-nowrap" t-esc="\', \'.join(line.tax_id.mapped(\'description\'))"/></td>'
NEW_TAX = '<td name="td_vatrate" class="text-end"><t t-set="barani_tax_labels" t-value="line.tax_id.filtered(\'description\').mapped(\'description\') or line.tax_id.mapped(\'name\')"/><span class="text-nowrap" t-esc="\', \'.join(barani_tax_labels)"/></td>'
OLD_PRICE = '<td name="td_priceunit" class="text-end"><span class="text-nowrap" name="barani_unit_price_currency"><span t-field="line.price_unit" t-options="{&quot;widget&quot;: &quot;float&quot;, &quot;precision&quot;: 2}"/> <span t-esc="o.currency_id.symbol"/></span></td>'
NEW_PRICE = '<td name="td_priceunit" class="text-end"><span class="text-nowrap" name="barani_unit_price_currency"><span t-esc="line.price_unit" t-options="{&quot;widget&quot;: &quot;monetary&quot;, &quot;display_currency&quot;: o.currency_id}"/></span></td>'
OLD_ROUND = '<p t-if="(barani_line_vat_sum - o.amount_tax) &gt; 0.005 or (o.amount_tax - barani_line_vat_sum) &gt; 0.005" class="text-muted"'
NEW_ROUND = '<p t-if="not o.currency_id.is_zero(barani_line_vat_sum - o.amount_tax)" class="text-muted"'
OLD_PRINT = "('Quotation - ' if object.state in ('draft','sent') else 'Sales Order - ') + (object.name or '')"
NEW_PRINT = "('Quotation - ' if object.state in ('draft','sent','cancel') else 'Sales Order - ') + (object.name or '')"

new_arch = old_arch
state_old_count = new_arch.count(OLD_STATE)
state_new_count = new_arch.count(NEW_STATE)
if state_old_count:
    new_arch = new_arch.replace(OLD_STATE, NEW_STATE)
elif state_new_count < 3:
    lines.append('STATE MARKER FAIL: old_count=%s new_count=%s' % (state_old_count, state_new_count))
    problems = problems + 1

if OLD_BAND in new_arch:
    new_arch = new_arch.replace(OLD_BAND, NEW_BAND, 1)
elif NEW_BAND not in new_arch:
    lines.append('PAYMENT BAND MARKER FAIL')
    problems = problems + 1

if OLD_TAX in new_arch:
    new_arch = new_arch.replace(OLD_TAX, NEW_TAX, 1)
elif NEW_TAX not in new_arch:
    lines.append('TAX LABEL MARKER FAIL')
    problems = problems + 1

if OLD_PRICE in new_arch:
    new_arch = new_arch.replace(OLD_PRICE, NEW_PRICE, 1)
elif NEW_PRICE not in new_arch:
    lines.append('UNIT PRICE MARKER FAIL')
    problems = problems + 1

if OLD_ROUND in new_arch:
    new_arch = new_arch.replace(OLD_ROUND, NEW_ROUND, 1)
elif NEW_ROUND not in new_arch:
    lines.append('ROUNDING MARKER FAIL')
    problems = problems + 1

new_print = old_print
if old_print == OLD_PRINT:
    new_print = NEW_PRINT
elif old_print != NEW_PRINT:
    lines.append('PRINT NAME MARKER FAIL live=%s' % repr(old_print))
    problems = problems + 1

lines.append('')
lines.append('PATCH ANALYSIS')
lines.append('  cancelled-state tuple old occurrences=%s new occurrences_before=%s' % (state_old_count, state_new_count))
lines.append('  payment band consumes PF wrapper flag=%s' % (NEW_BAND in new_arch))
lines.append('  tax label safe fallback=%s' % (NEW_TAX in new_arch))
lines.append('  unit price monetary/currency-aware=%s' % (NEW_PRICE in new_arch))
lines.append('  VAT rounding uses currency.is_zero=%s' % (NEW_ROUND in new_arch))
lines.append('  Q/SO filename treats cancel as Quotation=%s' % (new_print == NEW_PRINT))

# ---- Field preflight ----
lines.append('')
lines.append('FIELD PREFLIGHT')
for item in [('account.tax','description'), ('account.tax','name'), ('sale.order','state'), ('sale.order','currency_id'), ('sale.order.line','price_unit')]:
    fs = Field.search([('model', '=', item[0]), ('name', '=', item[1])], limit=1)
    lines.append('  %s.%s: %s' % (item[0], item[1], 'PASS' if fs else 'FAIL'))
    if not fs:
        problems = problems + 1

# ---- Structural self-check ----
checks = [
    ('standalone BARANI root', new_arch.startswith('<t t-name="' + BODY_KEY + '"')),
    ('no stock sale body', 'sale.report_saleorder_document' not in new_arch),
    ('no web.external_layout', 'web.external_layout' not in new_arch),
    ('no account.document_tax_totals', 'account.document_tax_totals' not in new_arch),
    ('no DDS prefix', 'dds_' not in new_arch),
    ('no Studio custom path', '.x_studio_' not in new_arch),
    ('no BRN prefix', 'brn_' not in new_arch),
    ('cancel tuple present', new_arch.count(NEW_STATE) >= 3),
    ('PF-only payment band gate', NEW_BAND in new_arch),
    ('safe tax fallback', NEW_TAX in new_arch),
    ('currency-aware unit price', NEW_PRICE in new_arch),
    ('currency-aware rounding', NEW_ROUND in new_arch),
]
lines.append('')
lines.append('TEMPLATE SELF-CHECK')
for c in checks:
    lines.append('  %s: %s' % (c[0], 'PASS' if c[1] else 'FAIL'))
    if not c[1]:
        problems = problems + 1

# ---- One-time backup consistency ----
marker = bool(Param.get_param(BK_MARKER))
body_bk = Param.search([('key', '=', BK_BODY)], limit=1)
action_bk = Param.search([('key', '=', BK_ACTION)], limit=1)
if marker and (not body_bk or not action_bk):
    lines.append('BACKUP FAIL: marker exists but one or more backup keys are missing.')
    problems = problems + 1
elif (not marker) and (body_bk or action_bk):
    lines.append('BACKUP FAIL: orphan backup key(s) exist without marker.')
    problems = problems + 1
else:
    lines.append('BACKUP state=%s' % ('COMPLETE_PRESERVED' if marker else 'ABSENT_READY'))

if problems:
    lines.append('')
    lines.append('ERROR: %s preflight problem(s). Refusing before any write.' % problems)
    raise UserError(NL.join(lines)[:90000])

body_change = (new_arch != old_arch)
action_change = (new_print != old_print)
lines.append('')
lines.append('PLAN')
lines.append('  body write needed=%s old_len=%s new_len=%s delta=%s' % (body_change, len(old_arch), len(new_arch), len(new_arch) - len(old_arch)))
lines.append('  Q/SO report print expression write needed=%s' % action_change)
lines.append('  wrappers/layout/paperformat/VAT/stock/DDS/Studio: untouched')

if not APPLY or CONFIRM != APPLY_TOKEN:
    lines.append('')
    lines.append('DRY RUN COMPLETE: no writes performed.')
    lines.append('Set APPLY=True and CONFIRM=INSTALL_BARANI_COMMERCIAL_Q_SO_PF_TUNE_L3 to apply.')
    raise UserError(NL.join(lines)[:90000])

if not marker:
    Param.set_param(BK_BODY, old_arch)
    Param.set_param(BK_ACTION, old_print)
    Param.set_param(BK_MARKER, '1')
    if (Param.search([('key', '=', BK_BODY)], limit=1).value or '') != old_arch:
        raise UserError('Backup read-back failed for body arch; transaction rolled back.')
    if (Param.search([('key', '=', BK_ACTION)], limit=1).value or '') != old_print:
        raise UserError('Backup read-back failed for print expression; transaction rolled back.')
    if Param.get_param(BK_MARKER) != '1':
        raise UserError('Backup marker read-back failed; transaction rolled back.')
    lines.append('PASS: one-time pre-L3 backup stored with exact read-back.')
else:
    lines.append('PASS: existing complete pre-L3 backup preserved.')

if body_change:
    body.write({'arch_db': new_arch})
if action_change:
    report.write({'print_report_name': new_print})

env.flush_all()
ViewB.invalidate_model(['arch_db'])
Rep.invalidate_model(['print_report_name'])

rb = 0
if (ViewB.browse(body.id).arch_db or '') != new_arch:
    lines.append('READ-BACK FAIL: body arch mismatch.')
    rb = rb + 1
if (Rep.browse(report.id).print_report_name or '') != new_print:
    lines.append('READ-BACK FAIL: report print expression mismatch.')
    rb = rb + 1
if rb:
    raise UserError((NL.join(lines) + NL + 'READ-BACK FAILED count=%s; transaction rolled back.' % rb)[:90000])

lines.append('TUNE L3 COMPLETE: exact read-back PASS.')
lines.append('TEST: print one cancelled quotation, one ordinary quotation/SO, and one PF. The bank band must appear only on PF.')
text = NL.join(lines)[:90000]
Param.set_param(OUTPUT_KEY, text)
p = Param.search([('key', '=', OUTPUT_KEY)], limit=1)
action = {'type': 'ir.actions.act_window', 'name': 'BARANI Commercial Tune L3 result', 'res_model': 'ir.config_parameter', 'view_mode': 'form', 'res_id': p.id, 'target': 'current'}
