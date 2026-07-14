# ============================================================================
# ACTION NAME : R10 RESTORE — BARANI report routing + Preview from B10 SAFE
# MODEL       : Module (ir.module.module) recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
#
# PURPOSE     : Restore the exact B10 state:
#               - all snapshotted report-action fields;
#               - original QWeb wrapper names and bytes;
#               - remove C20-created Preview inherited view and HTML action.
#
# SCOPE       : technical report/view/config records only.
# NO TOUCH    : account.move, sale.order, payments, taxes, journals, POHODA.
# ============================================================================

APPLY = False
CONFIRM = ''
CONFIRM_TOKEN = 'RESTORE_BARANI_REPORT_ROUTING_PREVIEW_FROM_B10_R10'
PAGE = 1
PAGE_SIZE = 60000

SNAPSHOT_CODE = 'pre_standard_relink_preview_2026_07_14'
PREFIX = 'barani.report_routing_preview.restore.' + SNAPSHOT_CODE
B10_MARKER = PREFIX + '.marker'
C10_MARKER = 'barani.report_routing_preview.c10.standard_relink.marker'
C20_MARKER = 'barani.report_routing_preview.c20.preview_html.marker'
C30_MARKER = 'barani.report_routing_preview.c30.hide_duplicates.marker'
C31_MARKER = 'barani.report_routing_preview.c31.archive_old_views.marker'
C32_MARKER = 'barani.report_routing_preview.c32.preview_action_rename.marker'
R10_MARKER = 'barani.report_routing_preview.r10.restored.marker'
OUT_KEY = 'barani.report_routing_preview.r10.restore.output'
SEP = chr(31)
NL = chr(10)

Param = env['ir.config_parameter'].sudo()
Report = env['ir.actions.report'].sudo().with_context(active_test=False)
View = env['ir.ui.view'].sudo().with_context(active_test=False, lang=None)

lines = []
lines.append('R10 RESTORE — BARANI report routing + Preview from B10 SAFE')
lines.append('APPLY=%s CONFIRM_OK=%s PAGE=%s' % (
    APPLY, CONFIRM == CONFIRM_TOKEN, PAGE
))
lines.append('Policy: restore technical routing/view state only; no business-record changes.')
lines.append('')

problems = 0
warnings = 0

if (Param.get_param(B10_MARKER) or '') != '1':
    lines.append('FAIL: B10 restore marker missing.')
    problems = problems + 1

report_index_raw = Param.get_param(PREFIX + '.report_index') or ''
view_index_raw = Param.get_param(PREFIX + '.view_index') or ''
report_ids = []
view_ids = []
if report_index_raw:
    for value in report_index_raw.split(SEP):
        if value:
            report_ids.append(int(value))
if view_index_raw:
    for value in view_index_raw.split(SEP):
        if value:
            view_ids.append(int(value))

if not report_ids:
    lines.append('FAIL: B10 report index is empty.')
    problems = problems + 1
if not view_ids:
    lines.append('FAIL: B10 view index is empty.')
    problems = problems + 1

report_plan = []
lines.append('REPORT RESTORE PLAN')
for rid in report_ids:
    rr = Report.browse(rid)
    if not rr.exists():
        lines.append('  FAIL: report id=%s no longer exists.' % rid)
        problems = problems + 1
    else:
        base = PREFIX + '.report.' + str(rid)
        pf_id = int(Param.get_param(base + '.paperformat_id') or '0')
        bm_id = int(Param.get_param(base + '.binding_model_id') or '0')
        vals = {
            'name': Param.get_param(base + '.name') or '',
            'report_name': Param.get_param(base + '.report_name') or '',
            'report_file': Param.get_param(base + '.report_file') or '',
            'report_type': Param.get_param(base + '.report_type') or 'qweb-pdf',
            'paperformat_id': pf_id or False,
            'binding_model_id': bm_id or False,
            'binding_type': Param.get_param(base + '.binding_type') or False,
            'binding_view_types': Param.get_param(base + '.binding_view_types') or '',
            'print_report_name': Param.get_param(base + '.print_report_name') or False,
            'attachment_use': (Param.get_param(base + '.attachment_use') or '0') == '1',
            'attachment': Param.get_param(base + '.attachment') or False,
            'multi': (Param.get_param(base + '.multi') or '0') == '1',
        }
        report_plan.append((rr, vals))
        lines.append('  id=%s current_name=%r current_report=%s -> original_name=%r original_report=%s binding_model_id=%s' % (
            rr.id, rr.name or '', rr.report_name or '',
            vals['name'], vals['report_name'], vals['binding_model_id']
        ))
lines.append('')

view_plan = []
lines.append('QWEB VIEW RESTORE PLAN')
for vid in view_ids:
    vw = View.browse(vid)
    if not vw.exists():
        lines.append('  FAIL: view id=%s no longer exists.' % vid)
        problems = problems + 1
    else:
        basev = PREFIX + '.view.' + str(vid)
        vals = {
            'name': Param.get_param(basev + '.name') or '',
            'active': (Param.get_param(basev + '.active') or '0') == '1',
            'arch_db': Param.get_param(basev + '.arch_db') or '',
        }
        original_key = Param.get_param(basev + '.key') or ''
        if (vw.key or '') != original_key:
            lines.append('  FAIL: view id=%s key drift current=%s original=%s; R10 does not rewrite keys.' % (
                vid, vw.key or '', original_key
            ))
            problems = problems + 1
        view_plan.append((vw, vals, original_key))
        lines.append('  id=%s key=%s current_name=%r -> original_name=%r arch_len=%s' % (
            vw.id, original_key, vw.name or '', vals['name'], len(vals['arch_db'])
        ))
