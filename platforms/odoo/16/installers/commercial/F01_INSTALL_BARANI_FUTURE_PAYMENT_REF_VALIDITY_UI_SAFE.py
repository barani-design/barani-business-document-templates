# ============================================================================
# ACTION NAME : F01 INSTALL — BARANI future Payment Ref + Valid Until UI SAFE
# MODEL       : Module (ir.module.module) recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
# PURPOSE     : Installs only two prospective/customization records:
#
#   1) Future-only base.automation on sale.order creation:
#        if standard sale.order.reference is blank,
#        set it to digits-only sale.order.name.
#      Odoo's standard sale.order._prepare_invoice() then copies reference into
#      account.move.payment_reference for future invoices.
#
#   2) Inherited sale.order form view:
#        expose standard sale.order.validity_date as "Valid Until";
#        editable in draft/sent and read-only in sale/done/cancel.
#
# HISTORICAL POLICY:
#   - No existing sale.order.reference is changed.
#   - No existing account.move.payment_reference is changed.
#   - Current PDF source-derived fallback remains untouched.
#
# NO TOUCH:
#   - Report routing, Print menus, Preview, QWeb templates, Delivery Note.
#   - Preferred Payment Method fixed "Wire transfer" policy.
#   - Any dds_*/Studio/custom business field.
# ============================================================================

APPLY = False
CONFIRM = ''
CONFIRM_TOKEN = 'INSTALL_BARANI_FUTURE_PAYMENT_REF_VALIDITY_UI_F01'

F00_MARKER = 'barani.future_ref_validity.f00.marker'
F00_PREFIX = 'barani.future_ref_validity.f00.'
MARKER = 'barani.future_ref_validity.f01.marker'
PREFIX = 'barani.future_ref_validity.f01.'
OUTPUT_KEY = 'barani.future_ref_validity.f01.output'

RUNTIME_MODULE = 'barani_runtime'
AUTO_XID = 'sale_order_future_payment_ref_automation'
SERVER_XID = 'sale_order_future_payment_ref_server_action'
VIEW_XID = 'view_order_form_valid_until_visible'
VIEW_KEY = 'barani_runtime.sale_order_valid_until_visible'

COMM_QSO = 'barani_commercial.report_saleorder'
COMM_PF = 'barani_commercial.report_saleorder_proforma'
VAT_BODY = 'barani_vat.report_invoice_document_vat'

NL = chr(10)
SEP = chr(31)

Param = env['ir.config_parameter'].sudo()
Report = env['ir.actions.report'].sudo().with_context(lang=None)
View = env['ir.ui.view'].sudo().with_context(lang=None, active_test=False)
Data = env['ir.model.data'].sudo().with_context(active_test=False)
Automation = env['base.automation'].sudo().with_context(active_test=False)
Model = env['ir.model'].sudo()

lines = []
lines.append('F01 INSTALL — BARANI future Payment Ref + Valid Until UI SAFE')
lines.append('APPLY=%s CONFIRM_OK=%s' % (APPLY, CONFIRM == CONFIRM_TOKEN))
lines.append('Future-only standard fields. Existing Sales Orders and invoices remain byte/value unchanged.')
lines.append('')

problems = 0
warnings = 0

if Param.get_param(F00_MARKER) != '1':
    lines.append('FAIL: F00 restore point marker missing.')
    problems = problems + 1
else:
    lines.append('PRECHECK F00 marker: PASS')

def report_signature(rec):
    return SEP.join([
        str(rec.id), rec.name or '', rec.model or '', rec.report_type or '',
        rec.report_name or '', rec.report_file or '',
        str(rec.binding_model_id.id if rec.binding_model_id else 0),
        rec.binding_type or '', rec.binding_view_types or '',
        str(rec.paperformat_id.id if rec.paperformat_id else 0),
        ','.join([str(x) for x in sorted(rec.groups_id.ids)]),
    ])

