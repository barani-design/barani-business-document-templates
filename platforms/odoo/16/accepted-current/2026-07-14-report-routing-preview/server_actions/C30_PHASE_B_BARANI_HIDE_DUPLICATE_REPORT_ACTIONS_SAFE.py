# ============================================================================
# ACTION NAME : C30 PHASE B — hide duplicate report actions after acceptance SAFE
# MODEL       : Module (ir.module.module) recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
#
# PURPOSE     : After all standard routes and Preview are proven:
#               - unbind duplicate custom Q/SO, PF and VAT "— 2026+" actions;
#               - unbind the standard "Invoices without Payment" Print entry
#                 while keeping its XMLID/action internally routed to BARANI;
#               - simplify Delivery Note user-facing action name.
#
# THIS ACTION DOES NOT:
#   - delete report actions;
#   - rename/archive QWeb templates (that is C31, last);
#   - change standard action names/XMLIDs;
#   - modify business records.
# ============================================================================

APPLY = False
CONFIRM = ''
CONFIRM_TOKEN = 'HIDE_BARANI_DUPLICATE_REPORT_ACTIONS_C30'
PAGE = 1
PAGE_SIZE = 60000

MANUAL_SALES_PRINT_PASS = False
MANUAL_ACCOUNTING_PRINT_PASS = False
MANUAL_SEND_PRINT_PASS = False
MANUAL_EMAIL_ATTACHMENTS_PASS = False
MANUAL_PREVIEW_PASS = False
MANUAL_ROLLBACK_REVIEWED = False

C10_MARKER = 'barani.report_routing_preview.c10.standard_relink.marker'
C20_MARKER = 'barani.report_routing_preview.c20.preview_html.marker'
C30_MARKER = 'barani.report_routing_preview.c30.hide_duplicates.marker'
OUT_KEY = 'barani.report_routing_preview.c30.hide_duplicates.output'
NL = chr(10)

Param = env['ir.config_parameter'].sudo()
Report = env['ir.actions.report'].sudo().with_context(active_test=False)

lines = []
lines.append('C30 PHASE B — hide duplicate report actions after acceptance SAFE')
lines.append('APPLY=%s CONFIRM_OK=%s PAGE=%s' % (
    APPLY, CONFIRM == CONFIRM_TOKEN, PAGE
))
lines.append('Policy: unbind only; no deletion; QWeb archive-labeling is deferred to C31.')
lines.append('')

problems = 0
warnings = 0

for key in [C10_MARKER, C20_MARKER]:
    if (Param.get_param(key) or '') != '1':
        lines.append('FAIL: required marker missing: %s' % key)
        problems = problems + 1
if Param.get_param(C30_MARKER) == '1':
    lines.append('FAIL: C30 marker already exists. Do not rerun.')
    problems = problems + 1

manual_checks = [
    ('MANUAL_SALES_PRINT_PASS', MANUAL_SALES_PRINT_PASS),
    ('MANUAL_ACCOUNTING_PRINT_PASS', MANUAL_ACCOUNTING_PRINT_PASS),
    ('MANUAL_SEND_PRINT_PASS', MANUAL_SEND_PRINT_PASS),
    ('MANUAL_EMAIL_ATTACHMENTS_PASS', MANUAL_EMAIL_ATTACHMENTS_PASS),
    ('MANUAL_PREVIEW_PASS', MANUAL_PREVIEW_PASS),
    ('MANUAL_ROLLBACK_REVIEWED', MANUAL_ROLLBACK_REVIEWED),
]
lines.append('MANUAL ACCEPTANCE FLAGS')
for ck in manual_checks:
    lines.append('  %s=%s' % (ck[0], ck[1]))
    if not ck[1]:
        problems = problems + 1
lines.append('')

standard_ids = []
for xmlid in [
    'sale.action_report_saleorder',
    'sale.action_report_pro_forma_invoice',
    'account.account_invoices',
    'account.account_invoices_without_payment',
]:
    rec = env.ref(xmlid, raise_if_not_found=False)
    if rec:
        standard_ids.append(rec.id)
    else:
        lines.append('FAIL: missing standard action %s' % xmlid)
        problems = problems + 1

duplicate_specs = [
    ('sale.order', 'barani_commercial.report_saleorder', 'custom Q/SO duplicate'),
    ('sale.order', 'barani_commercial.report_saleorder_proforma', 'custom PF duplicate'),
    ('account.move', 'barani_vat.report_invoice_document_vat', 'custom VAT RI/DPI duplicate'),
]

plan = []
lines.append('DUPLICATE CUSTOM ACTIONS')
for spec in duplicate_specs:
    rs = Report.search([
        ('model', '=', spec[0]),
        ('report_name', '=', spec[1]),
        ('report_type', '=', 'qweb-pdf'),
    ], order='id asc')
    found_custom = 0
    for rr in rs:
        if rr.id not in standard_ids:
            found_custom = found_custom + 1
            visible = bool(rr.binding_model_id and rr.binding_type == 'report')
            lines.append('  %s id=%s name=%r visible=%s' % (
                spec[2], rr.id, rr.name or '', visible
            ))
            if visible:
                plan.append((rr, {'binding_model_id': False}, 'unbind duplicate custom Print entry'))
    if found_custom == 0:
        lines.append('  WARN: no non-standard action found for %s' % spec[1])
        warnings = warnings + 1
lines.append('')

without_action = env.ref('account.account_invoices_without_payment', raise_if_not_found=False)
if without_action:
    lines.append('STANDARD INVOICES WITHOUT PAYMENT')
    lines.append('  id=%s name=%r report_name=%s bound=%s' % (
        without_action.id, without_action.name or '', without_action.report_name or '',
        without_action.binding_model_id.model if without_action.binding_model_id else ''
    ))
    if without_action.binding_model_id:
        plan.append((without_action, {'binding_model_id': False}, 'hide duplicate standard Print entry but preserve XMLID/internal BARANI route'))
