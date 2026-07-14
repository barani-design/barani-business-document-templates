# ============================================================================
# ACTION NAME : F00 CREATE RESTORE POINT — BARANI future Payment Ref + Valid Until SAFE
# MODEL       : Module (ir.module.module) recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
# PURPOSE     : Creates a one-time technical restore point before installing:
#               - a future-only sale.order on-create automation that fills the
#                 standard sale.order.reference with digits-only sale.order.name;
#               - an inherited sale.order form view that exposes the standard
#                 sale.order.validity_date as "Valid Until" in every state.
#
# CAPTURES / GATES:
#   - Accepted report-routing / Preview state remains untouched.
#   - Planned runtime records are absent.
#   - No active sale.order automation already writes Payment Ref/reference.
#   - Base sale.order form arch and current report/view signatures.
#
# READ/WRITE : Writes only ir.config_parameter when DRY_RUN=False.
# BUSINESS DATA: No sale.order/account.move records are modified.
# HISTORICAL POLICY: Existing references remain unchanged.
# DDS POLICY: No dds_* field is read, restored, created, or referenced.
# ============================================================================

DRY_RUN = True
CONFIRM = ''
CONFIRM_TOKEN = 'CREATE_BARANI_FUTURE_PAYMENT_REF_VALIDITY_RESTORE_POINT_F00'

MARKER = 'barani.future_ref_validity.f00.marker'
PREFIX = 'barani.future_ref_validity.f00.'
OUTPUT_KEY = 'barani.future_ref_validity.f00.output'

RUNTIME_MODULE = 'barani_runtime'
AUTO_XID = 'sale_order_future_payment_ref_automation'
SERVER_XID = 'sale_order_future_payment_ref_server_action'
VIEW_XID = 'view_order_form_valid_until_visible'
VIEW_KEY = 'barani_runtime.sale_order_valid_until_visible'

COMM_QSO = 'barani_commercial.report_saleorder'
COMM_PF = 'barani_commercial.report_saleorder_proforma'
VAT_BODY = 'barani_vat.report_invoice_document_vat'
PREVIEW_VIEW_KEY = 'barani_runtime.account_move_preview_2026_button'

NL = chr(10)
SEP = chr(31)

Param = env['ir.config_parameter'].sudo()
Report = env['ir.actions.report'].sudo().with_context(lang=None)
View = env['ir.ui.view'].sudo().with_context(lang=None, active_test=False)
Data = env['ir.model.data'].sudo().with_context(active_test=False)
Automation = env['base.automation'].sudo().with_context(active_test=False)
Model = env['ir.model'].sudo()

lines = []
lines.append('F00 CREATE RESTORE POINT — BARANI future Payment Ref + Valid Until SAFE')
lines.append('DRY_RUN=%s CONFIRM_OK=%s' % (DRY_RUN, CONFIRM == CONFIRM_TOKEN))
lines.append('Future-only standard-field automation + standard Valid Until UI. Historical records untouched.')
lines.append('')

problems = 0
warnings = 0
values = []
expected = []

def put(key, value):
    full_key = PREFIX + key
    expected.append(full_key)
    values.append((full_key, value if value is not None else ''))

def report_signature(rec):
    return SEP.join([
        str(rec.id),
        rec.name or '',
        rec.model or '',
        rec.report_type or '',
        rec.report_name or '',
        rec.report_file or '',
        str(rec.binding_model_id.id if rec.binding_model_id else 0),
        rec.binding_type or '',
        rec.binding_view_types or '',
        str(rec.paperformat_id.id if rec.paperformat_id else 0),
        ','.join([str(x) for x in sorted(rec.groups_id.ids)]),
    ])

def view_signature(rec):
    return SEP.join([
        str(rec.id),
        rec.key or '',
        rec.name or '',
        rec.model or '',
        rec.type or '',
        str(rec.inherit_id.id if rec.inherit_id else 0),
        str(rec.priority),
        '1' if rec.active else '0',
    ])

# ---------------------------------------------------------------------------
# A) Accepted routing / Preview no-touch gate
# ---------------------------------------------------------------------------
lines.append('A) ACCEPTED ROUTING / PREVIEW NO-TOUCH GATE')
route_specs = [
    ('std_sale', 'sale.action_report_saleorder', COMM_QSO, 'sale.order', True),
    ('std_pf', 'sale.action_report_pro_forma_invoice', COMM_PF, 'sale.order', True),
    ('std_inv', 'account.account_invoices', VAT_BODY, 'account.move', True),
    ('std_inv_np', 'account.account_invoices_without_payment', VAT_BODY, '', False),
]
for spec in route_specs:
    token, xid, target_report, target_binding, must_bind = spec
    rec = env.ref(xid, raise_if_not_found=False)
    ok = bool(rec) and rec.report_name == target_report and rec.report_file == target_report
    if must_bind:
        ok = ok and bool(rec.binding_model_id) and rec.binding_model_id.model == target_binding
    else:
        ok = ok and not rec.binding_model_id
    lines.append('  %s: %s id=%s report=%r binding=%r' % (
        xid, 'PASS' if ok else 'FAIL', rec.id if rec else 0,
        rec.report_name if rec else '', rec.binding_model_id.model if rec and rec.binding_model_id else ''
    ))
    if not ok:
        problems = problems + 1
    elif rec:
        put('report.' + token + '.signature', report_signature(rec))

