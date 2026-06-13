# ============================================================================
# ACTION NAME : BARANI new-DB reports — RESTORE FROM CURRENT RESTORE POINT SAFE
# MODEL       : Module (ir.module.module) or any model; selected records ignored.
# ACTION TO DO: Execute Python Code
# RUN BY      : Run APPLY=False first; then APPLY=True + CONFIRM='RESTORE_BARANI_REPORTS_POINT'.
# PURPOSE     : Restore both isolated BARANI report families from the current
#               restore point created by the companion backup script.
# WRITES      : Only BARANI-owned report artifacts: VAT views/report/paper and
#               Commercial views/reports/paper. Does NOT write invoices,
#               accounting entries, taxes, products, journals, sequences, or
#               stock/live Odoo reports.
# SAFE_EVAL   : no import/def/lambda/comprehension/with/getattr/hasattr/setattr/
#               eval/exec/open/dir/isinstance in executable code.
# ============================================================================

APPLY = False
CONFIRM = ''
CURRENT_KEY = 'barani.new_db_reports.restore_point.current'
BACKUP_TAG = ''  # leave empty to use CURRENT_KEY; set explicitly only if needed
OUTPUT_PARAMETER_KEY = 'barani.new_db_reports.restore_point.restore.last_run'

VAT_IDS_KEY = 'barani.vat_report.ids'
COM_IDS_KEY = 'barani.commercial_report.ids'
VAT_VIEW_KEY = 'barani_vat.report_invoice_document_vat'
VAT_VIEW_NAME = 'BARANI VAT report_invoice_document (commercial/VAT layout) v02'
VAT_LAYOUT_KEY = 'barani_vat.external_layout_standard_titled'
VAT_LAYOUT_NAME = 'BARANI VAT external_layout_standard_titled (logo + title header)'
VAT_REPORT_KEY = 'barani_vat.report_invoice_document_vat'
VAT_PAPER_NAME = 'BARANI VAT A4 7mm'
COM_LAYOUT_KEY = 'barani_commercial.external_layout_standard_titled'
COM_LAYOUT_NAME = 'BARANI Commercial external_layout_standard_titled'
COM_BODY_KEY = 'barani_commercial.report_saleorder_document'
COM_BODY_NAME = 'BARANI Commercial sale.order document body'
COM_SALE_WRAPPER_KEY = 'barani_commercial.report_saleorder'
COM_SALE_WRAPPER_NAME = 'BARANI Commercial Quotation / Sales Order wrapper'
COM_PF_WRAPPER_KEY = 'barani_commercial.report_saleorder_proforma'
COM_PF_WRAPPER_NAME = 'BARANI Commercial Pro-forma wrapper'
COM_SALE_REPORT_KEY = COM_SALE_WRAPPER_KEY
COM_PF_REPORT_KEY = COM_PF_WRAPPER_KEY
COM_PAPER_NAME = 'BARANI Commercial A4 7mm'

PRINT_REPORT_NAME_EXPR = "('Credit Note' if object.move_type == 'out_refund' else 'Vendor Credit Note' if object.move_type == 'in_refund' else 'Vendor Bill' if object.move_type == 'in_invoice' else 'Draft Invoice' if object.state == 'draft' else 'Cancelled Invoice' if object.state == 'cancel' else 'Invoice') + ((' ' + object.name) if object.name and object.name != '/' else '')"
SALE_PRINT_REPORT_NAME_EXPR = "('Quotation - ' if object.state in ('draft','sent') else 'Sales Order - ') + (object.name or '')"
PF_PRINT_REPORT_NAME_EXPR = "'Pro-Forma - ' + (object.name or '')"

ACTION_NAME = 'BARANI new-DB reports — RESTORE FROM CURRENT RESTORE POINT SAFE'

View = env['ir.ui.view'].sudo()
Report = env['ir.actions.report'].sudo()
Paper = env['report.paperformat'].sudo()
Model = env['ir.model'].sudo()
Param = env['ir.config_parameter'].sudo()

lines = []
lines.append(ACTION_NAME)
lines.append('APPLY=%s CONFIRM=%s' % (APPLY, CONFIRM))
if not BACKUP_TAG:
    BACKUP_TAG = Param.get_param(CURRENT_KEY, '') or ''
lines.append('BACKUP_TAG=%s' % BACKUP_TAG)
if not BACKUP_TAG:
    lines.append('ERROR: No current restore-point tag found in %s.' % CURRENT_KEY)
    raise UserError('\n'.join(lines)[:90000])
BACKUP_PREFIX = 'barani.new_db_reports.restore_point.' + BACKUP_TAG

