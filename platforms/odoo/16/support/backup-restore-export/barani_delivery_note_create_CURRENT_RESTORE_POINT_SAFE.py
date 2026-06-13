# ============================================================================
# ACTION NAME : BARANI Delivery Note 2026 — CREATE CURRENT RESTORE POINT SAFE
# MODEL       : Any model; selected records ignored.
# ACTION TO DO: Execute Python Code
# RUN BY      : Run APPLY=False first; then APPLY=True + CONFIRM='CREATE_DELIVERY_RESTORE_POINT'.
# PURPOSE     : Snapshot the current isolated BARANI Delivery Note 2026 report
#               body/layout/report/paper settings into ir.config_parameter keys.
#
# WRITES      : ir.config_parameter only. Does NOT write ir.ui.view, report,
#               paperformat, picking, stock moves, products, accounting records,
#               or live stock reports.
# SAFE_EVAL   : no import/def/lambda/comprehension/with/getattr/hasattr/setattr/
#               eval/exec/open/dir/isinstance in executable code.
# ============================================================================

APPLY = False
CONFIRM = ''
BACKUP_TAG = 'delivery_note_2026_dn_l1_qr_only_dds_free'
BODY_KEY = 'barani_delivery.report_delivery_note_2026'
LAYOUT_KEY = 'barani_delivery.external_layout_delivery_2026'
IDS_KEY = 'barani.delivery_note_2026.ids'
PREFIX = 'barani.delivery_note_2026.restore_point.' + BACKUP_TAG
CURRENT_KEY = 'barani.delivery_note_2026.restore_point.current'
ACTION_NAME = 'BARANI Delivery Note 2026 — CREATE CURRENT RESTORE POINT SAFE'

View = env['ir.ui.view'].sudo()
Report = env['ir.actions.report'].sudo()
Paper = env['report.paperformat'].sudo()
Param = env['ir.config_parameter'].sudo()

lines = []
lines.append(ACTION_NAME)
lines.append('APPLY=%s CONFIRM=%s BACKUP_TAG=%s' % (APPLY, CONFIRM, BACKUP_TAG))
lines.append('WRITES: ir.config_parameter only; no report/view/paper/picking/product writes.')
lines.append('')

# TEST 0 - savepoint and cache invalidation.
manual_sp_ok = False
cache_inv_method = ''
lines.append('TEST 0 - manual SQL savepoint recovery + ORM cache invalidation')
try:
    env.cr.execute('SAVEPOINT t0_delivery_rp_ok')
    env.cr.execute('SELECT 1')
    env.cr.execute('RELEASE SAVEPOINT t0_delivery_rp_ok')
    env.cr.execute('SAVEPOINT t0_delivery_rp_fail')
    try:
        env.cr.execute('SELECT * FROM __barani_missing_table_for_rollback_probe__')
        env.cr.execute('RELEASE SAVEPOINT t0_delivery_rp_fail')
    except Exception:
        env.cr.execute('ROLLBACK TO SAVEPOINT t0_delivery_rp_fail')
        env.cr.execute('RELEASE SAVEPOINT t0_delivery_rp_fail')
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

body = View.search([('key', '=', BODY_KEY)])
layout = View.search([('key', '=', LAYOUT_KEY)])
report = Report.search([('report_name', '=', BODY_KEY), ('model', '=', 'stock.picking')])
if len(body) != 1 or len(layout) != 1 or len(report) != 1:
    lines.append('ERROR: expected exactly one body/layout/report; found body=%s layout=%s report=%s' % (len(body), len(layout), len(report)))
    raise UserError('\n'.join(lines)[:90000])
