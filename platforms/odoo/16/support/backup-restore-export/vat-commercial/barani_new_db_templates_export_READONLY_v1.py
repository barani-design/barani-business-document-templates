# ============================================================================
# ACTION NAME : READ-ONLY: BARANI new-DB report template export v1
# MODEL       : Module (ir.module.module) or any model; selected records ignored.
# ACTION TO DO: Execute Python Code
# PURPOSE     : Export the CURRENT installed BARANI report templates after a new-DB
#               install. Dumps both isolated families:
#                 - VAT RI/DPI/Credit Note report views/layout/report/paper
#                 - Commercial Q/SO/PF report views/layout/wrappers/reports/paper
# READ-ONLY   : YES. No create/write/unlink/set_param/commit/SQL. Uses ORM reads
#               only and raises UserError as the output channel.
# PAGING      : Set PAGE = 1,2,3... until MORE REMAINS: NO.
# SAFE_EVAL   : no import/def/lambda/comprehension/with/getattr/hasattr/setattr/
#               eval/exec/open/dir/isinstance in executable code.
# ============================================================================

PAGE = 1
PAGE_SIZE = 30000
WHICH = 'all'  # all | vat | commercial

VatIdsKey = 'barani.vat_report.ids'
ComIdsKey = 'barani.commercial_report.ids'

VAT_VIEW_KEY = 'barani_vat.report_invoice_document_vat'
VAT_LAYOUT_KEY = 'barani_vat.external_layout_standard_titled'
VAT_REPORT_KEY = 'barani_vat.report_invoice_document_vat'
VAT_PAPER_NAME = 'BARANI VAT A4 7mm'

COM_LAYOUT_KEY = 'barani_commercial.external_layout_standard_titled'
COM_BODY_KEY = 'barani_commercial.report_saleorder_document'
COM_SALE_WRAPPER_KEY = 'barani_commercial.report_saleorder'
COM_PF_WRAPPER_KEY = 'barani_commercial.report_saleorder_proforma'
COM_SALE_REPORT_KEY = COM_SALE_WRAPPER_KEY
COM_PF_REPORT_KEY = COM_PF_WRAPPER_KEY
COM_PAPER_NAME = 'BARANI Commercial A4 7mm'

View = env['ir.ui.view'].sudo()
Report = env['ir.actions.report'].sudo()
Paper = env['report.paperformat'].sudo()
Param = env['ir.config_parameter'].sudo()

lines = []
lines.append('READ-ONLY: BARANI new-DB report template export v1')
lines.append('READ-ONLY:YES — no create/write/unlink/set_param/commit/SQL. WHICH=%s PAGE=%s PAGE_SIZE=%s' % (WHICH, PAGE, PAGE_SIZE))
lines.append('')

if WHICH not in ('all', 'vat', 'commercial'):
    raise UserError('WHICH must be all, vat, or commercial')