manual_sp_ok = False
cache_inv_method = ''
lines.append('')
lines.append('TEST 0 - manual SQL savepoint recovery + ORM cache invalidation')
try:
    env.cr.execute('SAVEPOINT t0_ok')
    env.cr.execute('SELECT 1')
    env.cr.execute('RELEASE SAVEPOINT t0_ok')
    env.cr.execute('SAVEPOINT t0_fail')
    try:
        env.cr.execute('SELECT * FROM __barani_missing_table_for_rollback_probe__')
        env.cr.execute('RELEASE SAVEPOINT t0_fail')
    except Exception:
        env.cr.execute('ROLLBACK TO SAVEPOINT t0_fail')
        env.cr.execute('RELEASE SAVEPOINT t0_fail')
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
            manual_sp_ok = True
            lines.append('PASS: SAVEPOINT recovery works; cache method=%s' % cache_inv_method)
except Exception as e0:
    lines.append('FATAL TEST 0: %s' % str(e0)[:500])
if not manual_sp_ok:
    lines.append('STOP: savepoint/cache mechanism unusable.')
    raise UserError('\n'.join(lines)[:90000])
lines.append('')

# Read backup payload.
created = Param.get_param(BACKUP_PREFIX + '.created', '') or ''
vat_view_arch = Param.get_param(BACKUP_PREFIX + '.vat.view_arch', '') or ''
vat_layout_arch = Param.get_param(BACKUP_PREFIX + '.vat.layout_arch', '') or ''
com_layout_arch = Param.get_param(BACKUP_PREFIX + '.commercial.layout_arch', '') or ''
com_body_arch = Param.get_param(BACKUP_PREFIX + '.commercial.body_arch', '') or ''
com_sale_wrapper_arch = Param.get_param(BACKUP_PREFIX + '.commercial.sale_wrapper_arch', '') or ''
com_pf_wrapper_arch = Param.get_param(BACKUP_PREFIX + '.commercial.pf_wrapper_arch', '') or ''
vat_report_name = Param.get_param(BACKUP_PREFIX + '.vat.report_name', '') or 'VAT Invoices RI/DPI - 2026+'
com_sale_report_name = Param.get_param(BACKUP_PREFIX + '.commercial.sale_report_name', '') or 'Quotation / Order — 2026+'
com_pf_report_name = Param.get_param(BACKUP_PREFIX + '.commercial.pf_report_name', '') or 'PRO-FORMA — 2026+'
if not created or not vat_view_arch or not vat_layout_arch or not com_layout_arch or not com_body_arch or not com_sale_wrapper_arch or not com_pf_wrapper_arch:
    lines.append('ERROR: restore point payload is incomplete. Refusing.')
    raise UserError('\n'.join(lines)[:90000])

marker_error = False
checks = [
    ('backup VAT looks current', 'EORI' in vat_layout_arch and 'Prepared by / Issued by' in vat_view_arch and 'Amount credited' in vat_view_arch),
    ('backup VAT bank fallback present', 'barani_company_receiving_banks' in vat_view_arch),
    ('backup Commercial looks current', 'Bank transfer:' in com_body_arch and 'Not specified' in com_body_arch),
    ('backup Commercial wrappers valid', COM_SALE_WRAPPER_KEY in com_sale_wrapper_arch and COM_PF_WRAPPER_KEY in com_pf_wrapper_arch),
]
lines.append('RESTORE POINT MARKER CHECK')
for chk in checks:
    lines.append('  %s: %s' % (chk[0], 'PASS' if chk[1] else 'FAIL'))
    if not chk[1]:
        marker_error = True
if marker_error:
    lines.append('ERROR: restore point does not look like current new-DB report baseline. Refusing.')
    raise UserError('\n'.join(lines)[:90000])
lines.append('')

# Resolve current target records by technical identity.
vat_view = View.search([('key', '=', VAT_VIEW_KEY)], limit=1)
vat_layout = View.search([('key', '=', VAT_LAYOUT_KEY)], limit=1)
vat_report = Report.search([('report_name', '=', VAT_REPORT_KEY)], limit=1)
vat_paper = Paper.search([('name', '=', VAT_PAPER_NAME)], limit=1)
com_layout = View.search([('key', '=', COM_LAYOUT_KEY)], limit=1)
com_body = View.search([('key', '=', COM_BODY_KEY)], limit=1)
sale_wrapper = View.search([('key', '=', COM_SALE_WRAPPER_KEY)], limit=1)
pf_wrapper = View.search([('key', '=', COM_PF_WRAPPER_KEY)], limit=1)
sale_report = Report.search([('report_name', '=', COM_SALE_REPORT_KEY)], limit=1)
pf_report = Report.search([('report_name', '=', COM_PF_REPORT_KEY)], limit=1)
com_paper = Paper.search([('name', '=', COM_PAPER_NAME)], limit=1)
move_model = Model.search([('model', '=', 'account.move')], limit=1)
sale_model = Model.search([('model', '=', 'sale.order')], limit=1)
if not move_model or not sale_model:
    lines.append('ERROR: account.move or sale.order model missing. Refusing.')
    raise UserError('\n'.join(lines)[:90000])

