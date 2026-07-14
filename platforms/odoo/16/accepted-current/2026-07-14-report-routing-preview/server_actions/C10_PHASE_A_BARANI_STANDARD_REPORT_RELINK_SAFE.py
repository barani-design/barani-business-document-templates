# ============================================================================
# ACTION NAME : C10 PHASE A — relink standard Odoo report actions to BARANI SAFE
# MODEL       : Module (ir.module.module) recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
#
# PURPOSE     : Keep the standard Odoo report-action XML IDs but route them to
#               the approved BARANI QWeb PDF renderers and BARANI paperformats.
#
# THIS PHASE DOES NOT:
#   - hide/unbind any duplicate custom "— 2026+" action;
#   - rename/archive any old QWeb view;
#   - change the Preview button;
#   - modify business/accounting records.
#
# WITHOUT-PAYMENT POLICY:
#   REVIEW_REQUIRED      = refuses apply.
#   SAME_BARANI_BODY     = account.account_invoices_without_payment uses the
#                          same BARANI VAT body and BARANI paperformat.
#   CONTROLLED_WRAPPER   = uses CONTROLLED_WRAPPER_REPORT_NAME, which must
#                          already exist as exactly one QWeb view.
# ============================================================================

APPLY = False
CONFIRM = ''
CONFIRM_TOKEN = 'INSTALL_BARANI_STANDARD_REPORT_RELINK_C10'
PAGE = 1
PAGE_SIZE = 60000

WITHOUT_PAYMENT_MODE = 'REVIEW_REQUIRED'
CONTROLLED_WRAPPER_REPORT_NAME = ''

SNAPSHOT_CODE = 'pre_standard_relink_preview_2026_07_14'
PREFIX = 'barani.report_routing_preview.restore.' + SNAPSHOT_CODE
B10_MARKER = PREFIX + '.marker'
C10_MARKER = 'barani.report_routing_preview.c10.standard_relink.marker'
OUT_KEY = 'barani.report_routing_preview.c10.standard_relink.output'
NL = chr(10)

Param = env['ir.config_parameter'].sudo()
Report = env['ir.actions.report'].sudo().with_context(active_test=False)
View = env['ir.ui.view'].sudo().with_context(active_test=False, lang=None)
Model = env['ir.model'].sudo().with_context(active_test=False)

lines = []
lines.append('C10 PHASE A — relink standard Odoo report actions to BARANI SAFE')
lines.append('APPLY=%s CONFIRM_OK=%s PAGE=%s WITHOUT_PAYMENT_MODE=%s' % (
    APPLY, CONFIRM == CONFIRM_TOKEN, PAGE, WITHOUT_PAYMENT_MODE
))
lines.append('Policy: keep standard XMLIDs; do not hide duplicates; do not rename templates.')
lines.append('')

problems = 0
warnings = 0

if (Param.get_param(B10_MARKER) or '') != '1':
    lines.append('FAIL: B10 restore point marker missing.')
    problems = problems + 1

if Param.get_param(C10_MARKER) == '1':
    lines.append('FAIL: C10 marker already exists. Do not rerun; verify or restore first.')
    problems = problems + 1

allowed_modes = ['SAME_BARANI_BODY', 'CONTROLLED_WRAPPER']
if WITHOUT_PAYMENT_MODE not in allowed_modes:
    lines.append('FAIL: WITHOUT_PAYMENT_MODE must be set from the P03 audit to SAME_BARANI_BODY or CONTROLLED_WRAPPER.')
    problems = problems + 1
if WITHOUT_PAYMENT_MODE == 'CONTROLLED_WRAPPER' and not CONTROLLED_WRAPPER_REPORT_NAME:
    lines.append('FAIL: CONTROLLED_WRAPPER_REPORT_NAME is required for CONTROLLED_WRAPPER.')
    problems = problems + 1
lines.append('')

sale_model = Model.search([('model', '=', 'sale.order')], limit=1)
move_model = Model.search([('model', '=', 'account.move')], limit=1)
if not sale_model or not move_model:
    lines.append('FAIL: ir.model records for sale.order/account.move are missing.')
    problems = problems + 1

standard_specs = [
    ('sale_qso', 'sale.action_report_saleorder', 'sale.order'),
    ('sale_pf', 'sale.action_report_pro_forma_invoice', 'sale.order'),
    ('account_invoice', 'account.account_invoices', 'account.move'),
    ('account_invoice_without_payment', 'account.account_invoices_without_payment', 'account.move'),
]

