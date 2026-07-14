# ============================================================================
# ACTION NAME : F99 RESTORE — Remove BARANI future Payment Ref + Valid Until runtime SAFE
# MODEL       : Module (ir.module.module) recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
# PURPOSE     : Removes only the runtime records created by F01:
#               - future sale.order Payment Ref automation/server action;
#               - inherited sale.order Valid Until form view.
#
# IMPORTANT BUSINESS-DATA POLICY:
#   References already assigned to future Sales Orders/invoices while F01 was
#   active are valid standard Odoo business data and are NOT cleared/reverted.
#   Historical records are never modified by F99.
#
# NO TOUCH: report routing, Preview, QWeb templates, Delivery Note, DDS fields.
# ============================================================================

APPLY = False
CONFIRM = ''
CONFIRM_TOKEN = 'RESTORE_REMOVE_BARANI_FUTURE_PAYMENT_REF_VALIDITY_RUNTIME_F99'

F00_MARKER = 'barani.future_ref_validity.f00.marker'
F00_PREFIX = 'barani.future_ref_validity.f00.'
F01_MARKER = 'barani.future_ref_validity.f01.marker'
MARKER = 'barani.future_ref_validity.f99.marker'
OUTPUT_KEY = 'barani.future_ref_validity.f99.output'

RUNTIME_MODULE = 'barani_runtime'
AUTO_XID = 'sale_order_future_payment_ref_automation'
SERVER_XID = 'sale_order_future_payment_ref_server_action'
VIEW_XID = 'view_order_form_valid_until_visible'

NL = chr(10)
SEP = chr(31)
Param = env['ir.config_parameter'].sudo()
Data = env['ir.model.data'].sudo().with_context(active_test=False)
Automation = env['base.automation'].sudo().with_context(active_test=False)
Server = env['ir.actions.server'].sudo().with_context(active_test=False)
View = env['ir.ui.view'].sudo().with_context(lang=None, active_test=False)
Report = env['ir.actions.report'].sudo().with_context(lang=None)

lines = []
lines.append('F99 RESTORE — Remove BARANI future Payment Ref + Valid Until runtime SAFE')
lines.append('APPLY=%s CONFIRM_OK=%s' % (APPLY, CONFIRM == CONFIRM_TOKEN))
lines.append('Removes runtime automation/view only; generated standard business references remain.')
lines.append('')
problems = 0

if Param.get_param(F00_MARKER) != '1':
    lines.append('FAIL: F00 marker missing.')
    problems = problems + 1

def report_signature(rec):
    return SEP.join([
        str(rec.id), rec.name or '', rec.model or '', rec.report_type or '',
        rec.report_name or '', rec.report_file or '',
        str(rec.binding_model_id.id if rec.binding_model_id else 0),
        rec.binding_type or '', rec.binding_view_types or '',
        str(rec.paperformat_id.id if rec.paperformat_id else 0),
        ','.join([str(x) for x in sorted(rec.groups_id.ids)]),
    ])

lines.append('A) REPORT ROUTING NO-DRIFT GATE')
preview_actions = Report.search([('model', '=', 'account.move'), ('report_type', '=', 'qweb-html'), ('report_name', '=', 'barani_vat.report_invoice_document_vat')], limit=2)
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

for token, xid in [
    ('std_sale', 'sale.action_report_saleorder'),
    ('std_pf', 'sale.action_report_pro_forma_invoice'),
    ('std_inv', 'account.account_invoices'),
    ('std_inv_np', 'account.account_invoices_without_payment'),
]:
    rec = env.ref(xid, raise_if_not_found=False)
    expected = Param.get_param(F00_PREFIX + 'report.' + token + '.signature') or ''
    ok = bool(rec) and report_signature(rec) == expected
    lines.append('  %s: %s' % (xid, 'PASS' if ok else 'FAIL_DRIFT'))
    if not ok:
        problems = problems + 1

records = []
lines.append('')
lines.append('B) RUNTIME RECORD INVENTORY')
for name, model_name, model_obj in [
    (AUTO_XID, 'base.automation', Automation),
    (SERVER_XID, 'ir.actions.server', Server),
    (VIEW_XID, 'ir.ui.view', View),
]:
    md = Data.search([('module', '=', RUNTIME_MODULE), ('name', '=', name), ('model', '=', model_name)], limit=1)
    rec = model_obj.browse(md.res_id).exists() if md else model_obj.browse([])
    lines.append('  %s.%s model=%s external_id=%s record_id=%s exists=%s' % (
        RUNTIME_MODULE, name, model_name, md.id if md else 0, rec.id if rec else 0, bool(rec)
    ))
    records.append((name, model_name, md, rec))

installed = Param.get_param(F01_MARKER) == '1'
if not installed and not any(row[3] for row in records):
    lines.append('')
    lines.append('NO-OP: F01 runtime is already absent.')
    raise UserError(NL.join(lines)[:90000])

if problems:
    lines.append('')
    lines.append('ERROR: %s preflight problem(s); refusing before writes.' % problems)
    raise UserError(NL.join(lines)[:90000])

lines.append('')
lines.append('PLAN')
lines.append('  remove base.automation first, then its server action, then inherited view')
lines.append('  remove corresponding barani_runtime external IDs')
lines.append('  leave all sale.order.reference and account.move.payment_reference values unchanged')
lines.append('  leave report routing/Preview/QWeb/Delivery Note unchanged')

if not APPLY or CONFIRM != CONFIRM_TOKEN:
    lines.append('')
    lines.append('DRY RUN — no writes performed.')
    lines.append('Apply with APPLY=True and CONFIRM=%s.' % CONFIRM_TOKEN)
    raise UserError(NL.join(lines)[:90000])

# Delete automation child first so delegated server action can be removed safely.
for row in records:
    if row[1] == 'base.automation' and row[3]:
        row[3].unlink()
for row in records:
    if row[1] == 'ir.actions.server' and row[3]:
        row[3].unlink()
for row in records:
    if row[1] == 'ir.ui.view' and row[3]:
        row[3].unlink()
for row in records:
    md = Data.browse(row[2].id).exists() if row[2] else Data.browse([])
    if md:
        md.unlink()
View.clear_caches()

readback_fail = 0
for name, model_name, model_obj in [
    (AUTO_XID, 'base.automation', Automation),
    (SERVER_XID, 'ir.actions.server', Server),
    (VIEW_XID, 'ir.ui.view', View),
]:
    md = Data.search([('module', '=', RUNTIME_MODULE), ('name', '=', name), ('model', '=', model_name)], limit=1)
    if md:
        lines.append('READ-BACK FAIL external ID remains %s.%s' % (RUNTIME_MODULE, name))
        readback_fail = readback_fail + 1

if readback_fail:
    raise UserError((NL.join(lines) + NL + 'READ-BACK FAILED; transaction rolled back.')[:90000])

Param.set_param(F01_MARKER, '0')
Param.set_param(MARKER, '1')
lines.append('')
lines.append('F99 COMPLETE: future Payment Ref automation and Valid Until inherited view removed; read-back PASS.')
lines.append('Existing standard Payment Ref values generated while active were intentionally preserved.')
text = NL.join(lines)[:90000]
Param.set_param(OUTPUT_KEY, text)
out = Param.search([('key', '=', OUTPUT_KEY)], limit=1)
action = {
    'type': 'ir.actions.act_window',
    'name': 'F99 BARANI future Payment Ref / Valid Until restore result',
    'res_model': 'ir.config_parameter',
    'view_mode': 'form',
    'res_id': out.id,
    'target': 'current',
}
