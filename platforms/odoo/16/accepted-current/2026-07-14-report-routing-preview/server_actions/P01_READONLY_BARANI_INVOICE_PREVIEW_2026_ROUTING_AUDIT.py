# ============================================================================
# ACTION NAME : P01 READ-ONLY — BARANI invoice Preview 2026+ routing audit
# MODEL       : Module (ir.module.module) recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
# PURPOSE     : Determine exactly what the Accounting invoice "Preview" button
#               calls in live Odoo and whether the current route is guaranteed
#               to render BARANI VAT Invoices RI/DPI - 2026+.
#
# IMPORTANT   : This action deliberately does NOT call preview_invoice() or
#               get_portal_url(), because those calls can create/ensure a portal
#               access token. It only inspects metadata, views, actions, and
#               existing records.
#
# SAFETY      : READ-ONLY:YES. No create/write/unlink/set_param/SQL writes.
# ============================================================================

PAGE = 1
PAGE_SIZE = 60000
MOVE_NAMES = ['2026232', '2026198', '2026200']

NL = chr(10)
lines = []
lines.append('P01 READ-ONLY — BARANI invoice Preview 2026+ routing audit')
lines.append('READ-ONLY:YES — metadata/search/read only; preview method is NOT executed. PAGE=%s PAGE_SIZE=%s' % (PAGE, PAGE_SIZE))
lines.append('Target: the existing Accounting Preview button must render the BARANI 2026+ RI/DPI/Credit Note format, not the standard portal invoice view.')
lines.append('')

problems = 0
warnings = 0

required_models = ['account.move', 'ir.ui.view', 'ir.actions.report', 'ir.actions.server', 'ir.model.data']
lines.append('MODEL PREFLIGHT')
for model_name in required_models:
    ok = model_name in env
    lines.append('  %s: %s' % (model_name, 'PASS' if ok else 'FAIL'))
    if not ok:
        problems = problems + 1
lines.append('')