lines.append('STANDARD ACTION DRIFT CHECK AGAINST B10')
for spec in standard_specs:
    token = spec[0]
    xmlid = spec[1]
    rec = env.ref(xmlid, raise_if_not_found=False)
    if not rec or rec._name != 'ir.actions.report':
        lines.append('  %s: FAIL — missing' % xmlid)
        problems = problems + 1
    else:
        snap_id = Param.get_param(PREFIX + '.standard.' + token + '.id') or ''
        snap_report_name = Param.get_param(PREFIX + '.standard.' + token + '.original_report_name') or ''
        snap_paper_id = Param.get_param(PREFIX + '.standard.' + token + '.original_paperformat_id') or '0'
        lines.append('  %s id=%s current_report=%s snapshot_report=%s current_paper=%s snapshot_paper=%s' % (
            xmlid, rec.id, rec.report_name or '', snap_report_name,
            rec.paperformat_id.id if rec.paperformat_id else 0, snap_paper_id
        ))
        if str(rec.id) != snap_id:
            lines.append('    FAIL: action id drift from B10.')
            problems = problems + 1
        if (rec.report_name or '') != snap_report_name:
            lines.append('    FAIL: report_name drift from B10; stop and reconcile.')
            problems = problems + 1
        if str(rec.paperformat_id.id if rec.paperformat_id else 0) != snap_paper_id:
            lines.append('    FAIL: paperformat drift from B10; stop and reconcile.')
            problems = problems + 1
lines.append('')

target_specs = [
    ('qso', 'sale.order', 'barani_commercial.report_saleorder'),
    ('pf', 'sale.order', 'barani_commercial.report_saleorder_proforma'),
    ('vat', 'account.move', 'barani_vat.report_invoice_document_vat'),
]
targets = {}
lines.append('APPROVED BARANI TARGET ACTIONS')
for spec in target_specs:
    token = spec[0]
    model_name = spec[1]
    report_name = spec[2]
    rs = Report.search([
        ('model', '=', model_name),
        ('report_name', '=', report_name),
        ('report_type', '=', 'qweb-pdf'),
    ], order='id asc')
    lines.append('  %s count=%s report_name=%s' % (token, len(rs), report_name))
    if len(rs) != 1:
        lines.append('    FAIL: expected exactly one BARANI qweb-pdf action.')
        problems = problems + 1
    else:
        targets[token] = rs[0]
        rr = rs[0]
        lines.append('    id=%s name=%r paper=%r print_name=%r' % (
            rr.id, rr.name or '',
            rr.paperformat_id.name if rr.paperformat_id else '',
            rr.print_report_name or ''
        ))
        if not rr.paperformat_id:
            lines.append('    FAIL: BARANI target action has no paperformat.')
            problems = problems + 1
lines.append('')

without_payment_report_name = 'barani_vat.report_invoice_document_vat'
without_payment_report_file = 'barani_vat.report_invoice_document_vat'
if WITHOUT_PAYMENT_MODE == 'CONTROLLED_WRAPPER':
    wrapper_views = View.search([
        ('type', '=', 'qweb'),
        ('key', '=', CONTROLLED_WRAPPER_REPORT_NAME),
    ])
    lines.append('CONTROLLED WITHOUT-PAYMENT WRAPPER count=%s key=%s' % (
        len(wrapper_views), CONTROLLED_WRAPPER_REPORT_NAME
    ))
    if len(wrapper_views) != 1:
        lines.append('FAIL: controlled wrapper must exist as exactly one QWeb view.')
        problems = problems + 1
    else:
        without_payment_report_name = CONTROLLED_WRAPPER_REPORT_NAME
        without_payment_report_file = CONTROLLED_WRAPPER_REPORT_NAME
lines.append('')

plan = []
if not problems:
    qso = targets['qso']
    pf = targets['pf']
    vat = targets['vat']

    sale_qso = env.ref('sale.action_report_saleorder')
    sale_pf = env.ref('sale.action_report_pro_forma_invoice')
    acc_inv = env.ref('account.account_invoices')
    acc_no = env.ref('account.account_invoices_without_payment')

    plan.append((sale_qso, {
        'report_name': qso.report_name,
        'report_file': qso.report_file or qso.report_name,
        'report_type': 'qweb-pdf',
        'paperformat_id': qso.paperformat_id.id,
        'print_report_name': qso.print_report_name or False,
        'binding_model_id': sale_model.id,
        'binding_type': 'report',
        'binding_view_types': sale_qso.binding_view_types or 'list,form',
    }, 'standard Q/SO XMLID -> approved BARANI Q/SO renderer'))

    plan.append((sale_pf, {
        'report_name': pf.report_name,
        'report_file': pf.report_file or pf.report_name,
        'report_type': 'qweb-pdf',
        'paperformat_id': pf.paperformat_id.id,
        'print_report_name': pf.print_report_name or False,
        'binding_model_id': sale_model.id,
        'binding_type': 'report',
        'binding_view_types': sale_pf.binding_view_types or 'list,form',
    }, 'standard PF XMLID -> approved BARANI PF renderer'))

    plan.append((acc_inv, {
        'report_name': vat.report_name,
        'report_file': vat.report_file or vat.report_name,
        'report_type': 'qweb-pdf',
        'paperformat_id': vat.paperformat_id.id,
        'print_report_name': vat.print_report_name or False,
        'binding_model_id': move_model.id,
        'binding_type': 'report',
        'binding_view_types': acc_inv.binding_view_types or 'list,form',
    }, 'standard invoice XMLID -> approved BARANI RI/DPI/Credit Note renderer'))

    plan.append((acc_no, {
        'report_name': without_payment_report_name,
        'report_file': without_payment_report_file,
        'report_type': 'qweb-pdf',
        'paperformat_id': vat.paperformat_id.id,
        'print_report_name': vat.print_report_name or False,
        'binding_model_id': move_model.id,
        'binding_type': 'report',
        'binding_view_types': acc_no.binding_view_types or 'list,form',
    }, 'standard invoice-without-payment XMLID -> approved audited BARANI route'))