lines.append('')

preview_report_id = int(Param.get_param(C20_MARKER + '.report_action_id') or '0')
preview_view_id = int(Param.get_param(C20_MARKER + '.view_id') or '0')
preview_report = Report.browse(preview_report_id) if preview_report_id else Report.browse()
preview_view = View.browse(preview_view_id) if preview_view_id else View.browse()

lines.append('C20-CREATED PREVIEW RECORD REMOVAL PLAN')
lines.append('  preview view id=%s exists=%s' % (
    preview_view_id, bool(preview_view.exists())
))
lines.append('  preview qweb-html action id=%s exists=%s' % (
    preview_report_id, bool(preview_report.exists())
))
lines.append('')

lines.append('SUMMARY PLAN')
lines.append('  report action restores=%s' % len(report_plan))
lines.append('  QWeb view restores=%s' % len(view_plan))
lines.append('  Preview inherited views to unlink=%s' % (1 if preview_view.exists() else 0))
lines.append('  Preview qweb-html actions to unlink=%s' % (1 if preview_report.exists() else 0))
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
    lines.append('Set APPLY=True and CONFIRM=%s to restore.' % CONFIRM_TOKEN)
    full2 = NL.join(lines)
    start2 = (PAGE - 1) * PAGE_SIZE
    end2 = start2 + PAGE_SIZE
    more2 = 'YES' if end2 < len(full2) else 'NO'
    raise UserError(('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s%s%s' % (
        PAGE, start2, min(end2, len(full2)), len(full2), more2, NL, full2[start2:end2]
    ))[:90000])

try:
    env.cr.execute('SAVEPOINT sp_barani_r10_restore')

    if preview_view.exists():
        preview_view.unlink()
    if preview_report.exists():
        preview_report.unlink()

    for item in report_plan:
        item[0].write(item[1])
    for item in view_plan:
        item[0].write(item[1])

    env.flush_all()
    try:
        View.clear_caches()
    except Exception as cache1:
        View.invalidate_model()
    Report.invalidate_model()

    failures = 0
    for item in report_plan:
        rr = Report.browse(item[0].id)
        vals = item[1]
        if rr.report_name != vals['report_name'] or rr.name != vals['name']:
            lines.append('READ-BACK FAIL: report id=%s' % rr.id)
            failures = failures + 1
    for item in view_plan:
        vw = View.browse(item[0].id)
        vals = item[1]
        if vw.name != vals['name'] or (vw.arch_db or '') != vals['arch_db'] or (vw.key or '') != item[2]:
            lines.append('READ-BACK FAIL: view id=%s' % vw.id)
            failures = failures + 1
    if preview_view_id and View.browse(preview_view_id).exists():
        lines.append('READ-BACK FAIL: Preview inherited view still exists.')
        failures = failures + 1
    if preview_report_id and Report.browse(preview_report_id).exists():
        lines.append('READ-BACK FAIL: Preview qweb-html action still exists.')
        failures = failures + 1
    if failures:
        raise Exception('R10 read-back failure count=%s' % failures)

    Param.set_param(C10_MARKER, '0')
    Param.set_param(C20_MARKER, '0')
    Param.set_param(C30_MARKER, '0')
    Param.set_param(C31_MARKER, '0')
    Param.set_param(C32_MARKER, '0')
    Param.set_param(C32_MARKER + '.action_id', '')
    Param.set_param(C32_MARKER + '.display_name', '')
    Param.set_param(R10_MARKER, '1')

    env.cr.execute('RELEASE SAVEPOINT sp_barani_r10_restore')
    lines.append('')
    lines.append('READ-BACK PASS: report-action routing/bindings/names restored from B10')
    lines.append('READ-BACK PASS: original QWeb wrapper names/bytes restored')
    lines.append('READ-BACK PASS: C20 Preview records removed')
    lines.append('R10 COMPLETE: pre-migration routing + Preview state restored.')
except Exception as exc:
    try:
        env.cr.execute('ROLLBACK TO SAVEPOINT sp_barani_r10_restore')
        env.cr.execute('RELEASE SAVEPOINT sp_barani_r10_restore')
        try:
            env.invalidate_all()
        except Exception as inv1:
            try:
                env.cache.invalidate()
            except Exception as inv2:
                pass
    except Exception as rb:
        lines.append('ROLLBACK PROBLEM: %s' % str(rb)[:500])
    raise UserError((NL.join(lines) + NL + 'R10 APPLY FAILED AND ROLLED BACK: %s' % str(exc))[:90000])

text = NL.join(lines)[:90000]
Param.set_param(OUT_KEY, text)
out_rec = Param.search([('key', '=', OUT_KEY)], limit=1)
action = {
    'type': 'ir.actions.act_window',
    'name': 'R10 restore report routing + Preview result',
    'res_model': 'ir.config_parameter',
    'view_mode': 'form',
    'res_id': out_rec.id,
    'target': 'current',
}