custom_specs = [
    ('dup_sale', 964, COMM_QSO, 'sale.order'),
    ('dup_pf', 965, COMM_PF, 'sale.order'),
    ('dup_vat', 918, VAT_BODY, 'account.move'),
]
for spec in custom_specs:
    token, rid, target_report, model_name = spec
    rec = Report.browse(rid).exists()
    ok = bool(rec) and rec.report_name == target_report and rec.model == model_name and not rec.binding_model_id
    lines.append('  hidden duplicate %s id=%s: %s binding=%r' % (
        token, rid, 'PASS' if ok else 'FAIL', rec.binding_model_id.model if rec and rec.binding_model_id else ''
    ))
    if not ok:
        problems = problems + 1
    elif rec:
        put('report.' + token + '.signature', report_signature(rec))

preview_actions = Report.search([
    ('model', '=', 'account.move'),
    ('report_type', '=', 'qweb-html'),
    ('report_name', '=', VAT_BODY),
], limit=2)
preview_views = View.search([('key', '=', PREVIEW_VIEW_KEY)], limit=2)
preview_ok = len(preview_actions) == 1 and not preview_actions[0].binding_model_id and len(preview_views) == 1 and preview_views[0].active
lines.append('  BARANI invoice Preview route: %s action_count=%s view_count=%s' % (
    'PASS' if preview_ok else 'FAIL', len(preview_actions), len(preview_views)
))
if not preview_ok:
    problems = problems + 1
else:
    put('preview.action.signature', report_signature(preview_actions[0]))
    put('preview.view.signature', view_signature(preview_views[0]))

# ---------------------------------------------------------------------------
# B) Standard fields and base form
# ---------------------------------------------------------------------------
lines.append('')
lines.append('B) STANDARD FIELD / BASE VIEW PREFLIGHT')
sale_model = Model.search([('model', '=', 'sale.order')], limit=1)
if not sale_model:
    lines.append('  FAIL: ir.model sale.order missing')
    problems = problems + 1
else:
    lines.append('  sale.order model id=%s: PASS' % sale_model.id)

required_fields = ['name', 'reference', 'validity_date', 'state']
for fname in required_fields:
    ok = fname in env['sale.order']._fields
    lines.append('  sale.order.%s: %s' % (fname, 'PASS' if ok else 'FAIL'))
    if not ok:
        problems = problems + 1

sale_form = env.ref('sale.view_order_form', raise_if_not_found=False)
if not sale_form:
    lines.append('  FAIL: sale.view_order_form missing')
    problems = problems + 1
else:
    arch = sale_form.arch_db or ''
    count_validity = arch.count('name="validity_date"') + arch.count("name='validity_date'")
    lines.append('  sale.view_order_form id=%s validity_date_occurrences=%s' % (sale_form.id, count_validity))
    if count_validity != 1:
        problems = problems + 1
    put('sale_form.signature', view_signature(sale_form))
    put('sale_form.arch', arch)

# ---------------------------------------------------------------------------
# C) Planned runtime record absence / conflict scan
# ---------------------------------------------------------------------------
lines.append('')
lines.append('C) PLANNED RUNTIME RECORD ABSENCE / AUTOMATION CONFLICT SCAN')
for name, model_name in [
    (AUTO_XID, 'base.automation'),
    (SERVER_XID, 'ir.actions.server'),
    (VIEW_XID, 'ir.ui.view'),
]:
    rows = Data.search([('module', '=', RUNTIME_MODULE), ('name', '=', name)], limit=2)
    ok = len(rows) == 0
    lines.append('  %s.%s (%s): %s' % (RUNTIME_MODULE, name, model_name, 'ABSENT_READY' if ok else 'FAIL_EXISTS'))
    put('planned.' + name + '.exists', '0' if ok else '1')
    if not ok:
        problems = problems + 1

if sale_model:
    active_automations = Automation.search([('model_id', '=', sale_model.id), ('active', '=', True)], order='id')
else:
    active_automations = Automation.browse([])