else:
    problems = problems + 1

delivery_actions = Report.search([
    ('model', '=', 'sale.order'),
    ('report_name', '=', 'barani_delivery.report_sale_order_delivery_note_2026'),
    ('report_type', '=', 'qweb-pdf'),
], order='id asc')
lines.append('DELIVERY NOTE ACTION')
if len(delivery_actions) != 1:
    lines.append('  FAIL: expected exactly one BARANI Delivery Note action; found=%s' % len(delivery_actions))
    problems = problems + 1
else:
    dn = delivery_actions[0]
    lines.append('  id=%s current_name=%r bound=%s' % (
        dn.id, dn.name or '', dn.binding_model_id.model if dn.binding_model_id else ''
    ))
    if (dn.name or '') != 'Delivery Note':
        plan.append((dn, {'name': 'Delivery Note'}, 'simplify user-facing Delivery Note label'))
    if not dn.binding_model_id:
        lines.append('  FAIL: Delivery Note must remain bound and visible.')
        problems = problems + 1
lines.append('')

lines.append('WRITE PLAN')
for item in plan:
    lines.append('  id=%s name=%r values=%s reason=%s' % (
        item[0].id, item[0].name or '', item[1], item[2]
    ))
lines.append('  planned report action writes=%s' % len(plan))
lines.append('  deletions=0')
lines.append('  QWeb view writes=0')
lines.append('  standard XMLID changes=0')
lines.append('  business record writes=0')
lines.append('  warnings=%s problems=%s' % (warnings, problems))

if problems:
    full = NL.join(lines)
    start = (PAGE - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    more = 'YES' if end < len(full) else 'NO'
    raise UserError(('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s%s%s' % (
        PAGE, start, min(end, len(full)), len(full), more, NL, full[start:end]
    ))[:90000])

if (not APPLY) or CONFIRM != CONFIRM_TOKEN:
    lines.append('')
    lines.append('DRY RUN COMPLETE: no writes performed.')
    lines.append('Set all manual flags True only after V30 and real workflow tests.')
    lines.append('Set APPLY=True and CONFIRM=%s to apply.' % CONFIRM_TOKEN)
    full2 = NL.join(lines)
    start2 = (PAGE - 1) * PAGE_SIZE
    end2 = start2 + PAGE_SIZE
    more2 = 'YES' if end2 < len(full2) else 'NO'
    raise UserError(('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s%s%s' % (
        PAGE, start2, min(end2, len(full2)), len(full2), more2, NL, full2[start2:end2]
    ))[:90000])

try:
    env.cr.execute('SAVEPOINT sp_barani_c30_hide')
    for item in plan:
        item[0].write(item[1])

    env.flush_all()
    Report.invalidate_model()

    failures = 0
    for item in plan:
        rec = Report.browse(item[0].id)
        for field_name in item[1]:
            expected = item[1][field_name]
            actual = rec[field_name]
            if field_name == 'binding_model_id':
                actual_cmp = actual.id if actual else False
            else:
                actual_cmp = actual or False
            if actual_cmp != expected:
                lines.append('READ-BACK FAIL: id=%s field=%s expected=%r actual=%r' % (
                    rec.id, field_name, expected, actual_cmp
                ))
                failures = failures + 1
    if failures:
        raise Exception('C30 read-back failure count=%s' % failures)

    if not env.ref('sale.action_report_saleorder').binding_model_id:
        raise Exception('standard Q/SO action became unbound')
    if not env.ref('sale.action_report_pro_forma_invoice').binding_model_id:
        raise Exception('standard PF action became unbound')
    if not env.ref('account.account_invoices').binding_model_id:
        raise Exception('standard Invoices action became unbound')
    if not delivery_actions[0].binding_model_id:
        raise Exception('Delivery Note became unbound')

    Param.set_param(C30_MARKER, '1')
    if (Param.get_param(C30_MARKER) or '') != '1':
        raise Exception('C30 marker read-back failed')

    env.cr.execute('RELEASE SAVEPOINT sp_barani_c30_hide')
    lines.append('')
    lines.append('READ-BACK PASS: duplicate custom Print actions are unbound')
    lines.append('READ-BACK PASS: Invoices without Payment is hidden but internally retained')
    lines.append('READ-BACK PASS: standard Q/SO, PF, Invoices and Delivery Note remain visible')
    lines.append('C30 COMPLETE: duplicate user-facing Print entries hidden without deleting actions/templates.')
    lines.append('NEXT: run C31 dry-run to archive-label the former stock QWeb wrappers last.')
except Exception as exc:
    try:
        env.cr.execute('ROLLBACK TO SAVEPOINT sp_barani_c30_hide')
        env.cr.execute('RELEASE SAVEPOINT sp_barani_c30_hide')
        try:
            env.invalidate_all()
        except Exception as inv1:
            try:
                env.cache.invalidate()
            except Exception as inv2:
                pass
    except Exception as rb:
        lines.append('ROLLBACK PROBLEM: %s' % str(rb)[:500])
    raise UserError((NL.join(lines) + NL + 'C30 APPLY FAILED AND ROLLED BACK: %s' % str(exc))[:90000])

text = NL.join(lines)[:90000]
Param.set_param(OUT_KEY, text)
out_rec = Param.search([('key', '=', OUT_KEY)], limit=1)
action = {
    'type': 'ir.actions.act_window',
    'name': 'C30 hide duplicate actions result',
    'res_model': 'ir.config_parameter',
    'view_mode': 'form',
    'res_id': out_rec.id,
    'target': 'current',
}