# VAT artifacts
if WHICH in ('all', 'vat'):
    lines.append('============================================================')
    lines.append('VAT RI/DPI/CREDIT NOTE FAMILY')
    lines.append('============================================================')
    vat_ids_text = Param.get_param(VatIdsKey, '') or ''
    lines.append('stored ids %s = %r' % (VatIdsKey, vat_ids_text))
    vat_view_id = 0
    vat_report_id = 0
    vat_paper_id = 0
    vat_layout_id = 0
    if vat_ids_text:
        parts = vat_ids_text.split(',')
        if len(parts) >= 1:
            try:
                vat_view_id = int(parts[0] or '0')
            except Exception:
                vat_view_id = 0
        if len(parts) >= 2:
            try:
                vat_report_id = int(parts[1] or '0')
            except Exception:
                vat_report_id = 0
        if len(parts) >= 3:
            try:
                vat_paper_id = int(parts[2] or '0')
            except Exception:
                vat_paper_id = 0
        if len(parts) >= 4:
            try:
                vat_layout_id = int(parts[3] or '0')
            except Exception:
                vat_layout_id = 0
    vat_view = View.browse(vat_view_id)
    if not vat_view.exists():
        vat_view = View.search([('key', '=', VAT_VIEW_KEY)], limit=1)
    vat_layout = View.browse(vat_layout_id)
    if not vat_layout.exists():
        vat_layout = View.search([('key', '=', VAT_LAYOUT_KEY)], limit=1)
    vat_report = Report.browse(vat_report_id)
    if not vat_report.exists():
        vat_report = Report.search([('report_name', '=', VAT_REPORT_KEY)], limit=1)
    vat_paper = Paper.browse(vat_paper_id)
    if not vat_paper.exists():
        vat_paper = Paper.search([('name', '=', VAT_PAPER_NAME)], limit=1)
    if not vat_view or vat_view.key != VAT_VIEW_KEY or not vat_layout or vat_layout.key != VAT_LAYOUT_KEY or not vat_report or vat_report.report_name != VAT_REPORT_KEY:
        lines.append('ERROR: VAT artifact identity check failed. Refusing to dump ambiguous data.')
        raise UserError('\n'.join(lines)[:90000])
    lines.append('VAT view id=%s key=%s name=%r write_date=%s' % (vat_view.id, vat_view.key, vat_view.name, vat_view.write_date))
    lines.append('VAT layout id=%s key=%s name=%r write_date=%s' % (vat_layout.id, vat_layout.key, vat_layout.name, vat_layout.write_date))
    lines.append('VAT report id=%s name=%r model=%s report_name=%s print_report_name=%r' % (vat_report.id, vat_report.name, vat_report.model, vat_report.report_name, vat_report.print_report_name))
    if vat_paper:
        lines.append('VAT paper id=%s name=%r margins T/B/L/R=%s/%s/%s/%s header_spacing=%s dpi=%s' % (vat_paper.id, vat_paper.name, vat_paper.margin_top, vat_paper.margin_bottom, vat_paper.margin_left, vat_paper.margin_right, vat_paper.header_spacing, vat_paper.dpi))
    lines.append('')
    lines.append('----- BEGIN VAT_VIEW_ARCH -----')
    lines.append(vat_view.arch_db or '')
    lines.append('----- END VAT_VIEW_ARCH -----')
    lines.append('')
    lines.append('----- BEGIN VAT_LAYOUT_ARCH -----')
    lines.append(vat_layout.arch_db or '')
    lines.append('----- END VAT_LAYOUT_ARCH -----')
    lines.append('')

