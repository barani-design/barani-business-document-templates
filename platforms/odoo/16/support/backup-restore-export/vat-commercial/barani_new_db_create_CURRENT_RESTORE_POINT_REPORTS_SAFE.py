# ============================================================================
# ACTION NAME : BARANI new-DB reports — CREATE CURRENT RESTORE POINT SAFE
# MODEL       : Module (ir.module.module) or any model; selected records ignored.
# ACTION TO DO: Execute Python Code
# RUN BY      : Run APPLY=False first; then APPLY=True + CONFIRM='CREATE_BARANI_REPORTS_RESTORE_POINT'.
# PURPOSE     : Snapshot the CURRENT live BARANI VAT + Commercial report/template
#               state into ir.config_parameter keys, so later experiments can be
#               rolled back/audited from this exact installed baseline.
# WRITES      : ir.config_parameter only. Does NOT write ir.ui.view, report,
#               paperformat, invoices, accounting entries, taxes, products,
#               journals, sequences, or live Odoo/DDS/Studio reports.
# SAFE_EVAL   : no import/def/lambda/comprehension/with/getattr/hasattr/setattr/
#               eval/exec/open/dir/isinstance in executable code.
# ============================================================================

APPLY = False
CONFIRM = ''
BACKUP_TAG = 'new_db_reports_current_20260609'
BACKUP_PREFIX = 'barani.new_db_report_restore_point.' + BACKUP_TAG
ALLOW_OVERWRITE = False

VAT_IDS_PARAMETER_KEY = 'barani.vat_report.ids'
COM_IDS_PARAMETER_KEY = 'barani.commercial_report.ids'
CURRENT_PARAMETER_KEY = 'barani.new_db_report_restore_point.current'
OUTPUT_PARAMETER_KEY = 'barani.new_db_report_restore_point.last_run'

VAT_VIEW_KEY = 'barani_vat.report_invoice_document_vat'
VAT_LAYOUT_KEY = 'barani_vat.external_layout_standard_titled'
VAT_REPORT_KEY = 'barani_vat.report_invoice_document_vat'
COM_BODY_KEY = 'barani_commercial.report_saleorder_document'
COM_LAYOUT_KEY = 'barani_commercial.external_layout_standard_titled'
COM_SALE_WRAPPER_KEY = 'barani_commercial.report_saleorder'
COM_PF_WRAPPER_KEY = 'barani_commercial.report_saleorder_proforma'

ACTION_NAME = 'BARANI new-DB reports — CREATE CURRENT RESTORE POINT SAFE'

View = env['ir.ui.view'].sudo()
Report = env['ir.actions.report'].sudo()
Paper = env['report.paperformat'].sudo()
Param = env['ir.config_parameter'].sudo()

lines = []
lines.append(ACTION_NAME)
lines.append('APPLY=%s CONFIRM=%s BACKUP_TAG=%s' % (APPLY, CONFIRM, BACKUP_TAG))
lines.append('WRITES: ir.config_parameter only; no report/view/paper/invoice/accounting writes.')
lines.append('')

# Resolve VAT.
vat_ids = Param.get_param(VAT_IDS_PARAMETER_KEY, '') or ''
vat_parts = vat_ids.split(',') if vat_ids else []
vat_view = View.browse(int(vat_parts[0])) if len(vat_parts) >= 1 and vat_parts[0] else View.search([('key', '=', VAT_VIEW_KEY)], limit=1)
vat_report = Report.browse(int(vat_parts[1])) if len(vat_parts) >= 2 and vat_parts[1] else Report.search([('report_name', '=', VAT_REPORT_KEY), ('model', '=', 'account.move')], limit=1)
vat_paper = Paper.browse(int(vat_parts[2])) if len(vat_parts) >= 3 and vat_parts[2] else Paper.search([('name', '=', 'BARANI VAT A4 7mm')], limit=1)
vat_layout = View.browse(int(vat_parts[3])) if len(vat_parts) >= 4 and vat_parts[3] else View.search([('key', '=', VAT_LAYOUT_KEY)], limit=1)

