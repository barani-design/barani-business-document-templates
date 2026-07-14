# ============================================================================
# ACTION NAME : B10 CREATE — BARANI report-routing + Preview restore point SAFE
# MODEL       : Module (ir.module.module) recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
# PURPOSE     : Capture the exact pre-migration state needed to roll back:
#               - four standard Odoo report actions;
#               - BARANI duplicate/custom report actions and Delivery Note;
#               - the four stock QWeb wrapper views currently reached by the
#                 standard actions;
#               - any collision with the planned BARANI HTML Preview records.
#
# SCOPE       : Writes ir.config_parameter restore rows only.
# NO TOUCH    : ir.actions.report, ir.ui.view, mail.template, account.move,
#               sale.order, payments, taxes, journals, POHODA, totals.
#
# RUN         :
#   Dry-run:
#       APPLY = False
#       CONFIRM = ''
#   Apply after full output review:
#       APPLY = True
#       CONFIRM = 'CREATE_BARANI_REPORT_ROUTING_PREVIEW_RESTORE_POINT_B10'
# ============================================================================

APPLY = False
CONFIRM = ''
CONFIRM_TOKEN = 'CREATE_BARANI_REPORT_ROUTING_PREVIEW_RESTORE_POINT_B10'
PAGE = 1
PAGE_SIZE = 60000

SNAPSHOT_CODE = 'pre_standard_relink_preview_2026_07_14'
PREFIX = 'barani.report_routing_preview.restore.' + SNAPSHOT_CODE
MARKER_KEY = PREFIX + '.marker'
OUT_KEY = PREFIX + '.output'
CURRENT_KEY = 'barani.report_routing_preview.restore.current'
SEP = chr(31)
NL = chr(10)

PREVIEW_REPORT_NAME = 'BARANI Invoice Preview 2026+ (hidden)'
PREVIEW_VIEW_NAME = 'BARANI Account Move Preview -> VAT 2026+ HTML'
PREVIEW_VIEW_KEY = 'barani_runtime.account_move_preview_2026_button'

Param = env['ir.config_parameter'].sudo()
Report = env['ir.actions.report'].sudo().with_context(active_test=False)
View = env['ir.ui.view'].sudo().with_context(active_test=False, lang=None)

lines = []
lines.append('B10 CREATE — BARANI report-routing + Preview restore point SAFE')
lines.append('APPLY=%s CONFIRM_OK=%s PAGE=%s SNAPSHOT_CODE=%s' % (
    APPLY, CONFIRM == CONFIRM_TOKEN, PAGE, SNAPSHOT_CODE
))
lines.append('Policy: restore point only; writes ir.config_parameter only.')
lines.append('')

problems = 0
warnings = 0

existing_marker = Param.get_param(MARKER_KEY) or ''
existing_rows = Param.search_count([('key', '=like', PREFIX + '.%')])
lines.append('EXISTING SNAPSHOT CHECK')
lines.append('  marker=%r rows=%s' % (existing_marker, existing_rows))
if existing_marker:
    lines.append('FAIL: restore point already exists for this SNAPSHOT_CODE. Use the existing point or a new code; do not overwrite casually.')
    problems = problems + 1
lines.append('')

standard_specs = [
    ('sale_qso', 'sale.action_report_saleorder', 'sale.order', 'barani_commercial.report_saleorder'),
    ('sale_pf', 'sale.action_report_pro_forma_invoice', 'sale.order', 'barani_commercial.report_saleorder_proforma'),
    ('account_invoice', 'account.account_invoices', 'account.move', 'barani_vat.report_invoice_document_vat'),
    ('account_invoice_without_payment', 'account.account_invoices_without_payment', 'account.move', 'barani_vat.report_invoice_document_vat'),
]

standard_reports = Report.browse()
standard_old_view_keys = []
lines.append('STANDARD ODOO REPORT ACTIONS — PRE-MIGRATION')
for spec in standard_specs:
    token = spec[0]
    xmlid = spec[1]
    model_name = spec[2]
    desired_report_name = spec[3]
    rec = env.ref(xmlid, raise_if_not_found=False)
    if not rec or rec._name != 'ir.actions.report':
        lines.append('  %s: FAIL — XMLID not found as ir.actions.report' % xmlid)
        problems = problems + 1
    else:
        standard_reports = standard_reports | rec
        old_key = rec.report_name or ''
        standard_old_view_keys.append(old_key)
        binding_model = rec.binding_model_id.model if rec.binding_model_id else ''
        lines.append(
            '  token=%s xmlid=%s id=%s name=%r model=%s report_name=%s report_file=%s '
            'paper=%r binding_model=%s binding_type=%s binding_views=%s desired=%s'
            % (
                token, xmlid, rec.id, rec.name or '', rec.model or '',
                rec.report_name or '', rec.report_file or '',
                rec.paperformat_id.name if rec.paperformat_id else '',
                binding_model, rec.binding_type or '', rec.binding_view_types or '',
                desired_report_name,
            )
        )
        if rec.model != model_name:
            lines.append('    FAIL: model mismatch expected=%s' % model_name)
            problems = problems + 1
        if (rec.report_name or '') == desired_report_name:
            lines.append('    FAIL: standard action already points to BARANI but no B10 pre-route snapshot exists; original route cannot be safely inferred.')
            problems = problems + 1
        if not old_key:
            lines.append('    FAIL: original report_name is blank.')
            problems = problems + 1
