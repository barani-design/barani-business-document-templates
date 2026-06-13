# ============================================================================
# ACTION NAME : BARANI Delivery Note 2026 — RESTORE FROM CURRENT RESTORE POINT SAFE
# MODEL       : Any model; selected records ignored.
# ACTION TO DO: Execute Python Code
# RUN BY      : Run APPLY=False first; then APPLY=True + CONFIRM='RESTORE_DELIVERY_POINT'.
# PURPOSE     : Restore the isolated BARANI Delivery Note 2026 body/layout/report
#               from the current ir.config_parameter restore point.
#
# WRITES      : ir.ui.view.arch_db for the delivery body/layout, the delivery
#               report action, and the owned paperformat if present. No picking,
#               stock move, product, accounting, tax, or invoice records are changed.
# SAFE_EVAL   : no import/def/lambda/comprehension/with/getattr/hasattr/setattr/
#               eval/exec/open/dir/isinstance in executable code.
# ============================================================================

APPLY = False
CONFIRM = ''
CURRENT_KEY = 'barani.delivery_note_2026.restore_point.current'
BODY_KEY = 'barani_delivery.report_delivery_note_2026'
LAYOUT_KEY = 'barani_delivery.external_layout_delivery_2026'
ACTION_NAME = 'BARANI Delivery Note 2026 — RESTORE FROM CURRENT RESTORE POINT SAFE'

View = env['ir.ui.view'].sudo()
Report = env['ir.actions.report'].sudo()
Paper = env['report.paperformat'].sudo()
Param = env['ir.config_parameter'].sudo()

lines = []
lines.append(ACTION_NAME)
lines.append('APPLY=%s CONFIRM=%s' % (APPLY, CONFIRM))

# TEST 0 - savepoint and cache invalidation.
manual_sp_ok = False
cache_inv_method = ''
lines.append('TEST 0 - manual SQL savepoint recovery + ORM cache invalidation')
try:
    env.cr.execute('SAVEPOINT t0_delivery_restore_ok')
    env.cr.execute('SELECT 1')
    env.cr.execute('RELEASE SAVEPOINT t0_delivery_restore_ok')
    env.cr.execute('SAVEPOINT t0_delivery_restore_fail')
    try:
        env.cr.execute('SELECT * FROM __barani_missing_table_for_rollback_probe__')
        env.cr.execute('RELEASE SAVEPOINT t0_delivery_restore_fail')
    except Exception:
        env.cr.execute('ROLLBACK TO SAVEPOINT t0_delivery_restore_fail')
        env.cr.execute('RELEASE SAVEPOINT t0_delivery_restore_fail')
        try:
            env.invalidate_all()
            cache_inv_method = 'env.invalidate_all'
        except Exception:
            try:
                env.cache.invalidate()
                cache_inv_method = 'env.cache.invalidate'
            except Exception:
                cache_inv_method = ''
        if cache_inv_method:
            env.cr.execute('SELECT 1')
            manual_sp_ok = True
            lines.append('PASS: SAVEPOINT recovery works; cache method=%s' % cache_inv_method)
except Exception as e0:
    lines.append('FATAL TEST 0: %s' % str(e0)[:500])
if not manual_sp_ok:
    lines.append('STOP: savepoint/cache mechanism unusable.')
    raise UserError('\n'.join(lines)[:90000])
lines.append('')

tag = Param.get_param(CURRENT_KEY, '') or ''
lines.append('current tag=%r' % tag)
if not tag:
    raise UserError('\n'.join(lines) + "\nERROR: no current restore point tag.")
prefix = 'barani.delivery_note_2026.restore_point.' + tag
body_arch = Param.get_param(prefix + '.body_arch', '') or ''
layout_arch = Param.get_param(prefix + '.layout_arch', '') or ''
ids = Param.get_param(prefix + '.ids', '') or ''
report_name = Param.get_param(prefix + '.report.name', '') or 'Delivery Note — 2026+'
print_name = Param.get_param(prefix + '.report.print_report_name', '') or "'DN ' + (object.name or '')"
if not body_arch or not layout_arch:
    raise UserError('\n'.join(lines) + "\nERROR: restore point missing arch payloads.")