lines.append('WRITE PLAN — STANDARD ACTIONS ONLY')
for item in plan:
    lines.append('  id=%s name=%r values=%s reason=%s' % (
        item[0].id, item[0].name or '', item[1], item[2]
    ))
lines.append('  planned report action writes=%s' % len(plan))
lines.append('  custom BARANI action writes=0')
lines.append('  QWeb view writes=0')
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
    lines.append('Apply only after P03 review and WITHOUT_PAYMENT_MODE approval.')
    lines.append('Set APPLY=True and CONFIRM=%s to apply.' % CONFIRM_TOKEN)
    full2 = NL.join(lines)
    start2 = (PAGE - 1) * PAGE_SIZE
    end2 = start2 + PAGE_SIZE
    more2 = 'YES' if end2 < len(full2) else 'NO'
    raise UserError(('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s%s%s' % (
        PAGE, start2, min(end2, len(full2)), len(full2), more2, NL, full2[start2:end2]
    ))[:90000])

try:
    env.cr.execute('SAVEPOINT sp_barani_c10_relink')
    for item in plan:
        item[0].write(item[1])

    env.flush_all()
    Report.invalidate_model()

    failures = 0
    for item in plan:
        rec = Report.browse(item[0].id)
        vals = item[1]
        item_failures = 0
        for field_name in vals:
            expected = vals[field_name]
            actual = rec[field_name]
            if field_name in ('paperformat_id', 'binding_model_id'):
                actual_cmp = actual.id if actual else False
            else:
                actual_cmp = actual or False
            if actual_cmp != expected:
                lines.append('READ-BACK FAIL: id=%s field=%s expected=%r actual=%r' % (
                    rec.id, field_name, expected, actual_cmp
                ))
                failures = failures + 1
                item_failures = item_failures + 1
        if item_failures == 0:
            lines.append('READ-BACK PASS: standard action id=%s now routes to %s' % (
                rec.id, rec.report_name or ''
            ))

    if failures:
        raise Exception('C10 read-back failure count=%s' % failures)

    Param.set_param(C10_MARKER, '1')
    Param.set_param(C10_MARKER + '.without_payment_mode', WITHOUT_PAYMENT_MODE)
    Param.set_param(C10_MARKER + '.without_payment_report_name', without_payment_report_name)
    if (Param.get_param(C10_MARKER) or '') != '1':
        raise Exception('C10 marker read-back failed')

    env.cr.execute('RELEASE SAVEPOINT sp_barani_c10_relink')
    lines.append('')
    lines.append('C10 COMPLETE: standard Odoo report-action XMLIDs now route to BARANI PDF renderers.')
    lines.append('IMPORTANT: duplicate custom — 2026+ actions remain visible by design.')
    lines.append('NEXT: run C20 dry-run to route the existing Preview button to BARANI qweb-html.')
except Exception as exc:
    try:
        env.cr.execute('ROLLBACK TO SAVEPOINT sp_barani_c10_relink')
        env.cr.execute('RELEASE SAVEPOINT sp_barani_c10_relink')
        try:
            env.invalidate_all()
        except Exception as inv1:
            try:
                env.cache.invalidate()
            except Exception as inv2:
                pass
    except Exception as rb:
        lines.append('ROLLBACK PROBLEM: %s' % str(rb)[:500])
    raise UserError((NL.join(lines) + NL + 'C10 APPLY FAILED AND ROLLED BACK: %s' % str(exc))[:90000])

text = NL.join(lines)[:90000]
Param.set_param(OUT_KEY, text)
out_rec = Param.search([('key', '=', OUT_KEY)], limit=1)
action = {
    'type': 'ir.actions.act_window',
    'name': 'C10 standard report relink result',
    'res_model': 'ir.config_parameter',
    'view_mode': 'form',
    'res_id': out_rec.id,
    'target': 'current',
}
