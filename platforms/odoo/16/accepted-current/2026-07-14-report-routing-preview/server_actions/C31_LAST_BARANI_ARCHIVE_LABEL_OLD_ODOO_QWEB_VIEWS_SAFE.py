# ============================================================================
# ACTION NAME : C31 LAST — archive-label former Odoo QWeb wrapper views SAFE
# MODEL       : Module (ir.module.module) recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
#
# PURPOSE     : Rename only ir.ui.view.name on the former QWeb wrapper views
#               that B10 recorded as being linked to the standard Odoo report
#               actions before C10.
#
# DO NOT CHANGE:
#   ir.ui.view.key, XML ID, t-name, arch_db, active, inherit_id;
#   standard report actions;
#   BARANI QWeb views;
#   business records.
# ============================================================================

APPLY = False
CONFIRM = ''
CONFIRM_TOKEN = 'ARCHIVE_LABEL_OLD_ODOO_QWEB_VIEWS_C31'
PAGE = 1
PAGE_SIZE = 60000

SNAPSHOT_CODE = 'pre_standard_relink_preview_2026_07_14'
PREFIX = 'barani.report_routing_preview.restore.' + SNAPSHOT_CODE
B10_MARKER = PREFIX + '.marker'
C30_MARKER = 'barani.report_routing_preview.c30.hide_duplicates.marker'
C31_MARKER = 'barani.report_routing_preview.c31.archive_old_views.marker'
OUT_KEY = 'barani.report_routing_preview.c31.archive_old_views.output'
NL = chr(10)

Param = env['ir.config_parameter'].sudo()
View = env['ir.ui.view'].sudo().with_context(active_test=False, lang=None)

lines = []
lines.append('C31 LAST — archive-label former Odoo QWeb wrapper views SAFE')
lines.append('APPLY=%s CONFIRM_OK=%s PAGE=%s' % (
    APPLY, CONFIRM == CONFIRM_TOKEN, PAGE
))
lines.append('Policy: change ir.ui.view.name only; technical identifiers and template bytes remain unchanged.')
lines.append('')

problems = 0
warnings = 0

if (Param.get_param(B10_MARKER) or '') != '1':
    lines.append('FAIL: B10 restore point marker missing.')
    problems = problems + 1
if (Param.get_param(C30_MARKER) or '') != '1':
    lines.append('FAIL: C30 marker missing. Archive-labeling must be last.')
    problems = problems + 1
if Param.get_param(C31_MARKER) == '1':
    lines.append('FAIL: C31 marker already exists. Do not rerun.')
    problems = problems + 1

mapping = [
    ('sale_qso', 'Archived — Odoo Quotation / Order'),
    ('sale_pf', 'Archived — Odoo Pro-Forma Invoice'),
    ('account_invoice', 'Archived — Odoo Invoice with Payments'),
    ('account_invoice_without_payment', 'Archived — Odoo Invoice without Payments'),
]

plan = []
seen_keys = []
lines.append('FORMER STANDARD-ACTION QWEB WRAPPERS FROM B10')
for item in mapping:
    token = item[0]
    desired_name = item[1]
    key = Param.get_param(PREFIX + '.standard.' + token + '.original_report_name') or ''
    lines.append('  token=%s key=%s desired_name=%r' % (token, key, desired_name))
    if not key:
        lines.append('    FAIL: B10 original report_name missing.')
        problems = problems + 1
    elif key.startswith('barani_'):
        lines.append('    FAIL: B10 original key is BARANI; refusing to archive an active BARANI template.')
        problems = problems + 1
    elif key in seen_keys:
        lines.append('    FAIL: duplicate original key across standard actions. Audit must choose one non-conflicting archive label.')
        problems = problems + 1
    else:
        seen_keys.append(key)
        rs = View.search([('type', '=', 'qweb'), ('key', '=', key)], order='id asc')
        lines.append('    count=%s' % len(rs))
        if len(rs) != 1:
            lines.append('    FAIL: expected exactly one QWeb view with key=%s' % key)
            problems = problems + 1
        else:
            vw = rs[0]
            original_name = Param.get_param(PREFIX + '.view.' + str(vw.id) + '.name')
            arch_param = Param.search([('key', '=', PREFIX + '.view.' + str(vw.id) + '.arch_db')], limit=1)
            if not arch_param:
                lines.append('    FAIL: B10 arch snapshot parameter missing.')
                problems = problems + 1
            else:
                original_arch = arch_param.value or ''
                lines.append('    id=%s current_name=%r B10_name=%r active=%s len=%s' % (
                    vw.id, vw.name or '', original_name or '', vw.active, len(vw.arch_db or '')
                ))
                if (vw.arch_db or '') != original_arch:
                    lines.append('    FAIL: template bytes drifted since B10; archive-labeling must not conceal unrelated changes.')
                    problems = problems + 1
                else:
                    plan.append((vw, {'name': desired_name}, original_arch, key))