lines.append('CURRENT TARGETS')
lines.append('  VAT view=%s layout=%s report=%s paper=%s' % (vat_view.id if vat_view else 0, vat_layout.id if vat_layout else 0, vat_report.id if vat_report else 0, vat_paper.id if vat_paper else 0))
lines.append('  Commercial layout=%s body=%s sale_wrapper=%s pf_wrapper=%s sale_report=%s pf_report=%s paper=%s' % (com_layout.id if com_layout else 0, com_body.id if com_body else 0, sale_wrapper.id if sale_wrapper else 0, pf_wrapper.id if pf_wrapper else 0, sale_report.id if sale_report else 0, pf_report.id if pf_report else 0, com_paper.id if com_paper else 0))
lines.append('')

lines.append('PLAN')
lines.append('  - restore/create VAT view/layout/report/paper from backup')
lines.append('  - restore/create Commercial layout/body/wrappers/reports/paper from backup')
lines.append('  - update stored id parameters')
lines.append('  - no invoice/accounting/tax/product/sequences writes')
lines.append('')
if not APPLY:
    lines.append('DRY RUN COMPLETE: no writes performed.')
    lines.append("Set APPLY=True and CONFIRM='RESTORE_BARANI_REPORTS_POINT' to restore.")
    raise UserError('\n'.join(lines)[:90000])
if CONFIRM != 'RESTORE_BARANI_REPORTS_POINT':
    lines.append('ERROR: APPLY=True but CONFIRM mismatch. Refusing.')
    raise UserError('\n'.join(lines)[:90000])

