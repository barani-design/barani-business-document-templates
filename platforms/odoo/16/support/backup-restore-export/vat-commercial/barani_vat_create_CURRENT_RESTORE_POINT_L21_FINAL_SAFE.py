# ============================================================================
# ACTION NAME : BARANI VAT REPORT — CREATE CURRENT RESTORE POINT L21 FINAL SAFE
# MODEL       : Module (ir.module.module) or any model; selected records ignored.
# ACTION TO DO: Execute Python Code
# RUN BY      : Run APPLY=False first; then APPLY=True + CONFIRM='CREATE_VAT_RESTORE_POINT'.
# PURPOSE     : Snapshot the CURRENT live isolated BARANI VAT RI/DPI/Credit Note
#               report/template state into fresh ir.config_parameter keys, so the
#               accepted L21 final template can be restored later.
#
# WRITES      : ir.config_parameter only. Does NOT write ir.ui.view, report,
#               paperformat, invoices, accounting entries, taxes, products,
#               journals, sequences, POHODA data, or live buttons 234/236/842/900.
# ============================================================================

APPLY = False
CONFIRM = ''

BACKUP_TAG = 'l21_final_20260609'
BACKUP_PREFIX = 'barani.vat_report.restore_point.' + BACKUP_TAG
ALLOW_OVERWRITE = False

VAT_VIEW_KEY = 'barani_vat.report_invoice_document_vat'
VAT_VIEW_NAME = 'BARANI VAT report_invoice_document (commercial/VAT layout) v02'
VAT_REPORT_NAME = 'VAT Invoices RI/DPI - 2026+'
PAPERFORMAT_NAME = 'BARANI VAT A4 7mm'
LAYOUT_VIEW_KEY = 'barani_vat.external_layout_standard_titled'
LAYOUT_VIEW_NAME = 'BARANI VAT external_layout_standard_titled (logo + title header)'
IDS_PARAMETER_KEY = 'barani.vat_report.ids'
OUTPUT_PARAMETER_KEY = 'barani.vat_report.restore_point.last_run'
CURRENT_PARAMETER_KEY = 'barani.vat_report.restore_point.current'
ACTION_NAME = 'BARANI VAT REPORT — CREATE CURRENT RESTORE POINT L21 FINAL SAFE'

View = env['ir.ui.view'].sudo()
Report = env['ir.actions.report'].sudo()
Paper = env['report.paperformat'].sudo()
Param = env['ir.config_parameter'].sudo()

lines = []
lines.append(ACTION_NAME)
lines.append('APPLY=%s CONFIRM=%s' % (APPLY, CONFIRM))
lines.append('BACKUP_TAG=%s' % BACKUP_TAG)
lines.append('WRITES: ir.config_parameter only; no report/view/paper/invoice/accounting/tax/product writes.')
lines.append('')

# Test savepoint + cache invalidation.
manual_sp_ok = False
cache_inv_method = ''
lines.append('TEST 0 - manual SQL savepoint recovery + ORM cache invalidation')
try:
    env.cr.execute('SAVEPOINT t0_l21_rp_ok')
    env.cr.execute('SELECT 1')
    env.cr.execute('RELEASE SAVEPOINT t0_l21_rp_ok')
    env.cr.execute('SAVEPOINT t0_l21_rp_fail')
    try:
        env.cr.execute('SELECT * FROM __barani_missing_table_for_rollback_probe__')
        env.cr.execute('RELEASE SAVEPOINT t0_l21_rp_fail')
    except Exception:
        env.cr.execute('ROLLBACK TO SAVEPOINT t0_l21_rp_fail')
        env.cr.execute('RELEASE SAVEPOINT t0_l21_rp_fail')
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

# Resolve ids from parameter.
id_text = Param.get_param(IDS_PARAMETER_KEY, '') or ''
view_id = 0
report_id = 0
paper_id = 0
layout_id = 0
if id_text:
    parts = id_text.split(',')
    if len(parts) >= 1:
        try:
            view_id = int(parts[0] or '0')
        except Exception:
            view_id = 0
    if len(parts) >= 2:
        try:
            report_id = int(parts[1] or '0')
        except Exception:
            report_id = 0
    if len(parts) >= 3:
        try:
            paper_id = int(parts[2] or '0')
        except Exception:
            paper_id = 0
    if len(parts) >= 4:
        try:
            layout_id = int(parts[3] or '0')
        except Exception:
            layout_id = 0

vat_view = View.browse(view_id) if view_id else View.search([('key', '=', VAT_VIEW_KEY)], limit=1)
vat_report = Report.browse(report_id) if report_id else Report.search([('report_name', '=', VAT_VIEW_KEY), ('model', '=', 'account.move')], limit=1)
vat_paper = Paper.browse(paper_id) if paper_id else Paper.search([('name', '=', PAPERFORMAT_NAME)], limit=1)
layout_view = View.browse(layout_id) if layout_id else View.search([('key', '=', LAYOUT_VIEW_KEY)], limit=1)

