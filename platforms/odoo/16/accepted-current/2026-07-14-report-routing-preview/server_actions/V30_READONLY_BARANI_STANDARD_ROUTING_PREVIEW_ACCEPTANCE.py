# ============================================================================
# ACTION NAME : V30 READ-ONLY — BARANI standard routing + Preview acceptance
# MODEL       : Module (ir.module.module) recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
# PURPOSE     : Verify Phase A routing before any duplicate action is hidden:
#               - standard Odoo report XMLIDs route to BARANI;
#               - custom "— 2026+" actions remain visible as fallback;
#               - Preview button routes to the hidden BARANI qweb-html action;
#               - relevant email templates/report references are inventoried.
#
# SAFETY      : READ-ONLY:YES. No writes and no Preview execution.
# ============================================================================

PAGE = 1
PAGE_SIZE = 60000
NL = chr(10)

C10_MARKER = 'barani.report_routing_preview.c10.standard_relink.marker'
C20_MARKER = 'barani.report_routing_preview.c20.preview_html.marker'
BARANI_VAT_REPORT_NAME = 'barani_vat.report_invoice_document_vat'

Param = env['ir.config_parameter'].sudo()
Report = env['ir.actions.report'].sudo().with_context(active_test=False)
View = env['ir.ui.view'].sudo().with_context(active_test=False, lang=None)
Move = env['account.move'].sudo()

lines = []
lines.append('V30 READ-ONLY — BARANI standard routing + Preview acceptance')
lines.append('READ-ONLY:YES — no report, view, email or business record writes. PAGE=%s' % PAGE)
lines.append('')

problems = 0
warnings = 0

lines.append('PHASE MARKERS')
for key in [C10_MARKER, C20_MARKER]:
    ok = (Param.get_param(key) or '') == '1'
    lines.append('  %s: %s' % (key, 'PASS' if ok else 'FAIL'))
    if not ok:
        problems = problems + 1
lines.append('')

checks = [
    ('sale.action_report_saleorder', 'barani_commercial.report_saleorder'),
    ('sale.action_report_pro_forma_invoice', 'barani_commercial.report_saleorder_proforma'),
    ('account.account_invoices', 'barani_vat.report_invoice_document_vat'),
]
without_mode = Param.get_param(C10_MARKER + '.without_payment_mode') or ''
without_target = Param.get_param(C10_MARKER + '.without_payment_report_name') or ''
checks.append(('account.account_invoices_without_payment', without_target))

lines.append('STANDARD ACTION ROUTING')
for item in checks:
    xmlid = item[0]
    expected = item[1]
    rr = env.ref(xmlid, raise_if_not_found=False)
    if not rr or rr._name != 'ir.actions.report':
        lines.append('  %s: FAIL — missing' % xmlid)
        problems = problems + 1
    else:
        ok = bool(expected) and rr.report_name == expected and rr.report_type == 'qweb-pdf' and rr.paperformat_id
        lines.append('  %s id=%s name=%r report_name=%s expected=%s paper=%r bound=%s: %s' % (
            xmlid, rr.id, rr.name or '', rr.report_name or '', expected,
            rr.paperformat_id.name if rr.paperformat_id else '',
            rr.binding_model_id.model if rr.binding_model_id else '',
            'PASS' if ok else 'FAIL'
        ))
        if not ok:
            problems = problems + 1
lines.append('  without-payment mode=%s' % without_mode)
lines.append('')

standard_ids = []
for xmlid in [
    'sale.action_report_saleorder',
    'sale.action_report_pro_forma_invoice',
    'account.account_invoices',
    'account.account_invoices_without_payment',
]:
    std = env.ref(xmlid, raise_if_not_found=False)
    if std:
        standard_ids.append(std.id)

lines.append('CUSTOM FALLBACK ACTIONS — MUST STILL BE VISIBLE BEFORE C30')
fallback_specs = [
    ('sale.order', 'barani_commercial.report_saleorder'),
    ('sale.order', 'barani_commercial.report_saleorder_proforma'),
    ('account.move', 'barani_vat.report_invoice_document_vat'),
]
for spec in fallback_specs:
    rs = Report.search([
        ('model', '=', spec[0]),
        ('report_name', '=', spec[1]),
        ('report_type', '=', 'qweb-pdf'),
    ], order='id asc')
    visible_ids = ''
    visible_count = 0
    for rr in rs:
        if rr.id not in standard_ids and rr.binding_model_id and rr.binding_model_id.model == rr.model and rr.binding_type == 'report':
            if visible_ids:
                visible_ids = visible_ids + ','
            visible_ids = visible_ids + str(rr.id)
            visible_count = visible_count + 1
    lines.append('  model=%s report_name=%s visible_custom_count=%s ids=%s' % (
        spec[0], spec[1], visible_count, visible_ids or 'NONE'
    ))
    if visible_count == 0:
        lines.append('    WARN: no visible custom fallback remains; verify whether another chat already hid it.')
        warnings = warnings + 1
lines.append('')