lines.append('')

target_specs = [
    ('barani_qso', 'sale.order', 'barani_commercial.report_saleorder'),
    ('barani_pf', 'sale.order', 'barani_commercial.report_saleorder_proforma'),
    ('barani_vat', 'account.move', 'barani_vat.report_invoice_document_vat'),
    ('barani_delivery', 'sale.order', 'barani_delivery.report_sale_order_delivery_note_2026'),
]

custom_reports = Report.browse()
lines.append('APPROVED BARANI PDF REPORT ACTIONS')
for spec in target_specs:
    token = spec[0]
    model_name = spec[1]
    report_name = spec[2]
    rs = Report.search([
        ('model', '=', model_name),
        ('report_name', '=', report_name),
        ('report_type', '=', 'qweb-pdf'),
    ], order='id asc')
    lines.append('  token=%s model=%s report_name=%s count=%s' % (
        token, model_name, report_name, len(rs)
    ))
    if len(rs) != 1:
        lines.append('    FAIL: expected exactly one approved BARANI qweb-pdf report action.')
        problems = problems + 1
    for rr in rs:
        custom_reports = custom_reports | rr
        lines.append(
            '    id=%s name=%r paper=%r binding_model=%s binding_type=%s binding_views=%s'
            % (
                rr.id, rr.name or '',
                rr.paperformat_id.name if rr.paperformat_id else '',
                rr.binding_model_id.model if rr.binding_model_id else '',
                rr.binding_type or '', rr.binding_view_types or '',
            )
        )
        if not rr.paperformat_id:
            lines.append('    FAIL: BARANI target action has no paperformat.')
            problems = problems + 1
lines.append('')

reports = standard_reports | custom_reports

old_views = View.browse()
lines.append('STOCK QWEB WRAPPERS CURRENTLY LINKED TO STANDARD ACTIONS')
seen_old_keys = []
for key in standard_old_view_keys:
    if key and key not in seen_old_keys:
        seen_old_keys.append(key)
        rs = View.search([('type', '=', 'qweb'), ('key', '=', key)], order='id asc')
        lines.append('  key=%s count=%s' % (key, len(rs)))
        if len(rs) != 1:
            lines.append('    FAIL: expected exactly one QWeb view with this key before migration.')
            problems = problems + 1
        for vw in rs:
            old_views = old_views | vw
            lines.append('    id=%s name=%r active=%s inherit_id=%s len=%s write_date=%s' % (
                vw.id, vw.name or '', vw.active,
                vw.inherit_id.id if vw.inherit_id else 0,
                len(vw.arch_db or ''), vw.write_date
            ))
            if (vw.key or '').startswith('barani_'):
                lines.append('    FAIL: original stock action already points to a BARANI key; B10 must capture the true pre-route state.')
                problems = problems + 1
lines.append('')

lines.append('PLANNED PREVIEW RECORD COLLISION CHECK')
existing_preview_reports = Report.search([
    ('model', '=', 'account.move'),
    ('report_type', '=', 'qweb-html'),
    '|',
    ('name', '=', PREVIEW_REPORT_NAME),
    ('report_name', '=', 'barani_vat.report_invoice_document_vat'),
], order='id asc')
existing_preview_views = View.search([
    ('model', '=', 'account.move'),
    '|',
    ('key', '=', PREVIEW_VIEW_KEY),
    ('name', '=', PREVIEW_VIEW_NAME),
], order='id asc')
lines.append('  matching qweb-html report actions=%s' % len(existing_preview_reports))
lines.append('  matching inherited Preview views=%s' % len(existing_preview_views))
if existing_preview_reports or existing_preview_views:
    lines.append('FAIL: planned BARANI Preview records already exist. Reconcile them before creating a new restore point.')
    problems = problems + 1
lines.append('')

lines.append('RESTORE-POINT PLAN')
lines.append('  report action snapshots=%s' % len(reports))
lines.append('  original stock QWeb wrapper snapshots=%s' % len(old_views))
lines.append('  writes: ir.config_parameter only')
lines.append('  ir.actions.report writes=0')
lines.append('  ir.ui.view writes=0')
lines.append('  mail.template writes=0')
lines.append('  account.move writes=0')
lines.append('  sale.order writes=0')
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
    lines.append('Set APPLY=True and CONFIRM=%s to create B10.' % CONFIRM_TOKEN)
    full2 = NL.join(lines)
    start2 = (PAGE - 1) * PAGE_SIZE
    end2 = start2 + PAGE_SIZE
    more2 = 'YES' if end2 < len(full2) else 'NO'
    raise UserError(('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s%s%s' % (
        PAGE, start2, min(end2, len(full2)), len(full2), more2, NL, full2[start2:end2]
    ))[:90000])