# Resolve Commercial. ids: body,sale_report,pf_report,paper,layout,sale_wrapper,pf_wrapper.
com_ids = Param.get_param(COM_IDS_PARAMETER_KEY, '') or ''
com_parts = com_ids.split(',') if com_ids else []
com_body = View.browse(int(com_parts[0])) if len(com_parts) >= 1 and com_parts[0] else View.search([('key', '=', COM_BODY_KEY)], limit=1)
com_sale_report = Report.browse(int(com_parts[1])) if len(com_parts) >= 2 and com_parts[1] else Report.search([('report_name', '=', COM_SALE_WRAPPER_KEY), ('model', '=', 'sale.order')], limit=1)
com_pf_report = Report.browse(int(com_parts[2])) if len(com_parts) >= 3 and com_parts[2] else Report.search([('report_name', '=', COM_PF_WRAPPER_KEY), ('model', '=', 'sale.order')], limit=1)
com_paper = Paper.browse(int(com_parts[3])) if len(com_parts) >= 4 and com_parts[3] else Paper.search([('name', '=', 'BARANI Commercial A4 7mm')], limit=1)
com_layout = View.browse(int(com_parts[4])) if len(com_parts) >= 5 and com_parts[4] else View.search([('key', '=', COM_LAYOUT_KEY)], limit=1)
com_sale_wrapper = View.browse(int(com_parts[5])) if len(com_parts) >= 6 and com_parts[5] else View.search([('key', '=', COM_SALE_WRAPPER_KEY)], limit=1)
com_pf_wrapper = View.browse(int(com_parts[6])) if len(com_parts) >= 7 and com_parts[6] else View.search([('key', '=', COM_PF_WRAPPER_KEY)], limit=1)

lines.append('RESOLVED ARTIFACTS')
lines.append('  VAT ids %s = %r' % (VAT_IDS_PARAMETER_KEY, vat_ids))
lines.append('    VAT view/report/paper/layout = %s/%s/%s/%s' % (vat_view.id if vat_view else 0, vat_report.id if vat_report else 0, vat_paper.id if vat_paper else 0, vat_layout.id if vat_layout else 0))
lines.append('    VAT report name=%r technical=%r' % (vat_report.name if vat_report else '', vat_report.report_name if vat_report else ''))
lines.append('  Commercial ids %s = %r' % (COM_IDS_PARAMETER_KEY, com_ids))
lines.append('    commercial body/sale_report/pf_report/paper/layout/sale_wrapper/pf_wrapper = %s/%s/%s/%s/%s/%s/%s' % (com_body.id if com_body else 0, com_sale_report.id if com_sale_report else 0, com_pf_report.id if com_pf_report else 0, com_paper.id if com_paper else 0, com_layout.id if com_layout else 0, com_sale_wrapper.id if com_sale_wrapper else 0, com_pf_wrapper.id if com_pf_wrapper else 0))
lines.append('    sale report=%r pf report=%r' % (com_sale_report.name if com_sale_report else '', com_pf_report.name if com_pf_report else ''))

errors = []
if not vat_view or vat_view.key != VAT_VIEW_KEY:
    errors.append('VAT view identity failed')
if not vat_layout or vat_layout.key != VAT_LAYOUT_KEY:
    errors.append('VAT layout identity failed')
if not vat_report or vat_report.model != 'account.move' or vat_report.report_name != VAT_REPORT_KEY or vat_report.report_file != VAT_REPORT_KEY:
    errors.append('VAT report identity failed')
if not vat_paper:
    errors.append('VAT paperformat missing')
if not com_body or com_body.key != COM_BODY_KEY:
    errors.append('commercial body identity failed')
if not com_layout or com_layout.key != COM_LAYOUT_KEY:
    errors.append('commercial layout identity failed')
if not com_sale_wrapper or com_sale_wrapper.key != COM_SALE_WRAPPER_KEY:
    errors.append('commercial sale wrapper identity failed')
if not com_pf_wrapper or com_pf_wrapper.key != COM_PF_WRAPPER_KEY:
    errors.append('commercial PF wrapper identity failed')
if not com_sale_report or com_sale_report.model != 'sale.order' or com_sale_report.report_name != COM_SALE_WRAPPER_KEY:
    errors.append('commercial sale report identity failed')
if not com_pf_report or com_pf_report.model != 'sale.order' or com_pf_report.report_name != COM_PF_WRAPPER_KEY:
    errors.append('commercial PF report identity failed')
if not com_paper:
    errors.append('commercial paperformat missing')
if errors:
    lines.append('ERRORS')
    for e in errors:
        lines.append('  ' + e)
    raise UserError('\n'.join(lines)[:90000])
lines.append('PASS: identity checks passed.')
lines.append('')