lines.append('')

lines.append('WRITE PLAN — NAME FIELD ONLY')
for item in plan:
    lines.append('  view_id=%s key=%s old_name=%r new_name=%r arch_len=%s' % (
        item[0].id, item[3], item[0].name or '', item[1]['name'], len(item[2])
    ))
lines.append('  planned ir.ui.view name writes=%s' % len(plan))
lines.append('  arch_db writes=0')
lines.append('  key writes=0')
lines.append('  active writes=0')
lines.append('  report action writes=0')
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
    lines.append('This is the last migration step; apply only after C30 and final menu verification.')
    lines.append('Set APPLY=True and CONFIRM=%s to apply.' % CONFIRM_TOKEN)
    full2 = NL.join(lines)
    start2 = (PAGE - 1) * PAGE_SIZE
    end2 = start2 + PAGE_SIZE
    more2 = 'YES' if end2 < len(full2) else 'NO'
    raise UserError(('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s%s%s' % (
        PAGE, start2, min(end2, len(full2)), len(full2), more2, NL, full2[start2:end2]
    ))[:90000])

try:
    env.cr.execute('SAVEPOINT sp_barani_c31_archive')
    for item in plan:
        item[0].write(item[1])

    env.flush_all()
    View.invalidate_model()

    failures = 0
    for item in plan:
        vw = View.browse(item[0].id)
        if vw.name != item[1]['name']:
            lines.append('READ-BACK FAIL: view id=%s name=%r expected=%r' % (
                vw.id, vw.name or '', item[1]['name']
            ))
            failures = failures + 1
        if (vw.key or '') != item[3]:
            lines.append('READ-BACK FAIL: view id=%s key changed.' % vw.id)
            failures = failures + 1
        if (vw.arch_db or '') != item[2]:
            lines.append('READ-BACK FAIL: view id=%s arch_db changed.' % vw.id)
            failures = failures + 1
    if failures:
        raise Exception('C31 read-back failure count=%s' % failures)

    Param.set_param(C31_MARKER, '1')
    if (Param.get_param(C31_MARKER) or '') != '1':
        raise Exception('C31 marker read-back failed')

    env.cr.execute('RELEASE SAVEPOINT sp_barani_c31_archive')
    lines.append('')
    lines.append('READ-BACK PASS: former stock wrapper view names now carry Archived — prefix')
    lines.append('READ-BACK PASS: keys and QWeb bytes are unchanged')
    lines.append('C31 COMPLETE: old Odoo-linked template records archive-labeled last.')
except Exception as exc:
    try:
        env.cr.execute('ROLLBACK TO SAVEPOINT sp_barani_c31_archive')
        env.cr.execute('RELEASE SAVEPOINT sp_barani_c31_archive')
        try:
            env.invalidate_all()
        except Exception as inv1:
            try:
                env.cache.invalidate()
            except Exception as inv2:
                pass
    except Exception as rb:
        lines.append('ROLLBACK PROBLEM: %s' % str(rb)[:500])
    raise UserError((NL.join(lines) + NL + 'C31 APPLY FAILED AND ROLLED BACK: %s' % str(exc))[:90000])

text = NL.join(lines)[:90000]
Param.set_param(OUT_KEY, text)
out_rec = Param.search([('key', '=', OUT_KEY)], limit=1)
action = {
    'type': 'ir.actions.act_window',
    'name': 'C31 archive-label old QWeb views result',
    'res_model': 'ir.config_parameter',
    'view_mode': 'form',
    'res_id': out_rec.id,
    'target': 'current',
}
