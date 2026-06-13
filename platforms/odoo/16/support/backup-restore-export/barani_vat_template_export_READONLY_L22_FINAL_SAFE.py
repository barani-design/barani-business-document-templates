# ============================================================================
# ACTION NAME : READ-ONLY: BARANI VAT REPORT — TEMPLATE EXPORT L22 FINAL SAFE
# MODEL       : Any model; selected records ignored. account.move is convenient.
# ACTION TO DO: Execute Python Code
# PURPOSE     : Export the CURRENT stored QWeb XML for the isolated BARANI VAT
#               body view and custom layout view after L22 final.
#
# READ-ONLY   : YES. Performs no create/write/unlink/set_param/commit/SQL.
#               Output is raised via UserError for copy/paste backup.
# ============================================================================

WHICH = 'both'      # 'both' | 'vat' | 'layout'
PAGE = 1
PAGE_SIZE = 80000

VAT_VIEW_KEY = 'barani_vat.report_invoice_document_vat'
LAYOUT_VIEW_KEY = 'barani_vat.external_layout_standard_titled'
IDS_PARAMETER_KEY = 'barani.vat_report.ids'
ACTION_NAME = 'READ-ONLY: BARANI VAT REPORT — TEMPLATE EXPORT L22 FINAL SAFE'

if PAGE < 1:
    raise UserError('PAGE must be >= 1')

View = env['ir.ui.view'].sudo()
Report = env['ir.actions.report'].sudo()
Paper = env['report.paperformat'].sudo()
Param = env['ir.config_parameter'].sudo()

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

vat_view = View.browse(view_id)
layout_view = View.browse(layout_id)
vat_report = Report.browse(report_id)
vat_paper = Paper.browse(paper_id)
if not vat_view.exists():
    vat_view = View.search([('key', '=', VAT_VIEW_KEY)], limit=1)
if not layout_view.exists():
    layout_view = View.search([('key', '=', LAYOUT_VIEW_KEY)], limit=1)
if not vat_report.exists():
    candidates = Report.search([('model', '=', 'account.move'), ('report_type', '=', 'qweb-pdf'), ('report_name', '=', VAT_VIEW_KEY), ('report_file', '=', VAT_VIEW_KEY)])
    if len(candidates) == 1:
        vat_report = candidates
if not vat_paper.exists():
    if vat_report and vat_report.exists() and vat_report.paperformat_id:
        vat_paper = vat_report.paperformat_id

vat_arch = vat_view.arch_db or ''
layout_arch = layout_view.arch_db or ''

lines = []
lines.append(ACTION_NAME)
lines.append('READ-ONLY:YES — search/read only; no writes. PAGE=%s PAGE_SIZE=%s' % (PAGE, PAGE_SIZE))
lines.append("WHICH=%r PAGE=%s PAGE_SIZE=%s" % (WHICH, PAGE, PAGE_SIZE))
lines.append('')
lines.append('RESOLVED ARTIFACTS')
lines.append('  stored ids %s = %r' % (IDS_PARAMETER_KEY, id_text))
lines.append('  VAT view:    id=%s key=%r name=%r type=%s inherit_id=%s write_date=%s' % (vat_view.id if vat_view else 0, vat_view.key if vat_view else '', vat_view.name if vat_view else '', vat_view.type if vat_view else '', vat_view.inherit_id.id if (vat_view and vat_view.inherit_id) else False, vat_view.write_date if vat_view else ''))
lines.append('  Layout view: id=%s key=%r name=%r type=%s inherit_id=%s write_date=%s' % (layout_view.id if layout_view else 0, layout_view.key if layout_view else '', layout_view.name if layout_view else '', layout_view.type if layout_view else '', layout_view.inherit_id.id if (layout_view and layout_view.inherit_id) else False, layout_view.write_date if layout_view else ''))
lines.append('  VAT report:  id=%s name=%r model=%s report_name=%s paperformat_id=%s print_report_name=%r' % (vat_report.id if vat_report else 0, vat_report.name if vat_report else '', vat_report.model if vat_report else '', vat_report.report_name if vat_report else '', vat_report.paperformat_id.id if (vat_report and vat_report.paperformat_id) else 0, vat_report.print_report_name if vat_report else ''))
lines.append('  Paperformat: id=%s name=%r margins T/B/L/R=%s/%s/%s/%s header_spacing=%s dpi=%s' % (vat_paper.id if vat_paper else 0, vat_paper.name if vat_paper else '', vat_paper.margin_top if vat_paper else '', vat_paper.margin_bottom if vat_paper else '', vat_paper.margin_left if vat_paper else '', vat_paper.margin_right if vat_paper else '', vat_paper.header_spacing if vat_paper else '', vat_paper.dpi if vat_paper else ''))
lines.append('')
lines.append('L22 MARKER CHECK')
checks = [
    ('production report label', vat_report and vat_report.exists() and vat_report.name == 'VAT Invoices RI/DPI - 2026+'),
    ('down-payment reconciliation table', 'barani_down_payment_reconciliation' in vat_arch and 'Down payment reconciliation' in vat_arch),
    ('duplicate gross down-payment rows absent', 'Total Advances Received' not in vat_arch and 'Advance VAT reconciliation' not in vat_arch),
    ('Tel phone labels', 'Tel:' in vat_arch and 'barani_customer_phone' in vat_arch and 'barani_shipping_phone' in vat_arch),
    ('customer/shipping email labels', 'Email: ' in vat_arch and 'barani_customer_email' in vat_arch and 'barani_shipping_email' in vat_arch),
    ('invoice/SO note fallback', 'barani_sale_order_note_fallback' in vat_arch and 'barani_note_source_orders' in vat_arch and 'sale_line_ids.order_id' in vat_arch),
    ('address no-indent classes', 'barani_customer_cell' in vat_arch and 'barani_has_shipping' in vat_arch and 'barani_shipping_cell' in vat_arch),
    ('company registration aligned', 'name="company_registration"' in layout_arch and 'padding-left:18px' in layout_arch),
]
for chk in checks:
    lines.append('  %s: %s' % (chk[0], 'PASS' if chk[1] else 'WARNING/FAIL'))
lines.append('')

body = '\n'.join(lines) + '\n'
if WHICH in ('both', 'vat'):
    body = body + '\n============================================================\nBEGIN VAT_ARCH  (key=' + VAT_VIEW_KEY + ')\n============================================================\n'
    body = body + 'length=' + str(len(vat_arch)) + ' chars\n'
    body = body + vat_arch + '\n'
    body = body + '============================================================\nEND VAT_ARCH\n============================================================\n'
if WHICH in ('both', 'layout'):
    body = body + '\n============================================================\nBEGIN LAYOUT_ARCH  (key=' + LAYOUT_VIEW_KEY + ')\n============================================================\n'
    body = body + 'length=' + str(len(layout_arch)) + ' chars\n'
    body = body + layout_arch + '\n'
    body = body + '============================================================\nEND LAYOUT_ARCH\n============================================================\n'

full_len = len(body)
start = (PAGE - 1) * PAGE_SIZE
end = PAGE * PAGE_SIZE
more = 'YES' if end < full_len else 'NO'
page_text = body[start:end]
header = 'PAGE %s | chars %s-%s of %s | MORE REMAINS: %s\n' % (PAGE, start, min(end, full_len), full_len, more)
footer = '\n--- END PAGE %s | MORE REMAINS: %s ---' % (PAGE, more)
raise UserError((header + page_text + footer)[:90000])