parts = ids.split(',')
body_id = 0
report_id = 0
paper_id = 0
layout_id = 0
try:
    if len(parts) > 0:
        body_id = int(parts[0] or '0')
    if len(parts) > 1:
        report_id = int(parts[1] or '0')
    if len(parts) > 2:
        paper_id = int(parts[2] or '0')
    if len(parts) > 3:
        layout_id = int(parts[3] or '0')
except Exception:
    pass
body = View.browse(body_id) if body_id else View.search([('key', '=', BODY_KEY)], limit=1)
layout = View.browse(layout_id) if layout_id else View.search([('key', '=', LAYOUT_KEY)], limit=1)
report = Report.browse(report_id) if report_id else Report.search([('report_name', '=', BODY_KEY), ('model', '=', 'stock.picking')], limit=1)
paper = Paper.browse(paper_id) if paper_id else (report.paperformat_id if report else Paper.browse())
if not (body.exists() and layout.exists() and report.exists()):
    raise UserError('\n'.join(lines) + "\nERROR: target body/layout/report not found.")
lines.append('PLAN')
lines.append('  restore body view id=%s key=%s len=%s' % (body.id, body.key, len(body_arch)))
lines.append('  restore layout view id=%s key=%s len=%s' % (layout.id, layout.key, len(layout_arch)))
lines.append('  restore report id=%s name=%r' % (report.id, report_name))
if paper.exists():
    lines.append('  restore paper id=%s name=%r margins from restore point' % (paper.id, paper.name))
lines.append('')
if not APPLY:
    lines.append('DRY RUN COMPLETE: no writes performed.')
    lines.append("Set APPLY=True and CONFIRM='RESTORE_DELIVERY_POINT' to restore.")
    raise UserError('\n'.join(lines)[:90000])
if CONFIRM != 'RESTORE_DELIVERY_POINT':
    raise UserError('\n'.join(lines) + "\nERROR: wrong CONFIRM.")
try:
    env.cr.execute('SAVEPOINT sp_delivery_restore')
    body.write({'arch_db': body_arch, 'key': BODY_KEY, 'type': 'qweb', 'inherit_id': False})
    layout.write({'arch_db': layout_arch, 'key': LAYOUT_KEY, 'type': 'qweb', 'inherit_id': False})
    if paper.exists():
        vals = {}
        for fld in ['margin_top', 'margin_bottom', 'margin_left', 'margin_right', 'header_spacing']:
            v = Param.get_param(prefix + '.paper.' + fld, '')
            if v != '':
                vals[fld] = float(v)
        dpi = Param.get_param(prefix + '.paper.dpi', '')
        if dpi != '':
            vals['dpi'] = int(float(dpi))
        if vals:
            paper.write(vals)
    report.write({'name': report_name, 'report_name': BODY_KEY, 'report_file': BODY_KEY, 'print_report_name': print_name, 'paperformat_id': paper.id if paper.exists() else False})
    if cache_inv_method == 'env.invalidate_all':
        env.invalidate_all()
    else:
        env.cache.invalidate()
    env.cr.execute('RELEASE SAVEPOINT sp_delivery_restore')
    lines.append('PASS: restore complete.')
except Exception as e:
    try:
        env.cr.execute('ROLLBACK TO SAVEPOINT sp_delivery_restore')
        env.cr.execute('RELEASE SAVEPOINT sp_delivery_restore')
    except Exception:
        pass
    lines.append('RESTORE FAILED: %s' % str(e)[:1000])
    raise UserError('\n'.join(lines)[:90000])
raise UserError('\n'.join(lines)[:90000])