try:
    env.cr.execute('SAVEPOINT sp_barani_b10_restore')

    report_index = ''
    for rr in reports:
        if report_index:
            report_index = report_index + SEP
        report_index = report_index + str(rr.id)
        base = PREFIX + '.report.' + str(rr.id)
        Param.set_param(base + '.name', rr.name or '')
        Param.set_param(base + '.model', rr.model or '')
        Param.set_param(base + '.report_name', rr.report_name or '')
        Param.set_param(base + '.report_file', rr.report_file or '')
        Param.set_param(base + '.report_type', rr.report_type or '')
        Param.set_param(base + '.paperformat_id', str(rr.paperformat_id.id if rr.paperformat_id else 0))
        Param.set_param(base + '.binding_model_id', str(rr.binding_model_id.id if rr.binding_model_id else 0))
        Param.set_param(base + '.binding_type', rr.binding_type or '')
        Param.set_param(base + '.binding_view_types', rr.binding_view_types or '')
        Param.set_param(base + '.print_report_name', rr.print_report_name or '')
        Param.set_param(base + '.attachment_use', '1' if rr.attachment_use else '0')
        Param.set_param(base + '.attachment', rr.attachment or '')
        Param.set_param(base + '.multi', '1' if rr.multi else '0')

    Param.set_param(PREFIX + '.report_index', report_index)

    view_index = ''
    for vw in old_views:
        if view_index:
            view_index = view_index + SEP
        view_index = view_index + str(vw.id)
        basev = PREFIX + '.view.' + str(vw.id)
        Param.set_param(basev + '.key', vw.key or '')
        Param.set_param(basev + '.name', vw.name or '')
        Param.set_param(basev + '.active', '1' if vw.active else '0')
        Param.set_param(basev + '.arch_db', vw.arch_db or '')

    Param.set_param(PREFIX + '.view_index', view_index)

    for spec in standard_specs:
        token = spec[0]
        xmlid = spec[1]
        rec = env.ref(xmlid)
        Param.set_param(PREFIX + '.standard.' + token + '.xmlid', xmlid)
        Param.set_param(PREFIX + '.standard.' + token + '.id', str(rec.id))
        Param.set_param(PREFIX + '.standard.' + token + '.original_report_name', rec.report_name or '')
        Param.set_param(PREFIX + '.standard.' + token + '.original_report_file', rec.report_file or '')
        Param.set_param(PREFIX + '.standard.' + token + '.original_paperformat_id', str(rec.paperformat_id.id if rec.paperformat_id else 0))

    Param.set_param(PREFIX + '.preview_report_name', PREVIEW_REPORT_NAME)
    Param.set_param(PREFIX + '.preview_view_name', PREVIEW_VIEW_NAME)
    Param.set_param(PREFIX + '.preview_view_key', PREVIEW_VIEW_KEY)
    Param.set_param(MARKER_KEY, '1')
    Param.set_param(CURRENT_KEY, SNAPSHOT_CODE)

    if (Param.get_param(MARKER_KEY) or '') != '1':
        raise Exception('B10 marker read-back failed')
    if (Param.get_param(PREFIX + '.report_index') or '') != report_index:
        raise Exception('B10 report index read-back failed')
    if (Param.get_param(PREFIX + '.view_index') or '') != view_index:
        raise Exception('B10 view index read-back failed')

    env.cr.execute('RELEASE SAVEPOINT sp_barani_b10_restore')
    lines.append('')
    lines.append('READ-BACK PASS: B10 marker stored')
    lines.append('READ-BACK PASS: report index stored')
    lines.append('READ-BACK PASS: original-view index stored')
    lines.append('B10 COMPLETE: pre-migration report-routing + Preview restore point created.')
    lines.append('NEXT: run C10 dry-run only; do not change Print bindings yet.')
except Exception as exc:
    try:
        env.cr.execute('ROLLBACK TO SAVEPOINT sp_barani_b10_restore')
        env.cr.execute('RELEASE SAVEPOINT sp_barani_b10_restore')
        try:
            env.invalidate_all()
        except Exception as inv1:
            try:
                env.cache.invalidate()
            except Exception as inv2:
                pass
    except Exception as rb:
        lines.append('ROLLBACK PROBLEM: %s' % str(rb)[:500])
    raise UserError((NL.join(lines) + NL + 'B10 APPLY FAILED AND ROLLED BACK: %s' % str(exc))[:90000])

text = NL.join(lines)[:90000]
Param.set_param(OUT_KEY, text)
out_rec = Param.search([('key', '=', OUT_KEY)], limit=1)
action = {
    'type': 'ir.actions.act_window',
    'name': 'B10 report-routing restore point result',
    'res_model': 'ir.config_parameter',
    'view_mode': 'form',
    'res_id': out_rec.id,
    'target': 'current',
}