try:
    env.cr.execute('SAVEPOINT sp_barani_reports_restore')
    if not vat_paper:
        vat_paper = Paper.create({'name': VAT_PAPER_NAME, 'format': 'A4', 'orientation': 'Portrait', 'margin_top': 40.0, 'margin_bottom': 18.0, 'margin_left': 7.0, 'margin_right': 7.0, 'header_spacing': 35.0, 'header_line': False, 'dpi': 90})
    if not com_paper:
        com_paper = Paper.create({'name': COM_PAPER_NAME, 'format': 'A4', 'orientation': 'Portrait', 'margin_top': 40.0, 'margin_bottom': 18.0, 'margin_left': 7.0, 'margin_right': 7.0, 'header_spacing': 35.0, 'header_line': False, 'dpi': 90})
    if vat_view:
        vat_view.write({'name': VAT_VIEW_NAME, 'key': VAT_VIEW_KEY, 'type': 'qweb', 'inherit_id': False, 'arch_db': vat_view_arch})
    else:
        vat_view = View.create({'name': VAT_VIEW_NAME, 'key': VAT_VIEW_KEY, 'type': 'qweb', 'arch_db': vat_view_arch})
    if vat_layout:
        vat_layout.write({'name': VAT_LAYOUT_NAME, 'key': VAT_LAYOUT_KEY, 'type': 'qweb', 'inherit_id': False, 'arch_db': vat_layout_arch})
    else:
        vat_layout = View.create({'name': VAT_LAYOUT_NAME, 'key': VAT_LAYOUT_KEY, 'type': 'qweb', 'arch_db': vat_layout_arch})
    if vat_report:
        vat_report.write({'name': vat_report_name, 'model': 'account.move', 'report_type': 'qweb-pdf', 'report_name': VAT_REPORT_KEY, 'report_file': VAT_REPORT_KEY, 'binding_model_id': move_model.id, 'binding_type': 'report', 'paperformat_id': vat_paper.id, 'print_report_name': Param.get_param(BACKUP_PREFIX + '.vat.report_print_report_name', '') or PRINT_REPORT_NAME_EXPR})
    else:
        vat_report = Report.create({'name': vat_report_name, 'model': 'account.move', 'report_type': 'qweb-pdf', 'report_name': VAT_REPORT_KEY, 'report_file': VAT_REPORT_KEY, 'binding_model_id': move_model.id, 'binding_type': 'report', 'paperformat_id': vat_paper.id, 'print_report_name': PRINT_REPORT_NAME_EXPR})
    if com_layout:
        com_layout.write({'name': COM_LAYOUT_NAME, 'key': COM_LAYOUT_KEY, 'type': 'qweb', 'inherit_id': False, 'arch_db': com_layout_arch})
    else:
        com_layout = View.create({'name': COM_LAYOUT_NAME, 'key': COM_LAYOUT_KEY, 'type': 'qweb', 'arch_db': com_layout_arch})
    if com_body:
        com_body.write({'name': COM_BODY_NAME, 'key': COM_BODY_KEY, 'type': 'qweb', 'inherit_id': False, 'arch_db': com_body_arch})
    else:
        com_body = View.create({'name': COM_BODY_NAME, 'key': COM_BODY_KEY, 'type': 'qweb', 'arch_db': com_body_arch})
    if sale_wrapper:
        sale_wrapper.write({'name': COM_SALE_WRAPPER_NAME, 'key': COM_SALE_WRAPPER_KEY, 'type': 'qweb', 'inherit_id': False, 'arch_db': com_sale_wrapper_arch})
    else:
        sale_wrapper = View.create({'name': COM_SALE_WRAPPER_NAME, 'key': COM_SALE_WRAPPER_KEY, 'type': 'qweb', 'arch_db': com_sale_wrapper_arch})
    if pf_wrapper:
        pf_wrapper.write({'name': COM_PF_WRAPPER_NAME, 'key': COM_PF_WRAPPER_KEY, 'type': 'qweb', 'inherit_id': False, 'arch_db': com_pf_wrapper_arch})
    else:
        pf_wrapper = View.create({'name': COM_PF_WRAPPER_NAME, 'key': COM_PF_WRAPPER_KEY, 'type': 'qweb', 'arch_db': com_pf_wrapper_arch})
    if sale_report:
        sale_report.write({'name': com_sale_report_name, 'model': 'sale.order', 'report_type': 'qweb-pdf', 'report_name': COM_SALE_REPORT_KEY, 'report_file': COM_SALE_REPORT_KEY, 'binding_model_id': sale_model.id, 'binding_type': 'report', 'paperformat_id': com_paper.id, 'print_report_name': Param.get_param(BACKUP_PREFIX + '.commercial.sale_print_report_name', '') or SALE_PRINT_REPORT_NAME_EXPR})
    else:
        sale_report = Report.create({'name': com_sale_report_name, 'model': 'sale.order', 'report_type': 'qweb-pdf', 'report_name': COM_SALE_REPORT_KEY, 'report_file': COM_SALE_REPORT_KEY, 'binding_model_id': sale_model.id, 'binding_type': 'report', 'paperformat_id': com_paper.id, 'print_report_name': SALE_PRINT_REPORT_NAME_EXPR})
    if pf_report:
        pf_report.write({'name': com_pf_report_name, 'model': 'sale.order', 'report_type': 'qweb-pdf', 'report_name': COM_PF_REPORT_KEY, 'report_file': COM_PF_REPORT_KEY, 'binding_model_id': sale_model.id, 'binding_type': 'report', 'paperformat_id': com_paper.id, 'print_report_name': Param.get_param(BACKUP_PREFIX + '.commercial.pf_print_report_name', '') or PF_PRINT_REPORT_NAME_EXPR})
    else:
        pf_report = Report.create({'name': com_pf_report_name, 'model': 'sale.order', 'report_type': 'qweb-pdf', 'report_name': COM_PF_REPORT_KEY, 'report_file': COM_PF_REPORT_KEY, 'binding_model_id': sale_model.id, 'binding_type': 'report', 'paperformat_id': com_paper.id, 'print_report_name': PF_PRINT_REPORT_NAME_EXPR})
    Param.set_param(VAT_IDS_KEY, '%s,%s,%s,%s' % (vat_view.id, vat_report.id, vat_paper.id, vat_layout.id))
    Param.set_param(COM_IDS_KEY, '%s,%s,%s,%s,%s,%s,%s' % (com_body.id, sale_report.id, pf_report.id, com_paper.id, com_layout.id, sale_wrapper.id, pf_wrapper.id))
    env.cr.execute('RELEASE SAVEPOINT sp_barani_reports_restore')
    lines.append('PASS: restored BARANI report families from restore point %s.' % BACKUP_TAG)
except Exception as e_apply:
    try:
        env.cr.execute('ROLLBACK TO SAVEPOINT sp_barani_reports_restore')
        env.cr.execute('RELEASE SAVEPOINT sp_barani_reports_restore')
    except Exception as e_rb:
        lines.append('ROLLBACK PROBLEM: %s' % str(e_rb)[:500])
    lines.append('FAILED: %s' % str(e_apply)[:1500])
    raise UserError('\n'.join(lines)[:90000])

if cache_inv_method == 'env.invalidate_all':
    env.invalidate_all()
else:
    env.cache.invalidate()
lines.append('PASS: ORM cache invalidated via %s.' % cache_inv_method)
lines.append('RESTORE COMPLETE.')
text = '\n'.join(lines)
Param.set_param(OUTPUT_PARAMETER_KEY, text)
param = Param.search([('key', '=', OUTPUT_PARAMETER_KEY)], limit=1)
action = {'type': 'ir.actions.act_window', 'name': ACTION_NAME, 'res_model': 'ir.config_parameter', 'view_mode': 'form', 'res_id': param.id, 'target': 'current'}