# ---------------------------------------------------------------------------
# A) Accepted report routing no-drift gate
# ---------------------------------------------------------------------------
lines.append('')
lines.append('A) ACCEPTED ROUTING NO-DRIFT GATE')
route_specs = [
    ('std_sale', 'sale.action_report_saleorder'),
    ('std_pf', 'sale.action_report_pro_forma_invoice'),
    ('std_inv', 'account.account_invoices'),
    ('std_inv_np', 'account.account_invoices_without_payment'),
]
for token, xid in route_specs:
    rec = env.ref(xid, raise_if_not_found=False)
    expected = Param.get_param(F00_PREFIX + 'report.' + token + '.signature') or ''
    current = report_signature(rec) if rec else ''
    ok = bool(rec) and current == expected
    lines.append('  %s: %s' % (xid, 'PASS' if ok else 'FAIL_DRIFT'))
    if not ok:
        problems = problems + 1
# Preserve the accepted BARANI Preview action/view exactly as captured by F00.
preview_actions = Report.search([('model', '=', 'account.move'), ('report_type', '=', 'qweb-html'), ('report_name', '=', VAT_BODY)], limit=2)
preview_views = View.search([('key', '=', 'barani_runtime.account_move_preview_2026_button')], limit=2)
preview_action_ok = len(preview_actions) == 1 and report_signature(preview_actions[0]) == (Param.get_param(F00_PREFIX + 'preview.action.signature') or '')
preview_view_current = ''
if len(preview_views) == 1:
    pv = preview_views[0]
    preview_view_current = SEP.join([str(pv.id), pv.key or '', pv.name or '', pv.model or '', pv.type or '', str(pv.inherit_id.id if pv.inherit_id else 0), str(pv.priority), '1' if pv.active else '0'])
preview_view_ok = len(preview_views) == 1 and preview_view_current == (Param.get_param(F00_PREFIX + 'preview.view.signature') or '')
lines.append('  accepted invoice Preview action: %s' % ('PASS' if preview_action_ok else 'FAIL_DRIFT'))
lines.append('  accepted invoice Preview view: %s' % ('PASS' if preview_view_ok else 'FAIL_DRIFT'))
if not preview_action_ok:
    problems = problems + 1
if not preview_view_ok:
    problems = problems + 1

for token, rid in [('dup_sale', 964), ('dup_pf', 965), ('dup_vat', 918)]:
    rec = Report.browse(rid).exists()
    expected = Param.get_param(F00_PREFIX + 'report.' + token + '.signature') or ''
    current = report_signature(rec) if rec else ''
    ok = bool(rec) and current == expected
    lines.append('  hidden %s id=%s: %s' % (token, rid, 'PASS' if ok else 'FAIL_DRIFT'))
    if not ok:
        problems = problems + 1

# ---------------------------------------------------------------------------
# B) Standard model/view and conflict preflight
# ---------------------------------------------------------------------------
lines.append('')
lines.append('B) STANDARD MODEL / VIEW / CONFLICT PREFLIGHT')
sale_model = Model.search([('model', '=', 'sale.order')], limit=1)
sale_form = env.ref('sale.view_order_form', raise_if_not_found=False)
if not sale_model:
    lines.append('  FAIL: sale.order model missing')
    problems = problems + 1
if not sale_form:
    lines.append('  FAIL: sale.view_order_form missing')
    problems = problems + 1
else:
    base_arch = sale_form.arch_db or ''
    expected_arch = Param.get_param(F00_PREFIX + 'sale_form.arch') or ''
    count_validity = base_arch.count('name="validity_date"') + base_arch.count("name='validity_date'")
    ok = base_arch == expected_arch and count_validity == 1
    lines.append('  sale.view_order_form unchanged / validity occurrence=1: %s' % ('PASS' if ok else 'FAIL'))
    if not ok:
        problems = problems + 1

for fname in ['name', 'reference', 'validity_date', 'state']:
    ok = fname in env['sale.order']._fields
    lines.append('  sale.order.%s: %s' % (fname, 'PASS' if ok else 'FAIL'))
    if not ok:
        problems = problems + 1

existing_data = []
for name, model_name in [
    (AUTO_XID, 'base.automation'),
    (SERVER_XID, 'ir.actions.server'),
    (VIEW_XID, 'ir.ui.view'),
]:
    rows = Data.search([('module', '=', RUNTIME_MODULE), ('name', '=', name)], limit=2)
    if rows:
        existing_data.append((name, model_name, rows))

