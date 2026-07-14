# ============================================================================
# ACTION NAME : C32 LAST — rename BARANI Preview action display name SAFE
# MODEL       : Module (ir.module.module) recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
#
# PURPOSE     : Change only the human-readable ir.actions.report.name of the
#               hidden BARANI qweb-html Preview action so the breadcrumb shows:
#
#                   Invoice Preview
#
# DO NOT CHANGE:
#   action ID, model, report_type, report_name, report_file, paperformat,
#   binding, QWeb view, inherited Preview view, business records.
# ============================================================================

APPLY = False
CONFIRM = ''
CONFIRM_TOKEN = 'RENAME_BARANI_PREVIEW_ACTION_DISPLAY_NAME_C32'
PAGE = 1
PAGE_SIZE = 60000

C20_MARKER = 'barani.report_routing_preview.c20.preview_html.marker'
C31_MARKER = 'barani.report_routing_preview.c31.archive_old_views.marker'
C32_MARKER = 'barani.report_routing_preview.c32.preview_action_rename.marker'
OUT_KEY = 'barani.report_routing_preview.c32.preview_action_rename.output'

EXPECTED_REPORT_NAME = 'barani_vat.report_invoice_document_vat'
TARGET_DISPLAY_NAME = 'Invoice Preview'
NL = chr(10)

Param = env['ir.config_parameter'].sudo()
Report = env['ir.actions.report'].sudo().with_context(active_test=False)

lines = []
lines.append('C32 LAST — rename BARANI Preview action display name SAFE')
lines.append('APPLY=%s CONFIRM_OK=%s PAGE=%s' % (
    APPLY, CONFIRM == CONFIRM_TOKEN, PAGE
))
lines.append('Policy: change ir.actions.report.name only.')
lines.append('')

problems = 0
warnings = 0

if (Param.get_param(C20_MARKER) or '') != '1':
    lines.append('FAIL: C20 Preview marker missing.')
    problems = problems + 1

if (Param.get_param(C31_MARKER) or '') != '1':
    lines.append('FAIL: C31 archive-label marker missing. C32 must run last.')
    problems = problems + 1

if (Param.get_param(C32_MARKER) or '') == '1':
    lines.append('FAIL: C32 marker already exists. Do not rerun.')
    problems = problems + 1

preview_action_id = int(Param.get_param(C20_MARKER + '.report_action_id') or '0')
preview_action = Report.browse(preview_action_id) if preview_action_id else Report.browse()

lines.append('TARGET ACTION')
lines.append('  marker action id=%s' % preview_action_id)

if not preview_action.exists():
    lines.append('  FAIL: Preview report action does not exist.')
    problems = problems + 1
else:
    lines.append(
        '  id=%s current_name=%r model=%s report_type=%s report_name=%s '
        'report_file=%s paperformat=%r binding_model=%s'
        % (
            preview_action.id,
            preview_action.name or '',
            preview_action.model or '',
            preview_action.report_type or '',
            preview_action.report_name or '',
            preview_action.report_file or '',
            preview_action.paperformat_id.name if preview_action.paperformat_id else '',
            preview_action.binding_model_id.model if preview_action.binding_model_id else '',
        )
    )

    if preview_action.model != 'account.move':
        lines.append('  FAIL: unexpected model.')
        problems = problems + 1
    if preview_action.report_type != 'qweb-html':
        lines.append('  FAIL: action is not qweb-html.')
        problems = problems + 1
    if preview_action.report_name != EXPECTED_REPORT_NAME:
        lines.append('  FAIL: action does not use the approved BARANI VAT body.')
        problems = problems + 1
    if preview_action.binding_model_id:
        lines.append('  FAIL: Preview action unexpectedly has a Print-menu binding.')
        problems = problems + 1

lines.append('')
lines.append('WRITE PLAN')
if preview_action.exists():
    lines.append(
        '  action id=%s name: %r -> %r'
        % (preview_action.id, preview_action.name or '', TARGET_DISPLAY_NAME)
    )
lines.append('  ir.actions.report name writes=%s' % (1 if preview_action.exists() else 0))
lines.append('  report_name writes=0')
lines.append('  report_file writes=0')
lines.append('  binding writes=0')
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
    lines.append(
        'Set APPLY=True and CONFIRM=%s to apply.'
        % CONFIRM_TOKEN
    )
    full2 = NL.join(lines)
    start2 = (PAGE - 1) * PAGE_SIZE
    end2 = start2 + PAGE_SIZE
    more2 = 'YES' if end2 < len(full2) else 'NO'
    raise UserError(('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s%s%s' % (
        PAGE, start2, min(end2, len(full2)), len(full2), more2, NL, full2[start2:end2]
    ))[:90000])

try:
    env.cr.execute('SAVEPOINT sp_barani_c32_preview_name')

    original_report_name = preview_action.report_name or ''
    original_report_file = preview_action.report_file or ''
    original_binding_model_id = preview_action.binding_model_id.id if preview_action.binding_model_id else 0
    original_report_type = preview_action.report_type or ''

    preview_action.write({'name': TARGET_DISPLAY_NAME})

    env.flush_all()
    Report.invalidate_model()

    rb = Report.browse(preview_action.id)

    if rb.name != TARGET_DISPLAY_NAME:
        raise Exception('Preview action name read-back failed')
    if (rb.report_name or '') != original_report_name:
        raise Exception('report_name changed unexpectedly')
    if (rb.report_file or '') != original_report_file:
        raise Exception('report_file changed unexpectedly')
    if (rb.binding_model_id.id if rb.binding_model_id else 0) != original_binding_model_id:
        raise Exception('binding changed unexpectedly')
    if (rb.report_type or '') != original_report_type:
        raise Exception('report_type changed unexpectedly')

    Param.set_param(C32_MARKER, '1')
    Param.set_param(C32_MARKER + '.action_id', str(rb.id))
    Param.set_param(C32_MARKER + '.display_name', TARGET_DISPLAY_NAME)

    if (Param.get_param(C32_MARKER) or '') != '1':
        raise Exception('C32 marker read-back failed')

    env.cr.execute('RELEASE SAVEPOINT sp_barani_c32_preview_name')

    lines.append('')
    lines.append('READ-BACK PASS: Preview action display name=%r' % rb.name)
    lines.append('READ-BACK PASS: renderer, type and binding unchanged')
    lines.append('C32 COMPLETE: Preview breadcrumb label cleaned up.')
except Exception as exc:
    try:
        env.cr.execute('ROLLBACK TO SAVEPOINT sp_barani_c32_preview_name')
        env.cr.execute('RELEASE SAVEPOINT sp_barani_c32_preview_name')
        try:
            env.invalidate_all()
        except Exception as inv1:
            try:
                env.cache.invalidate()
            except Exception as inv2:
                pass
    except Exception as rb_exc:
        lines.append('ROLLBACK PROBLEM: %s' % str(rb_exc)[:500])

    raise UserError(
        (NL.join(lines) + NL + 'C32 APPLY FAILED AND ROLLED BACK: %s' % str(exc))[:90000]
    )

text = NL.join(lines)[:90000]
Param.set_param(OUT_KEY, text)
out_rec = Param.search([('key', '=', OUT_KEY)], limit=1)

action = {
    'type': 'ir.actions.act_window',
    'name': 'C32 Preview action display-name result',
    'res_model': 'ir.config_parameter',
    'view_mode': 'form',
    'res_id': out_rec.id,
    'target': 'current',
}