# Commercial artifacts
if WHICH in ('all', 'commercial'):
    lines.append('============================================================')
    lines.append('COMMERCIAL Q/SO/PF FAMILY')
    lines.append('============================================================')
    com_ids_text = Param.get_param(ComIdsKey, '') or ''
    lines.append('stored ids %s = %r' % (ComIdsKey, com_ids_text))
    body_id = 0
    sale_report_id = 0
    pf_report_id = 0
    paper_id = 0
    layout_id = 0
    sale_wrapper_id = 0
    pf_wrapper_id = 0
    if com_ids_text:
        parts = com_ids_text.split(',')
        if len(parts) >= 1:
            try:
                body_id = int(parts[0] or '0')
            except Exception:
                body_id = 0
        if len(parts) >= 2:
            try:
                sale_report_id = int(parts[1] or '0')
            except Exception:
                sale_report_id = 0
        if len(parts) >= 3:
            try:
                pf_report_id = int(parts[2] or '0')
            except Exception:
                pf_report_id = 0
        if len(parts) >= 4:
            try:
                paper_id = int(parts[3] or '0')
            except Exception:
                paper_id = 0
        if len(parts) >= 5:
            try:
                layout_id = int(parts[4] or '0')
            except Exception:
                layout_id = 0
        if len(parts) >= 6:
            try:
                sale_wrapper_id = int(parts[5] or '0')
            except Exception:
                sale_wrapper_id = 0
        if len(parts) >= 7:
            try:
                pf_wrapper_id = int(parts[6] or '0')
            except Exception:
                pf_wrapper_id = 0
    com_layout = View.browse(layout_id)
    if not com_layout.exists():
        com_layout = View.search([('key', '=', COM_LAYOUT_KEY)], limit=1)
    com_body = View.browse(body_id)
    if not com_body.exists():
        com_body = View.search([('key', '=', COM_BODY_KEY)], limit=1)
    sale_wrapper = View.browse(sale_wrapper_id)
    if not sale_wrapper.exists():
        sale_wrapper = View.search([('key', '=', COM_SALE_WRAPPER_KEY)], limit=1)
    pf_wrapper = View.browse(pf_wrapper_id)
    if not pf_wrapper.exists():
        pf_wrapper = View.search([('key', '=', COM_PF_WRAPPER_KEY)], limit=1)
    sale_report = Report.browse(sale_report_id)
    if not sale_report.exists():
        sale_report = Report.search([('report_name', '=', COM_SALE_REPORT_KEY)], limit=1)
    pf_report = Report.browse(pf_report_id)
    if not pf_report.exists():
        pf_report = Report.search([('report_name', '=', COM_PF_REPORT_KEY)], limit=1)
    com_paper = Paper.browse(paper_id)
    if not com_paper.exists():
        com_paper = Paper.search([('name', '=', COM_PAPER_NAME)], limit=1)
    if not com_layout or com_layout.key != COM_LAYOUT_KEY or not com_body or com_body.key != COM_BODY_KEY or not sale_wrapper or sale_wrapper.key != COM_SALE_WRAPPER_KEY or not pf_wrapper or pf_wrapper.key != COM_PF_WRAPPER_KEY or not sale_report or sale_report.report_name != COM_SALE_REPORT_KEY or not pf_report or pf_report.report_name != COM_PF_REPORT_KEY:
        lines.append('ERROR: Commercial artifact identity check failed. Refusing to dump ambiguous data.')
        raise UserError('\n'.join(lines)[:90000])
    lines.append('Commercial layout id=%s key=%s name=%r write_date=%s' % (com_layout.id, com_layout.key, com_layout.name, com_layout.write_date))
    lines.append('Commercial body id=%s key=%s name=%r write_date=%s' % (com_body.id, com_body.key, com_body.name, com_body.write_date))
    lines.append('Commercial sale wrapper id=%s key=%s name=%r' % (sale_wrapper.id, sale_wrapper.key, sale_wrapper.name))
    lines.append('Commercial PF wrapper id=%s key=%s name=%r' % (pf_wrapper.id, pf_wrapper.key, pf_wrapper.name))
    lines.append('Commercial sale report id=%s name=%r report_name=%s print_report_name=%r' % (sale_report.id, sale_report.name, sale_report.report_name, sale_report.print_report_name))
    lines.append('Commercial PF report id=%s name=%r report_name=%s print_report_name=%r' % (pf_report.id, pf_report.name, pf_report.report_name, pf_report.print_report_name))
    if com_paper:
        lines.append('Commercial paper id=%s name=%r margins T/B/L/R=%s/%s/%s/%s header_spacing=%s dpi=%s' % (com_paper.id, com_paper.name, com_paper.margin_top, com_paper.margin_bottom, com_paper.margin_left, com_paper.margin_right, com_paper.header_spacing, com_paper.dpi))
    lines.append('')
    lines.append('----- BEGIN COMMERCIAL_LAYOUT_ARCH -----')
    lines.append(com_layout.arch_db or '')
    lines.append('----- END COMMERCIAL_LAYOUT_ARCH -----')
    lines.append('')
    lines.append('----- BEGIN COMMERCIAL_BODY_ARCH -----')
    lines.append(com_body.arch_db or '')
    lines.append('----- END COMMERCIAL_BODY_ARCH -----')
    lines.append('')
    lines.append('----- BEGIN COMMERCIAL_SALE_WRAPPER_ARCH -----')
    lines.append(sale_wrapper.arch_db or '')
    lines.append('----- END COMMERCIAL_SALE_WRAPPER_ARCH -----')
    lines.append('')
    lines.append('----- BEGIN COMMERCIAL_PF_WRAPPER_ARCH -----')
    lines.append(pf_wrapper.arch_db or '')
    lines.append('----- END COMMERCIAL_PF_WRAPPER_ARCH -----')

text = '\n'.join(lines)
start = (PAGE - 1) * PAGE_SIZE
end = start + PAGE_SIZE
chunk = text[start:end]
more = 'YES' if end < len(text) else 'NO'
raise UserError('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s\n%s' % (PAGE, start, min(end, len(text)), len(text), more, chunk))