active_conflicts = []
if sale_model:
    for auto in Automation.search([('model_id', '=', sale_model.id), ('active', '=', True)], order='id'):
        code = auto.action_server_id.code or ''
        low = code.lower()
        if 'reference' in low and ('payment' in low or 'digit' in low or "record.write({'reference'" in low):
            active_conflicts.append(auto)

already_done = Param.get_param(MARKER) == '1'
if already_done:
    lines.append('  F01 marker already present; read-back verification will determine no-op.')
elif existing_data:
    lines.append('  FAIL: planned runtime external IDs already exist while F01 marker is absent.')
    for item in existing_data:
        lines.append('    %s model=%s count=%s' % (item[0], item[1], len(item[2])))
    problems = problems + len(existing_data)
elif active_conflicts:
    lines.append('  FAIL: active sale.order reference-related automation(s) already exist.')
    for auto in active_conflicts:
        lines.append('    id=%s name=%r trigger=%s' % (auto.id, auto.name or '', auto.trigger or ''))
    problems = problems + len(active_conflicts)
else:
    lines.append('  planned runtime records absent / no automation conflict: PASS')

# ---------------------------------------------------------------------------
# C) Desired definitions
# ---------------------------------------------------------------------------
automation_code = NL.join([
    "if record and not record.reference:",
    "    raw_name = record.name or ''",
    "    digits = ''",
    "    for char in raw_name:",
    "        if char >= '0' and char <= '9':",
    "            digits = digits + char",
    "    if digits:",
    "        record.write({'reference': digits})",
])
filter_domain = "[('reference', '=', False)]"
view_arch = NL.join([
    '<data>',
    '  <xpath expr="//field[@name=\'validity_date\']" position="attributes">',
    '    <attribute name="string">Valid Until</attribute>',
    '    <attribute name="attrs">{\'readonly\': [(\'state\', \'in\', [\'sale\', \'done\', \'cancel\'])]}</attribute>',
    '  </xpath>',
    '</data>',
])

# ---------------------------------------------------------------------------
# D) Existing-history reference hashes / cutoff
# ---------------------------------------------------------------------------
lines.append('')
lines.append('C) HISTORICAL VALUE-PRESERVATION SNAPSHOT')
env.cr.execute('SELECT COALESCE(MAX(id), 0) FROM sale_order')
cutoff_sale_id = (env.cr.fetchone() or (0,))[0]
env.cr.execute("SELECT COALESCE(MAX(id), 0) FROM account_move WHERE move_type IN ('out_invoice','out_refund')")
cutoff_move_id = (env.cr.fetchone() or (0,))[0]
env.cr.execute("SELECT COALESCE(md5(string_agg(id::text || ':' || COALESCE(reference, ''), '|' ORDER BY id)), md5('')) FROM sale_order WHERE id <= %s", (cutoff_sale_id,))
sale_hash_before = (env.cr.fetchone() or ('',))[0] or ''
env.cr.execute("SELECT COALESCE(md5(string_agg(id::text || ':' || COALESCE(payment_reference, ''), '|' ORDER BY id)), md5('')) FROM account_move WHERE id <= %s AND move_type IN ('out_invoice','out_refund')", (cutoff_move_id,))
move_hash_before = (env.cr.fetchone() or ('',))[0] or ''
lines.append('  install cutoff sale_order.id=%s' % cutoff_sale_id)
lines.append('  install cutoff customer account_move.id=%s' % cutoff_move_id)
lines.append('  existing sale.order.reference digest captured: YES')
lines.append('  existing account.move.payment_reference digest captured: YES')