# Duplicate checks.
views_by_key = View.search([('key', '=', VAT_VIEW_KEY)])
layouts_by_key = View.search([('key', '=', LAYOUT_VIEW_KEY)])
reports_by_technical = Report.search([('report_name', '=', VAT_VIEW_KEY), ('model', '=', 'account.move')])
reports_by_name = Report.search([('name', '=', VAT_REPORT_NAME), ('model', '=', 'account.move')])
papers_by_name = Paper.search([('name', '=', PAPERFORMAT_NAME)])

lines.append('RESOLVED ARTIFACTS')
lines.append('  ids param %s = %r' % (IDS_PARAMETER_KEY, id_text))
lines.append('  VAT view:   id=%s key=%r name=%r' % (vat_view.id if vat_view and vat_view.exists() else 0, vat_view.key if vat_view and vat_view.exists() else '', vat_view.name if vat_view and vat_view.exists() else ''))
lines.append('  Report:     id=%s name=%r report_name=%r' % (vat_report.id if vat_report and vat_report.exists() else 0, vat_report.name if vat_report and vat_report.exists() else '', vat_report.report_name if vat_report and vat_report.exists() else ''))
lines.append('  Paper:      id=%s name=%r' % (vat_paper.id if vat_paper and vat_paper.exists() else 0, vat_paper.name if vat_paper and vat_paper.exists() else ''))
lines.append('  Layout:     id=%s key=%r name=%r' % (layout_view.id if layout_view and layout_view.exists() else 0, layout_view.key if layout_view and layout_view.exists() else '', layout_view.name if layout_view and layout_view.exists() else ''))

bad = False
if not vat_view or not vat_view.exists() or vat_view.key != VAT_VIEW_KEY or vat_view.type != 'qweb' or vat_view.inherit_id:
    bad = True
    lines.append('ERROR: VAT view identity check failed.')
if not layout_view or not layout_view.exists() or layout_view.key != LAYOUT_VIEW_KEY or layout_view.type != 'qweb' or layout_view.inherit_id:
    bad = True
    lines.append('ERROR: layout view identity check failed.')
if not vat_report or not vat_report.exists() or vat_report.report_name != VAT_VIEW_KEY or vat_report.report_file != VAT_VIEW_KEY or vat_report.model != 'account.move':
    bad = True
    lines.append('ERROR: report identity check failed.')
if not vat_paper or not vat_paper.exists() or vat_paper.name != PAPERFORMAT_NAME:
    bad = True
    lines.append('ERROR: paperformat identity check failed.')
if len(views_by_key) != 1:
    bad = True
    lines.append('ERROR: VAT view duplicate count=%s.' % len(views_by_key))
if len(layouts_by_key) != 1:
    bad = True
    lines.append('ERROR: layout view duplicate count=%s.' % len(layouts_by_key))
if len(reports_by_technical) != 1:
    bad = True
    lines.append('ERROR: VAT technical report count=%s.' % len(reports_by_technical))
if len(reports_by_name) != 1:
    bad = True
    lines.append('ERROR: production report name count=%s for %r.' % (len(reports_by_name), VAT_REPORT_NAME))
if len(papers_by_name) != 1:
    bad = True
    lines.append('ERROR: paperformat count=%s.' % len(papers_by_name))
if bad:
    raise UserError('\n'.join(lines)[:90000])
lines.append('PASS: identity checks passed.')
lines.append('')

vat_arch = vat_view.arch_db or ''
layout_arch = layout_view.arch_db or ''

lines.append('L21 FINAL MARKER CHECK')
checks = [
    ('production print label', vat_report.name == VAT_REPORT_NAME),
    ('company registration aligned with shipping column', 'name="company_registration" style="font-size:10pt; line-height:1.25; padding-left:18px; box-sizing:border-box;"' in layout_arch),
    ('Down payment reconciliation table present', 'barani_down_payment_reconciliation_table' in vat_arch and 'Down payment reconciliation' in vat_arch and 'Invoice total after down payments' in vat_arch),
    ('negative down-payment base/VAT/total uses 324 line values', 'bvt_rec_dl.price_subtotal' in vat_arch and 'bvt_rec_dl.price_total' in vat_arch),
    ('duplicate gross down-payment rows removed from right totals', 'Total Advances Received' not in vat_arch),
    ('old Advance VAT reconciliation wording absent', 'Advance VAT reconciliation' not in vat_arch),
    ('Tel prefix present', 'Tel: ' in vat_arch),
    ('address no-single-column-indent markers present', 'barani_customer_cell.barani_has_shipping' in vat_arch and '.barani_shipping_cell' in vat_arch),
    ('confirmed receiving bank fallback present', 'barani_company_receiving_banks' in vat_arch and 'barani_effective_bank' in vat_arch),
    ('bank transfer band present', 'barani_bank_transfer_band' in vat_arch and 'Bank transfer:' in vat_arch),
    ('QR omitted', 'o.display_qr_code' not in vat_arch and '_generate_qr_code' not in vat_arch),
    ('right-side title/header present; centered title absent', 'bvt_type_label' in layout_arch and 't-field="o.name"' in layout_arch and 'barani_doc_title' not in layout_arch and 'barani_top_title_divider' in layout_arch),
]
marker_bad = False
for c in checks:
    lines.append('  %s: %s' % (c[0], 'PASS' if c[1] else 'FAIL'))
    if not c[1]:
        marker_bad = True