paper = report.paperformat_id
lines.append('RESOLVED ARTIFACTS')
lines.append('  body id=%s key=%s len=%s' % (body.id, body.key, len(body.arch_db or '')))
lines.append('  layout id=%s key=%s len=%s' % (layout.id, layout.key, len(layout.arch_db or '')))
lines.append('  report id=%s name=%r' % (report.id, report.name))
lines.append('  paper id=%s name=%r' % (paper.id if paper else 0, paper.name if paper else ''))
markers = [
    ('product QR', 'barcode_type=%s' in (body.arch_db or '') and 'move.product_id.barcode' in (body.arch_db or '')),
    ('delivery table', 'barani_delivery_line_table' in (body.arch_db or '')),
    ('right header title', 'barani_delivery_doc_title_right' in (layout.arch_db or '')),
    ('no EORI from VAT', 'EORI:' not in (layout.arch_db or '')),
    ('no DDS/brn strings', 'dds_' not in (body.arch_db or '') and 'brn_' not in (body.arch_db or '') and 'dds_' not in (layout.arch_db or '') and 'brn_' not in (layout.arch_db or '')),
]
err = False
for name, ok in markers:
    lines.append('  marker %-24s %s' % (name, 'PASS' if ok else 'FAIL'))
    if not ok:
        err = True
if err:
    lines.append('ERROR: marker check failed; refusing backup.')
    raise UserError('\n'.join(lines)[:90000])
exists = bool(Param.get_param(PREFIX + '.created', ''))
lines.append('')
lines.append('TARGET prefix=%s exists_now=%s' % (PREFIX, exists))
if exists:
    lines.append('ERROR: restore point exists; refusing to overwrite.')
    raise UserError('\n'.join(lines)[:90000])
lines.append('')
lines.append('PLAN')
lines.append('  - store current body/layout/report/paper metadata in ir.config_parameter only')
lines.append('  - set %s = %s' % (CURRENT_KEY, BACKUP_TAG))
lines.append('  - NO ir.ui.view/report/paper/picking/product records will be changed')
lines.append('')

if not APPLY:
    lines.append('DRY RUN COMPLETE: no writes performed.')
    lines.append("Set APPLY=True and CONFIRM='CREATE_DELIVERY_RESTORE_POINT' to create.")
    raise UserError('\n'.join(lines)[:90000])
if CONFIRM != 'CREATE_DELIVERY_RESTORE_POINT':
    lines.append('ERROR: APPLY=True but CONFIRM is not CREATE_DELIVERY_RESTORE_POINT.')
    raise UserError('\n'.join(lines)[:90000])

try:
    env.cr.execute('SAVEPOINT sp_delivery_create_restore_point')
    Param.set_param(PREFIX + '.created', '1')
    Param.set_param(PREFIX + '.ids', '%s,%s,%s,%s' % (body.id, report.id, paper.id if paper else 0, layout.id))
    Param.set_param(PREFIX + '.body_arch', body.arch_db or '')
    Param.set_param(PREFIX + '.layout_arch', layout.arch_db or '')
    Param.set_param(PREFIX + '.report.name', report.name or '')
    Param.set_param(PREFIX + '.report.print_report_name', report.print_report_name or '')
    if paper:
        Param.set_param(PREFIX + '.paper.margin_top', str(paper.margin_top))
        Param.set_param(PREFIX + '.paper.margin_bottom', str(paper.margin_bottom))
        Param.set_param(PREFIX + '.paper.margin_left', str(paper.margin_left))
        Param.set_param(PREFIX + '.paper.margin_right', str(paper.margin_right))
        Param.set_param(PREFIX + '.paper.header_spacing', str(paper.header_spacing))
        Param.set_param(PREFIX + '.paper.dpi', str(paper.dpi))
    Param.set_param(CURRENT_KEY, BACKUP_TAG)
    if cache_inv_method == 'env.invalidate_all':
        env.invalidate_all()
    else:
        env.cache.invalidate()
    env.cr.execute('RELEASE SAVEPOINT sp_delivery_create_restore_point')
    lines.append('PASS: created delivery restore point %s.' % BACKUP_TAG)
except Exception as e:
    try:
        env.cr.execute('ROLLBACK TO SAVEPOINT sp_delivery_create_restore_point')
        env.cr.execute('RELEASE SAVEPOINT sp_delivery_create_restore_point')
    except Exception:
        pass
    lines.append('CREATE RESTORE POINT FAILED: %s' % str(e)[:1000])
    raise UserError('\n'.join(lines)[:90000])

raise UserError('\n'.join(lines)[:90000])