# ---------------------------------------------------------------------------
# E) Already-installed read-back / dry-run plan
# ---------------------------------------------------------------------------
if already_done:
    auto_md = Data.search([('module', '=', RUNTIME_MODULE), ('name', '=', AUTO_XID), ('model', '=', 'base.automation')], limit=1)
    srv_md = Data.search([('module', '=', RUNTIME_MODULE), ('name', '=', SERVER_XID), ('model', '=', 'ir.actions.server')], limit=1)
    view_md = Data.search([('module', '=', RUNTIME_MODULE), ('name', '=', VIEW_XID), ('model', '=', 'ir.ui.view')], limit=1)
    auto = Automation.browse(auto_md.res_id).exists() if auto_md else Automation.browse([])
    srv = env['ir.actions.server'].sudo().browse(srv_md.res_id).exists() if srv_md else env['ir.actions.server'].sudo().browse([])
    v = View.browse(view_md.res_id).exists() if view_md else View.browse([])
    complete = bool(auto and srv and v)
    if complete:
        complete = auto.active and auto.trigger == 'on_create' and (auto.filter_domain or '') == filter_domain
        complete = complete and (srv.code or '') == automation_code and srv.model_id == sale_model
        complete = complete and v.active and v.inherit_id == sale_form and (v.arch_db or '') == view_arch and (v.key or '') == VIEW_KEY
    if problems:
        lines.append('')
        lines.append('ERROR: %s problem(s); refusing.' % problems)
        raise UserError(NL.join(lines)[:90000])
    if complete:
        lines.append('')
        lines.append('NO-OP: F01 already installed and exact read-back is complete.')
        raise UserError(NL.join(lines)[:90000])
    lines.append('FAIL: F01 marker exists but runtime state is incomplete.')
    problems = problems + 1

if problems:
    lines.append('')
    lines.append('ERROR: %s preflight problem(s); refusing before writes.' % problems)
    raise UserError(NL.join(lines)[:90000])

lines.append('')
lines.append('PLAN')
lines.append('  create one active on_create base.automation on sale.order')
lines.append('  fill standard sale.order.reference only when blank; digits-only from sale.order.name')
lines.append('  create one inherited form view exposing standard validity_date as Valid Until')
lines.append('  make Valid Until editable in draft/sent and read-only in sale/done/cancel')
lines.append('  do not backfill any existing sale.order or account.move')
lines.append('  do not touch routing, Preview, QWeb, Delivery Note, Preferred Payment Method, or DDS fields')

if not APPLY or CONFIRM != CONFIRM_TOKEN:
    lines.append('')
    lines.append('DRY RUN — no writes performed.')
    lines.append('Apply with APPLY=True and CONFIRM=%s.' % CONFIRM_TOKEN)
    raise UserError(NL.join(lines)[:90000])

# Save cutoffs/hashes before runtime customization creation.
Param.set_param(PREFIX + 'cutoff_sale_id', str(cutoff_sale_id))
Param.set_param(PREFIX + 'cutoff_move_id', str(cutoff_move_id))
Param.set_param(PREFIX + 'sale_reference_hash_before', sale_hash_before)
Param.set_param(PREFIX + 'move_payment_reference_hash_before', move_hash_before)
Param.set_param(PREFIX + 'automation_code', automation_code)
Param.set_param(PREFIX + 'view_arch', view_arch)

# Create delegated Automated Action + Server Action in one operation.
auto_vals = {
    'name': 'BARANI Future Payment Ref — digits from Q/SO number',
    'model_id': sale_model.id,
    'state': 'code',
    'code': automation_code,
    'trigger': 'on_create',
    'filter_domain': filter_domain,
    'active': True,
}
automation = Automation.create(auto_vals)
server_action = automation.action_server_id
Data.create({
    'module': RUNTIME_MODULE,
    'name': AUTO_XID,
    'model': 'base.automation',
    'res_id': automation.id,
    'noupdate': True,
})
Data.create({
    'module': RUNTIME_MODULE,
    'name': SERVER_XID,
    'model': 'ir.actions.server',
    'res_id': server_action.id,
    'noupdate': True,
})

view_vals = {
    'name': 'BARANI Sale Order Valid Until — standard field visible',
    'key': VIEW_KEY,
    'model': 'sale.order',
    'type': 'form',
    'inherit_id': sale_form.id,
    'priority': 900,
    'active': True,
    'arch_db': view_arch,
}
if 'mode' in View._fields:
    view_vals['mode'] = 'extension'