if problems:
    full_text = NL.join(lines)
    start = (PAGE - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    more = end < len(full_text)
    raise UserError('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s%s%s' % (
        PAGE, start, min(end, len(full_text)), len(full_text), 'YES' if more else 'NO', NL, full_text[start:end]
    ))

Move = env['account.move'].sudo().with_context(active_test=False)
View = env['ir.ui.view'].sudo().with_context(active_test=False, lang=None)
Report = env['ir.actions.report'].sudo().with_context(active_test=False)
ServerAction = env['ir.actions.server'].sudo().with_context(active_test=False)
ModelData = env['ir.model.data'].sudo().with_context(active_test=False)

# Effective form view and exact Preview button snippet.
lines.append('EFFECTIVE ACCOUNT.MOVE FORM — PREVIEW BUTTON')
move_form_arch = ''
try:
    form_data = Move.get_view(view_type='form')
    move_form_arch = (form_data or {}).get('arch') or ''
    lines.append('  effective form arch: PASS len=%s' % len(move_form_arch))
except Exception as exc:
    lines.append('  effective form arch: FAIL %s' % str(exc)[:1000])
    problems = problems + 1

preview_markers = ['string="Preview"', "string='Preview'", 'name="preview_invoice"', "name='preview_invoice'"]
positions = []
for marker in preview_markers:
    pos = move_form_arch.find(marker)
    if pos != -1 and pos not in positions:
        positions.append(pos)
if not positions:
    lines.append('  Preview button marker: FAIL — not found in effective form')
    problems = problems + 1
else:
    positions.sort()
    for pos in positions[:5]:
        start = max(0, pos - 450)
        end = min(len(move_form_arch), pos + 850)
        snippet = move_form_arch[start:end].replace(NL, ' ')
        lines.append('  snippet=%r' % snippet)

standard_object_route = ('name="preview_invoice"' in move_form_arch or "name='preview_invoice'" in move_form_arch) and ('type="object"' in move_form_arch or "type='object'" in move_form_arch)
lines.append('  effective button still calls object method preview_invoice: %s' % ('YES' if standard_object_route else 'NO/NOT PROVEN'))
lines.append('')

# All form views that mention Preview/preview_invoice, to find Studio/module overrides.
lines.append('ACCOUNT.MOVE FORM VIEW SOURCES MENTIONING PREVIEW')
preview_views = View.search([
    ('model', '=', 'account.move'),
    ('type', 'in', ('form', 'qweb')),
    '|', ('arch_db', 'ilike', 'preview_invoice'), ('arch_db', 'ilike', '>Preview<'),
], order='priority asc, id asc', limit=200)
if not preview_views:
    lines.append('  NONE')
for vw in preview_views:
    arch = vw.arch_db or ''
    pos = arch.find('preview_invoice')
    if pos == -1:
        pos = arch.find('Preview')
    start = max(0, pos - 350) if pos != -1 else 0
    end = min(len(arch), pos + 700) if pos != -1 else min(len(arch), 700)
    snippet = arch[start:end].replace(NL, ' ')
    lines.append('  id=%s key=%r name=%r active=%s inherit_id=%s priority=%s write_date=%s snippet=%r' % (
        vw.id, vw.key or '', vw.name or '', vw.active, vw.inherit_id.id if vw.inherit_id else 0,
        vw.priority, vw.write_date, snippet
    ))
lines.append('')

# Custom 2026+ report action and any HTML sibling action.
lines.append('BARANI 2026+ REPORT ACTIONS')
barani_reports = Report.search([
    '|', ('report_name', '=', 'barani_vat.report_invoice_document_vat'),
         ('name', 'ilike', 'VAT Invoices RI/DPI'),
], order='id asc')
if not barani_reports:
    lines.append('  FAIL — no BARANI VAT RI/DPI report action found')
    problems = problems + 1
for rr in barani_reports:
    xmlids = []
    md_rows = ModelData.search([('model', '=', 'ir.actions.report'), ('res_id', '=', rr.id)])
    for md in md_rows:
        xmlids.append('%s.%s' % (md.module, md.name))
    lines.append('  id=%s name=%r model=%s report_name=%s report_type=%s binding_model=%s paper=%r xmlids=%s' % (
        rr.id, rr.name or '', rr.model or '', rr.report_name or '', rr.report_type or '',
        rr.binding_model_id.model if rr.binding_model_id else '',
        rr.paperformat_id.name if rr.paperformat_id else '',
        ','.join(xmlids) if xmlids else 'NONE'
    ))

barani_html_reports = Report.search([
    ('model', '=', 'account.move'),
    ('report_name', '=', 'barani_vat.report_invoice_document_vat'),
    ('report_type', '=', 'qweb-html'),
], order='id asc')
lines.append('  qweb-html action using BARANI 2026+ report_name: %s' % (
    ', '.join([str(x.id) for x in barani_html_reports]) if barani_html_reports else 'NONE'
))
lines.append('')

# Current live BARANI view marker check.
lines.append('LIVE BARANI 2026+ QWEB MARKERS')
vat_views = View.search([('type', '=', 'qweb'), ('key', '=', 'barani_vat.report_invoice_document_vat')])
vat_arch = ''
if len(vat_views) == 1:
    vat_arch = vat_views.arch_db or ''
    lines.append('  body id=%s len=%s write_date=%s: PASS' % (vat_views.id, len(vat_arch), vat_views.write_date))
else:
    lines.append('  body count=%s expected=1: FAIL' % len(vat_views))
    problems = problems + 1
marker_checks = [
    ('Preferred Payment Method', 'Preferred Payment Method' in vat_arch),
    ('DD MON YYYY date helper', 'barani_month_abbr_en' in vat_arch),
    ('numeric PDF payment reference', 'barani_pdf_payment_ref' in vat_arch),
    ('HS Code column', 'HS Code' in vat_arch),
    ('COO column', 'COO' in vat_arch),
    ('VAT Rate column', 'VAT Rate' in vat_arch),
    ('credit Original Invoice', 'Original Invoice' in vat_arch),
    ('credit Original Payment Reference', 'Original Payment Reference' in vat_arch),
]
for label, ok in marker_checks:
    lines.append('  %s: %s' % (label, 'PASS' if ok else 'FAIL'))
    if not ok:
        problems = problems + 1
lines.append('')

# Portal invoice templates and whether they explicitly call/reference the BARANI report.
lines.append('PORTAL INVOICE QWEB DISCOVERY')
portal_views = View.search([
    ('type', '=', 'qweb'),
    '|', '|',
    ('key', 'ilike', 'portal_invoice'),
    ('name', 'ilike', 'portal invoice'),
    ('arch_db', 'ilike', 'portal_invoice'),
], order='id asc', limit=200)
portal_refs_barani = []
portal_refs_standard_invoice = []
if not portal_views:
    lines.append('  NONE found')
for vw in portal_views:
    arch = vw.arch_db or ''
    has_barani = 'barani_vat.report_invoice_document_vat' in arch or 'barani_vat' in arch
    has_standard = 'account.report_invoice' in arch or 'account.report_invoice_document' in arch
    if has_barani:
        portal_refs_barani.append(vw.id)
    if has_standard:
        portal_refs_standard_invoice.append(vw.id)
    lines.append('  id=%s key=%r name=%r active=%s inherit_id=%s has_BARANI=%s has_standard_invoice=%s len=%s' % (
        vw.id, vw.key or '', vw.name or '', vw.active, vw.inherit_id.id if vw.inherit_id else 0,
        'YES' if has_barani else 'NO', 'YES' if has_standard else 'NO', len(arch)
    ))
lines.append('  portal views explicitly referencing BARANI 2026+ report: %s' % (
    ','.join([str(x) for x in portal_refs_barani]) if portal_refs_barani else 'NONE'
))
lines.append('  portal views explicitly referencing standard invoice report: %s' % (
    ','.join([str(x) for x in portal_refs_standard_invoice]) if portal_refs_standard_invoice else 'NONE'
))
lines.append('')

# Server actions or report actions that may already reroute Preview.
lines.append('PREVIEW-RELATED SERVER ACTIONS')
preview_server_actions = ServerAction.search([
    '|', '|',
    ('name', 'ilike', 'preview'),
    ('code', 'ilike', 'preview_invoice'),
    ('code', 'ilike', 'barani_vat.report_invoice_document_vat'),
], order='id asc', limit=200)
if not preview_server_actions:
    lines.append('  NONE')
for sa in preview_server_actions:
    code = sa.code or ''
    snippet = code[:1200].replace(NL, ' ')
    lines.append('  id=%s name=%r state=%s model=%s binding_model=%s active=%s snippet=%r' % (
        sa.id, sa.name or '', sa.state or '', sa.model_id.model if sa.model_id else '',
        sa.binding_model_id.model if sa.binding_model_id else '',
        sa.active if 'active' in sa._fields else 'n/a', snippet
    ))
lines.append('')

# Exact test records. Do not call preview/get_portal_url.
lines.append('PREVIEW TEST RECORDS — METHOD NOT CALLED')
moves = Move.search([('name', 'in', MOVE_NAMES)], order='name asc')
found_names = []
for mv in moves:
    found_names.append(mv.name or '/')
    access_url_value = ''
    if 'access_url' in mv._fields:
        access_url_value = mv.access_url or ''
    lines.append('  id=%s name=%s type=%s state=%s origin=%r payment_state=%s access_url_existing=%r' % (
        mv.id, mv.name or '/', mv.move_type or '', mv.state or '', mv.invoice_origin or '',
        mv.payment_state or '', access_url_value
    ))
for requested_name in MOVE_NAMES:
    if requested_name not in found_names:
        lines.append('  WARN: requested test move %s not found' % requested_name)
        warnings = warnings + 1
lines.append('')

# Decision gate.
lines.append('DECISION GATE')
if standard_object_route and not portal_refs_barani:
    lines.append('  NOT GUARANTEED / LIKELY FAIL: the effective button still calls preview_invoice, while no inspected portal invoice view explicitly references the BARANI 2026+ report.')
    lines.append('  Printing from the custom qweb-pdf action does not by itself prove that Preview renders the same template.')
elif barani_html_reports:
    lines.append('  A BARANI qweb-html report action exists. Verify whether the effective Preview button/action actually routes to it.')
elif portal_refs_barani:
    lines.append('  A portal invoice view references BARANI 2026+ markers. Inspect the exact inheritance and render path before declaring PASS.')
else:
    lines.append('  Routing is inconclusive from metadata. Review the full output and perform a manual preview of 2026232 before designing a patch.')
lines.append('  Required final behavior: the existing visible Preview button must render barani_vat.report_invoice_document_vat in HTML/preview form for RI, DPI, and Credit Note without changing Print, accounting, totals, or portal access security.')
lines.append('  No write-capable action is authorized by this audit.')
lines.append('')
lines.append('SUMMARY problems=%s warnings=%s writes_performed=0' % (problems, warnings))

full_text = NL.join(lines)
start = (PAGE - 1) * PAGE_SIZE
end = start + PAGE_SIZE
chunk = full_text[start:end]
more = end < len(full_text)
header = 'PAGE %s | chars %s-%s of %s | MORE REMAINS: %s' % (
    PAGE, start, min(end, len(full_text)), len(full_text), 'YES' if more else 'NO'
)
footer = '--- END PAGE %s | MORE REMAINS: %s ---' % (PAGE, 'YES' if more else 'NO')
raise UserError(header + NL + chunk + NL + footer)