lines.append('PREVIEW ROUTING')
html_id = int(Param.get_param(C20_MARKER + '.report_action_id') or '0')
view_id = int(Param.get_param(C20_MARKER + '.view_id') or '0')
html_action = Report.browse(html_id) if html_id else Report.browse()
preview_view = View.browse(view_id) if view_id else View.browse()
if not html_action.exists():
    lines.append('  hidden qweb-html action: FAIL id=%s missing' % html_id)
    problems = problems + 1
else:
    ok = html_action.report_type == 'qweb-html' and html_action.report_name == BARANI_VAT_REPORT_NAME and not html_action.binding_model_id
    lines.append('  hidden action id=%s name=%r report_type=%s report_name=%s bound=%s: %s' % (
        html_action.id, html_action.name or '', html_action.report_type or '',
        html_action.report_name or '',
        html_action.binding_model_id.model if html_action.binding_model_id else '',
        'PASS' if ok else 'FAIL'
    ))
    if not ok:
        problems = problems + 1

if not preview_view.exists():
    lines.append('  inherited Preview view: FAIL id=%s missing' % view_id)
    problems = problems + 1
else:
    lines.append('  inherited view id=%s name=%r key=%r active=%s priority=%s' % (
        preview_view.id, preview_view.name or '', preview_view.key or '',
        preview_view.active, preview_view.priority
    ))

effective_arch = ''
try:
    effective_arch = (Move.get_view(view_type='form') or {}).get('arch') or ''
except Exception as exc:
    lines.append('  effective form read: FAIL %s' % str(exc)[:500])
    problems = problems + 1

marker1 = 'name="%s"' % html_id
marker2 = "name='%s'" % html_id
pos = effective_arch.find(marker1)
if pos == -1:
    pos = effective_arch.find(marker2)
snippet = effective_arch[max(0, pos - 350):min(len(effective_arch), pos + 800)] if pos != -1 else ''
preview_ok = pos != -1 and ('type="action"' in snippet or "type='action'" in snippet)
lines.append('  effective Preview button action-id/type check: %s' % ('PASS' if preview_ok else 'FAIL'))
lines.append('  snippet=%r' % snippet.replace(NL, ' '))
if not preview_ok:
    problems = problems + 1
lines.append('')

lines.append('MAIL TEMPLATE REPORT REFERENCES')
if 'mail.template' not in env:
    lines.append('  WARN: mail.template unavailable.')
    warnings = warnings + 1
else:
    Template = env['mail.template'].sudo().with_context(active_test=False)
    templates = Template.search([('model', 'in', ('sale.order', 'account.move'))], order='model,id', limit=250)
    report_fields = []
    if 'report_template' in Template._fields:
        report_fields.append('report_template')
    if 'report_template_ids' in Template._fields:
        report_fields.append('report_template_ids')
    lines.append('  dynamic report fields=%s' % (','.join(report_fields) if report_fields else 'NONE'))
    for tmpl in templates:
        refs = []
        if 'report_template' in report_fields and tmpl.report_template:
            refs.append(tmpl.report_template)
        if 'report_template_ids' in report_fields:
            for rr in tmpl.report_template_ids:
                refs.append(rr)
        if refs:
            ref_text = ''
            non_barani = False
            for rr in refs:
                if ref_text:
                    ref_text = ref_text + '; '
                ref_text = ref_text + '%s:%s:%s' % (rr.id, rr.name or '', rr.report_name or '')
                if rr.model in ('sale.order', 'account.move') and not (rr.report_name or '').startswith('barani_'):
                    non_barani = True
            lines.append('  id=%s model=%s name=%r refs=%s result=%s' % (
                tmpl.id, tmpl.model or '', tmpl.name or '',
                ref_text,
                'REVIEW' if non_barani else 'BARANI/ALIGNED'
            ))
            if non_barani:
                warnings = warnings + 1
lines.append('')

lines.append('MANUAL ACCEPTANCE GATE — REQUIRED BEFORE C30')
lines.append('  [ ] Standard Quotation / Order prints BARANI Q/SO PDF')
lines.append('  [ ] Standard PRO-FORMA Invoice prints BARANI PF PDF')
lines.append('  [ ] Standard Invoices prints BARANI RI/DPI/Credit Note PDF')
lines.append('  [ ] Invoices without Payment follows the approved audited BARANI route')
lines.append('  [ ] Send by Email / Send Pro-Forma Invoice attachments are BARANI')
lines.append('  [ ] Send & Print invoice and credit-note attachments are BARANI')
lines.append('  [ ] Preview on RI 2026232 renders BARANI HTML')
lines.append('  [ ] Preview on DPI 2026198 renders BARANI HTML')
lines.append('  [ ] Preview on Credit Note 2026200 renders BARANI HTML')
lines.append('  [ ] B10 restore was reviewed as a valid rollback')
lines.append('')
lines.append('SUMMARY problems=%s warnings=%s writes_performed=0' % (problems, warnings))
lines.append('No duplicate action may be hidden until every manual box above passes.')

full = NL.join(lines)
start = (PAGE - 1) * PAGE_SIZE
end = start + PAGE_SIZE
more = 'YES' if end < len(full) else 'NO'
raise UserError(('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s%s%s' % (
    PAGE, start, min(end, len(full)), len(full), more, NL, full[start:end]
))[:90000])