validity_view = View.create(view_vals)
Data.create({
    'module': RUNTIME_MODULE,
    'name': VIEW_XID,
    'model': 'ir.ui.view',
    'res_id': validity_view.id,
    'noupdate': True,
})
View.clear_caches()

# Verify no existing values changed during installation.
env.cr.execute("SELECT COALESCE(md5(string_agg(id::text || ':' || COALESCE(reference, ''), '|' ORDER BY id)), md5('')) FROM sale_order WHERE id <= %s", (cutoff_sale_id,))
sale_hash_after = (env.cr.fetchone() or ('',))[0] or ''
env.cr.execute("SELECT COALESCE(md5(string_agg(id::text || ':' || COALESCE(payment_reference, ''), '|' ORDER BY id)), md5('')) FROM account_move WHERE id <= %s AND move_type IN ('out_invoice','out_refund')", (cutoff_move_id,))
move_hash_after = (env.cr.fetchone() or ('',))[0] or ''

readback_fail = 0
if sale_hash_after != sale_hash_before:
    lines.append('READ-BACK FAIL: existing sale.order.reference digest changed')
    readback_fail = readback_fail + 1
if move_hash_after != move_hash_before:
    lines.append('READ-BACK FAIL: existing account.move.payment_reference digest changed')
    readback_fail = readback_fail + 1
if not automation.active or automation.trigger != 'on_create' or (automation.filter_domain or '') != filter_domain:
    lines.append('READ-BACK FAIL: automation definition')
    readback_fail = readback_fail + 1
if (server_action.code or '') != automation_code or server_action.model_id != sale_model:
    lines.append('READ-BACK FAIL: server action definition')
    readback_fail = readback_fail + 1
if not validity_view.active or validity_view.inherit_id != sale_form or (validity_view.arch_db or '') != view_arch or (validity_view.key or '') != VIEW_KEY:
    lines.append('READ-BACK FAIL: inherited Valid Until view')
    readback_fail = readback_fail + 1
for name, model_name, rid in [
    (AUTO_XID, 'base.automation', automation.id),
    (SERVER_XID, 'ir.actions.server', server_action.id),
    (VIEW_XID, 'ir.ui.view', validity_view.id),
]:
    md = Data.search([('module', '=', RUNTIME_MODULE), ('name', '=', name), ('model', '=', model_name), ('res_id', '=', rid)], limit=1)
    if not md:
        lines.append('READ-BACK FAIL external ID %s.%s' % (RUNTIME_MODULE, name))
        readback_fail = readback_fail + 1

# Re-check routing signatures are unchanged.
for token, xid in route_specs:
    rec = env.ref(xid, raise_if_not_found=False)
    expected = Param.get_param(F00_PREFIX + 'report.' + token + '.signature') or ''
    if not rec or report_signature(rec) != expected:
        lines.append('READ-BACK FAIL routing drift %s' % xid)
        readback_fail = readback_fail + 1

if readback_fail:
    raise UserError((NL.join(lines) + NL + 'READ-BACK FAILED; transaction rolled back.')[:90000])

Param.set_param(PREFIX + 'automation_id', str(automation.id))
Param.set_param(PREFIX + 'server_action_id', str(server_action.id))
Param.set_param(PREFIX + 'view_id', str(validity_view.id))
Param.set_param(MARKER, '1')

lines.append('')
lines.append('F01 COMPLETE: future-only standard Payment Ref automation and standard Valid Until UI installed; read-back PASS.')
lines.append('Historical sale.order.reference and account.move.payment_reference digests: UNCHANGED.')
lines.append('Manual next step: create a NEW quotation, confirm Valid Until visibility, then create its invoice and verify matching Payment Reference.')
text = NL.join(lines)[:90000]
Param.set_param(OUTPUT_KEY, text)
out = Param.search([('key', '=', OUTPUT_KEY)], limit=1)
action = {
    'type': 'ir.actions.act_window',
    'name': 'F01 BARANI future Payment Ref / Valid Until install result',
    'res_model': 'ir.config_parameter',
    'view_mode': 'form',
    'res_id': out.id,
    'target': 'current',
}