vat_arch = vat_view.arch_db or ''
vat_layout_arch = vat_layout.arch_db or ''
com_body_arch = com_body.arch_db or ''
com_layout_arch = com_layout.arch_db or ''
com_sale_wrapper_arch = com_sale_wrapper.arch_db or ''
com_pf_wrapper_arch = com_pf_wrapper.arch_db or ''

lines.append('BASELINE MARKER CHECK')
checks = [
    ['VAT EORI present', 'EORI:' in vat_layout_arch],
    ['VAT print label production', vat_report.name == 'VAT Invoices RI/DPI - 2026+'],
    ['VAT Incoterms Not specified', 'Not specified' in vat_arch and 'barani_incoterms_code_name' in vat_arch],
    ['VAT address wrap/gutter', 'barani_addr_block .col-6' in vat_arch and 'padding-right: 18px' in vat_arch],
    ['VAT confirmed-bank fallback', 'barani_company_receiving_bank' in vat_arch and 'barani_pay_bank' in vat_arch],
    ['VAT credit-note cleanup', 'Amount credited' in vat_arch and 'barani_is_customer_credit_note' in vat_arch],
    ['Commercial print labels', com_sale_report.name == 'Quotation / Order — 2026+' and com_pf_report.name == 'PRO-FORMA — 2026+'],
    ['Commercial Incoterms Not specified', 'Not specified' in com_body_arch],
    ['Commercial bank band', 'Bank transfer:' in com_body_arch and 'SWIFT/BIC' in com_body_arch],
    ['Commercial address wrap/gutter', 'barani_addr_block .col-6' in com_body_arch and 'padding-right: 18px' in com_body_arch],
]
marker_error = False
for c in checks:
    lines.append('  %s: %s' % (c[0], 'PASS' if c[1] else 'FAIL'))
    if not c[1]:
        marker_error = True
if marker_error:
    lines.append('ERROR: current templates do not look like the intended current new-DB baseline. Refusing to snapshot.')
    raise UserError('\n'.join(lines)[:90000])
lines.append('')

exists_now = bool(Param.get_param(BACKUP_PREFIX + '.created', ''))
lines.append('BACKUP POINT TARGET')
lines.append('  prefix=%s' % BACKUP_PREFIX)
lines.append('  exists_now=%s' % exists_now)
if exists_now and not ALLOW_OVERWRITE:
    lines.append('ERROR: restore point already exists and ALLOW_OVERWRITE=False. Change BACKUP_TAG or set ALLOW_OVERWRITE=True deliberately.')
    raise UserError('\n'.join(lines)[:90000])
lines.append('')

lines.append('PLAN')
lines.append('  - store VAT arch/layout/report/paper metadata under %s.*' % BACKUP_PREFIX)
lines.append('  - store Commercial body/layout/wrappers/report/paper metadata under %s.*' % BACKUP_PREFIX)
lines.append('  - set %s = %s' % (CURRENT_PARAMETER_KEY, BACKUP_TAG))
lines.append('  - NO ir.ui.view/report/paper/invoice/accounting/tax/product records will be changed')
lines.append('')

if not APPLY:
    lines.append('DRY RUN COMPLETE: no writes performed.')
    lines.append("Set APPLY=True and CONFIRM='CREATE_BARANI_REPORTS_RESTORE_POINT' to create the restore point.")
    raise UserError('\n'.join(lines)[:90000])
if CONFIRM != 'CREATE_BARANI_REPORTS_RESTORE_POINT':
    lines.append('ERROR: APPLY=True but CONFIRM mismatch. Refusing.')
    raise UserError('\n'.join(lines)[:90000])

# Writes only ir.config_parameter.
# Build group id strings without comprehensions.
vat_group_text = ''
for g in vat_report.groups_id:
    if vat_group_text:
        vat_group_text = vat_group_text + ','
    vat_group_text = vat_group_text + str(g.id)
com_sale_group_text = ''
for g in com_sale_report.groups_id:
    if com_sale_group_text:
        com_sale_group_text = com_sale_group_text + ','
    com_sale_group_text = com_sale_group_text + str(g.id)
com_pf_group_text = ''
for g in com_pf_report.groups_id:
    if com_pf_group_text:
        com_pf_group_text = com_pf_group_text + ','
    com_pf_group_text = com_pf_group_text + str(g.id)