if marker_bad:
    lines.append('ERROR: L21 marker check failed. Refusing to snapshot as L21 final.')
    raise UserError('\n'.join(lines)[:90000])
lines.append('')

exists_now = bool(Param.get_param(BACKUP_PREFIX + '.created', ''))
lines.append('BACKUP POINT TARGET')
lines.append('  prefix=%s' % BACKUP_PREFIX)
lines.append('  exists_now=%s' % exists_now)
if exists_now and not ALLOW_OVERWRITE:
    lines.append('ERROR: restore point already exists. Change BACKUP_TAG or set ALLOW_OVERWRITE=True intentionally.')
    raise UserError('\n'.join(lines)[:90000])
lines.append('')

bound_ids = vat_report.groups_id.ids
bound_texts = []
for x in bound_ids:
    bound_texts.append(str(x))
bound_text = ','.join(bound_texts)
meta = 'tag=%s; report_id=%s; report_name=%s; view_id=%s; layout_id=%s; paper_id=%s; vat_len=%s; layout_len=%s' % (BACKUP_TAG, vat_report.id, vat_report.name, vat_view.id, layout_view.id, vat_paper.id, len(vat_arch), len(layout_arch))

lines.append('PLAN')
lines.append('  - store current VAT arch in %s.vat_arch len=%s' % (BACKUP_PREFIX, len(vat_arch)))
lines.append('  - store current layout arch in %s.layout_arch len=%s' % (BACKUP_PREFIX, len(layout_arch)))
lines.append('  - store ids/meta/report/paper settings under prefix %s' % BACKUP_PREFIX)
lines.append('  - set %s = %s' % (CURRENT_PARAMETER_KEY, BACKUP_TAG))
lines.append('  - NO ir.ui.view/report/paper/invoice/accounting/tax/product records will be changed')
lines.append('')

if not APPLY:
    lines.append('DRY RUN COMPLETE: no writes performed.')
    lines.append("Set APPLY=True and CONFIRM='CREATE_VAT_RESTORE_POINT' to create the backup point.")
    raise UserError('\n'.join(lines)[:90000])
if CONFIRM != 'CREATE_VAT_RESTORE_POINT':
    lines.append('ERROR: APPLY=True but CONFIRM is not CREATE_VAT_RESTORE_POINT.')
    raise UserError('\n'.join(lines)[:90000])

try:
    env.cr.execute('SAVEPOINT sp_vat_l21_restore_point')
    Param.set_param(BACKUP_PREFIX + '.created', '1')
    Param.set_param(BACKUP_PREFIX + '.ids', '%s,%s,%s,%s' % (vat_view.id, vat_report.id, vat_paper.id, layout_view.id))
    Param.set_param(BACKUP_PREFIX + '.vat_arch', vat_arch)
    Param.set_param(BACKUP_PREFIX + '.layout_arch', layout_arch)
    Param.set_param(BACKUP_PREFIX + '.meta', meta)
    Param.set_param(BACKUP_PREFIX + '.report.name', vat_report.name or '')
    Param.set_param(BACKUP_PREFIX + '.report.print_report_name', vat_report.print_report_name or '')
    Param.set_param(BACKUP_PREFIX + '.report.groups_id', bound_text)
    Param.set_param(BACKUP_PREFIX + '.paper.margin_top', str(vat_paper.margin_top))
    Param.set_param(BACKUP_PREFIX + '.paper.margin_bottom', str(vat_paper.margin_bottom))
    Param.set_param(BACKUP_PREFIX + '.paper.margin_left', str(vat_paper.margin_left))
    Param.set_param(BACKUP_PREFIX + '.paper.margin_right', str(vat_paper.margin_right))
    Param.set_param(BACKUP_PREFIX + '.paper.header_spacing', str(vat_paper.header_spacing))
    Param.set_param(BACKUP_PREFIX + '.paper.dpi', str(vat_paper.dpi))
    Param.set_param(CURRENT_PARAMETER_KEY, BACKUP_TAG)
    Param.set_param(OUTPUT_PARAMETER_KEY, '\n'.join(lines))
    if cache_inv_method == 'env.invalidate_all':
        env.invalidate_all()
    else:
        env.cache.invalidate()
    env.cr.execute('RELEASE SAVEPOINT sp_vat_l21_restore_point')
    lines.append('PASS: created current restore point %s.' % BACKUP_TAG)
    lines.append('PASS: ORM cache invalidated via %s.' % cache_inv_method)
    lines.append('BACKUP COMPLETE. You can restore this L21 state with the companion restore script.')
except Exception as e:
    try:
        env.cr.execute('ROLLBACK TO SAVEPOINT sp_vat_l21_restore_point')
        env.cr.execute('RELEASE SAVEPOINT sp_vat_l21_restore_point')
    except Exception:
        pass
    lines.append('FAILED: %s' % str(e)[:1500])
    raise UserError('\n'.join(lines)[:90000])

raise UserError('\n'.join(lines)[:90000])