conflicts = []
for auto in active_automations:
    code = auto.action_server_id.code or ''
    low = code.lower()
    if 'reference' in low and ('payment' in low or 'digit' in low or "record.write({'reference'" in low):
        conflicts.append(auto)
lines.append('  active sale.order automations=%s; reference-related conflicts=%s' % (len(active_automations), len(conflicts)))
for auto in conflicts:
    lines.append('    FAIL automation id=%s name=%r trigger=%s server_action_id=%s' % (
        auto.id, auto.name or '', auto.trigger or '', auto.action_server_id.id
    ))
if conflicts:
    problems = problems + len(conflicts)

# ---------------------------------------------------------------------------
# D) Current business cutoffs (informational only; no payload copied)
# ---------------------------------------------------------------------------
lines.append('')
lines.append('D) CURRENT BUSINESS CUTOFFS — INFORMATIONAL ONLY')
env.cr.execute('SELECT COALESCE(MAX(id), 0), COUNT(*) FROM sale_order')
sale_stats = env.cr.fetchone() or (0, 0)
env.cr.execute("SELECT COALESCE(MAX(id), 0), COUNT(*) FROM account_move WHERE move_type IN ('out_invoice','out_refund')")
move_stats = env.cr.fetchone() or (0, 0)
lines.append('  sale_order max_id=%s count=%s' % (sale_stats[0], sale_stats[1]))
lines.append('  customer account_move max_id=%s count=%s' % (move_stats[0], move_stats[1]))
put('pre.sale_max_id', str(sale_stats[0]))
put('pre.move_max_id', str(move_stats[0]))

# ---------------------------------------------------------------------------
# E) Restore-point state
# ---------------------------------------------------------------------------
put('meta.version', 'F00-v1')
put('meta.scope', 'future-only standard sale.order.reference automation + standard sale.order.validity_date UI')
marker = Param.get_param(MARKER) or ''
present = 0
missing = []
for key in expected:
    if Param.search([('key', '=', key)], limit=1):
        present = present + 1
    else:
        missing.append(key)

lines.append('')
lines.append('E) RESTORE POINT STATE')
if marker == '1' and not missing:
    state = 'COMPLETE_PRESERVED'
elif marker or present:
    state = 'PARTIAL_INVALID'
    problems = problems + 1
else:
    state = 'ABSENT_READY'
lines.append('  state=%s marker=%r present=%s expected=%s missing=%s' % (
    state, marker, present, len(expected), len(missing)
))

if problems:
    lines.append('')
    lines.append('ERROR: %s preflight problem(s); refusing before writes.' % problems)
    raise UserError(NL.join(lines)[:90000])

if state == 'COMPLETE_PRESERVED':
    lines.append('')
    lines.append('NO-OP: complete F00 restore point already exists and will not be overwritten.')
    raise UserError(NL.join(lines)[:90000])

lines.append('')
lines.append('PLAN')
lines.append('  save accepted routing/Preview signatures and sale.view_order_form bytes')
lines.append('  save runtime-record absence and business cutoffs')
lines.append('  write only ir.config_parameter keys')
lines.append('  do not modify any sale.order, account.move, QWeb, report action, or DDS field')

if DRY_RUN or CONFIRM != CONFIRM_TOKEN:
    lines.append('')
    lines.append('DRY RUN — no parameters written.')
    lines.append('Apply with DRY_RUN=False and CONFIRM=%s.' % CONFIRM_TOKEN)
    raise UserError(NL.join(lines)[:90000])

for key, value in values:
    Param.set_param(key, value)
Param.set_param(MARKER, '1')

readback_fail = 0
for key, value in values:
    row = Param.search([('key', '=', key)], limit=1)
    if not row or (row.value or '') != value:
        lines.append('READ-BACK FAIL key=%s' % key)
        readback_fail = readback_fail + 1
if Param.get_param(MARKER) != '1':
    lines.append('READ-BACK FAIL marker')
    readback_fail = readback_fail + 1
if readback_fail:
    raise UserError((NL.join(lines) + NL + 'READ-BACK FAILED; transaction rolled back.')[:90000])

lines.append('')
lines.append('F00 COMPLETE: future Payment Ref / Valid Until technical restore point created; read-back PASS.')
text = NL.join(lines)[:90000]
Param.set_param(OUTPUT_KEY, text)
out = Param.search([('key', '=', OUTPUT_KEY)], limit=1)
action = {
    'type': 'ir.actions.act_window',
    'name': 'F00 BARANI future Payment Ref / Valid Until restore result',
    'res_model': 'ir.config_parameter',
    'view_mode': 'form',
    'res_id': out.id,
    'target': 'current',
}