Param.set_param(BACKUP_PREFIX + '.created', '1')
Param.set_param(BACKUP_PREFIX + '.vat.ids', '%s,%s,%s,%s' % (vat_view.id, vat_report.id, vat_paper.id, vat_layout.id))
Param.set_param(BACKUP_PREFIX + '.vat.view_arch', vat_arch)
Param.set_param(BACKUP_PREFIX + '.vat.layout_arch', vat_layout_arch)
Param.set_param(BACKUP_PREFIX + '.vat.report.name', vat_report.name or '')
Param.set_param(BACKUP_PREFIX + '.vat.report.print_report_name', vat_report.print_report_name or '')
Param.set_param(BACKUP_PREFIX + '.vat.report.groups_id', vat_group_text)
Param.set_param(BACKUP_PREFIX + '.vat.paper.margin_top', str(vat_paper.margin_top))
Param.set_param(BACKUP_PREFIX + '.vat.paper.margin_bottom', str(vat_paper.margin_bottom))
Param.set_param(BACKUP_PREFIX + '.vat.paper.margin_left', str(vat_paper.margin_left))
Param.set_param(BACKUP_PREFIX + '.vat.paper.margin_right', str(vat_paper.margin_right))
Param.set_param(BACKUP_PREFIX + '.vat.paper.header_spacing', str(vat_paper.header_spacing))
Param.set_param(BACKUP_PREFIX + '.vat.paper.dpi', str(vat_paper.dpi))
Param.set_param(BACKUP_PREFIX + '.commercial.ids', '%s,%s,%s,%s,%s,%s,%s' % (com_body.id, com_sale_report.id, com_pf_report.id, com_paper.id, com_layout.id, com_sale_wrapper.id, com_pf_wrapper.id))
Param.set_param(BACKUP_PREFIX + '.commercial.body_arch', com_body_arch)
Param.set_param(BACKUP_PREFIX + '.commercial.layout_arch', com_layout_arch)
Param.set_param(BACKUP_PREFIX + '.commercial.sale_wrapper_arch', com_sale_wrapper_arch)
Param.set_param(BACKUP_PREFIX + '.commercial.pf_wrapper_arch', com_pf_wrapper_arch)
Param.set_param(BACKUP_PREFIX + '.commercial.sale_report.name', com_sale_report.name or '')
Param.set_param(BACKUP_PREFIX + '.commercial.pf_report.name', com_pf_report.name or '')
Param.set_param(BACKUP_PREFIX + '.commercial.sale_report.print_report_name', com_sale_report.print_report_name or '')
Param.set_param(BACKUP_PREFIX + '.commercial.pf_report.print_report_name', com_pf_report.print_report_name or '')
Param.set_param(BACKUP_PREFIX + '.commercial.sale_report.groups_id', com_sale_group_text)
Param.set_param(BACKUP_PREFIX + '.commercial.pf_report.groups_id', com_pf_group_text)
Param.set_param(BACKUP_PREFIX + '.commercial.paper.margin_top', str(com_paper.margin_top))
Param.set_param(BACKUP_PREFIX + '.commercial.paper.margin_bottom', str(com_paper.margin_bottom))
Param.set_param(BACKUP_PREFIX + '.commercial.paper.margin_left', str(com_paper.margin_left))
Param.set_param(BACKUP_PREFIX + '.commercial.paper.margin_right', str(com_paper.margin_right))
Param.set_param(BACKUP_PREFIX + '.commercial.paper.header_spacing', str(com_paper.header_spacing))
Param.set_param(BACKUP_PREFIX + '.commercial.paper.dpi', str(com_paper.dpi))
Param.set_param(BACKUP_PREFIX + '.meta', 'BARANI new-DB report restore point for VAT RI/DPI/CN + Commercial Q/SO/PF')
Param.set_param(CURRENT_PARAMETER_KEY, BACKUP_TAG)

try:
    env.invalidate_all()
except Exception:
    env.cache.invalidate()
lines.append('PASS: created current restore point %s.' % BACKUP_TAG)
lines.append('BACKUP COMPLETE.')
text = '\n'.join(lines)
Param.set_param(OUTPUT_PARAMETER_KEY, text)
param = Param.search([('key', '=', OUTPUT_PARAMETER_KEY)], limit=1)
action = {'type': 'ir.actions.act_window', 'name': ACTION_NAME, 'res_model': 'ir.config_parameter', 'view_mode': 'form', 'res_id': param.id, 'target': 'current'}
