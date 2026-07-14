# ============================================================================
# ACTION NAME : V40 READ-ONLY — BARANI final routing + Preview state audit
# MODEL       : Module (ir.module.module) recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
#
# PURPOSE     : Final, post-migration verification after C10/C20/C30/C31/C32.
#
# VERIFIES:
#   - standard Odoo action XML IDs still route to BARANI;
#   - only intended Print actions remain visible;
#   - hidden duplicate actions are retained but unbound;
#   - Delivery Note is visible and renamed;
#   - Preview uses hidden BARANI qweb-html action and breadcrumb name;
#   - former Odoo-linked QWeb wrappers have Archived — display names only;
#   - QWeb keys and bytes still match B10;
#   - mail templates still reference the standard BARANI-routed actions.
#
# SAFETY      : READ-ONLY:YES. No writes.
# ============================================================================

PAGE = 1
PAGE_SIZE = 60000
NL = chr(10)

SNAPSHOT_CODE = 'pre_standard_relink_preview_2026_07_14'
PREFIX = 'barani.report_routing_preview.restore.' + SNAPSHOT_CODE

C10_MARKER = 'barani.report_routing_preview.c10.standard_relink.marker'
C20_MARKER = 'barani.report_routing_preview.c20.preview_html.marker'
C30_MARKER = 'barani.report_routing_preview.c30.hide_duplicates.marker'
C31_MARKER = 'barani.report_routing_preview.c31.archive_old_views.marker'
C32_MARKER = 'barani.report_routing_preview.c32.preview_action_rename.marker'

BARANI_QSO = 'barani_commercial.report_saleorder'
BARANI_PF = 'barani_commercial.report_saleorder_proforma'
BARANI_VAT = 'barani_vat.report_invoice_document_vat'
BARANI_DN = 'barani_delivery.report_sale_order_delivery_note_2026'

Param = env['ir.config_parameter'].sudo()
Report = env['ir.actions.report'].sudo().with_context(active_test=False)
View = env['ir.ui.view'].sudo().with_context(active_test=False, lang=None)
Move = env['account.move'].sudo()

lines = []
lines.append('V40 READ-ONLY — BARANI final routing + Preview state audit')
lines.append('READ-ONLY:YES — no report, view, email or business record writes. PAGE=%s' % PAGE)
lines.append('')

problems = 0
warnings = 0

lines.append('PHASE MARKERS')
for key in [C10_MARKER, C20_MARKER, C30_MARKER, C31_MARKER, C32_MARKER]:
    ok = (Param.get_param(key) or '') == '1'
    lines.append('  %s: %s' % (key, 'PASS' if ok else 'FAIL'))
    if not ok:
        problems = problems + 1
lines.append('')

standard_checks = [
    ('sale.action_report_saleorder', BARANI_QSO, 'sale.order', True, 'BARANI Commercial A4 7mm'),
    ('sale.action_report_pro_forma_invoice', BARANI_PF, 'sale.order', True, 'BARANI Commercial A4 7mm'),
    ('account.account_invoices', BARANI_VAT, 'account.move', True, 'BARANI VAT A4 7mm'),
    ('account.account_invoices_without_payment', BARANI_VAT, 'account.move', False, 'BARANI VAT A4 7mm'),
]

lines.append('STANDARD ACTION ROUTING AND BINDINGS')
standard_ids = []
for item in standard_checks:
    xmlid = item[0]
    expected_report = item[1]
    expected_model = item[2]
    should_be_bound = item[3]
    expected_paper = item[4]
    rr = env.ref(xmlid, raise_if_not_found=False)
    if not rr or rr._name != 'ir.actions.report':
        lines.append('  %s: FAIL — missing' % xmlid)
        problems = problems + 1
    else:
        standard_ids.append(rr.id)
        bound = bool(rr.binding_model_id and rr.binding_type == 'report')
        paper_name = rr.paperformat_id.name if rr.paperformat_id else ''
        ok = (
            rr.report_name == expected_report
            and rr.report_file == expected_report
            and rr.model == expected_model
            and rr.report_type == 'qweb-pdf'
            and bound == should_be_bound
            and paper_name == expected_paper
        )
        lines.append(
            '  %s id=%s name=%r report_name=%s paper=%r bound=%s expected_bound=%s: %s'
            % (
                xmlid, rr.id, rr.name or '', rr.report_name or '',
                paper_name, bound, should_be_bound, 'PASS' if ok else 'FAIL'
            )
        )
        if not ok:
            problems = problems + 1
lines.append('')

lines.append('HIDDEN CUSTOM ACTIONS RETAINED')
custom_specs = [
    ('sale.order', BARANI_QSO, 964, 'Quotation / Order — 2026+'),
    ('sale.order', BARANI_PF, 965, 'PRO-FORMA — 2026+'),
    ('account.move', BARANI_VAT, 918, 'VAT Invoices RI/DPI - 2026+'),
]
for item in custom_specs:
    model_name = item[0]
    report_name = item[1]
    expected_id = item[2]
    expected_name = item[3]
    rr = Report.browse(expected_id)
    exists = bool(rr.exists())
    bound = bool(rr.binding_model_id) if exists else False
    ok = (
        exists
        and rr.model == model_name
        and rr.report_name == report_name
        and rr.name == expected_name
        and not bound
    )
    lines.append(
        '  id=%s exists=%s name=%r report_name=%s bound=%s: %s'
        % (
            expected_id, exists, rr.name if exists else '',
            rr.report_name if exists else '', bound, 'PASS' if ok else 'FAIL'
        )
    )
    if not ok:
        problems = problems + 1
lines.append('')

lines.append('DELIVERY NOTE ACTION')
dn_rs = Report.search([
    ('model', '=', 'sale.order'),
    ('report_name', '=', BARANI_DN),
    ('report_type', '=', 'qweb-pdf'),
], order='id asc')
if len(dn_rs) != 1:
    lines.append('  FAIL: expected exactly one BARANI Delivery Note action; found=%s' % len(dn_rs))
    problems = problems + 1
else:
    dn = dn_rs[0]
    dn_bound = bool(dn.binding_model_id and dn.binding_model_id.model == 'sale.order' and dn.binding_type == 'report')
    dn_ok = dn.name == 'Delivery Note' and dn_bound
    lines.append(
        '  id=%s name=%r paper=%r bound=%s: %s'
        % (
            dn.id, dn.name or '',
            dn.paperformat_id.name if dn.paperformat_id else '',
            dn_bound, 'PASS' if dn_ok else 'FAIL'
        )
    )
    if not dn_ok:
        problems = problems + 1
lines.append('')

lines.append('FINAL FORM PRINT ACTIONS')
sale_visible = Report.search([
    ('model', '=', 'sale.order'),
    ('binding_model_id.model', '=', 'sale.order'),
    ('binding_type', '=', 'report'),
], order='id asc')
sale_form_names = []
for rr in sale_visible:
    views = rr.binding_view_types or ''
    if not views or 'form' in views.split(','):
        sale_form_names.append(rr.name or '')
        lines.append('  sale.order id=%s name=%r report_name=%s views=%s' % (
            rr.id, rr.name or '', rr.report_name or '', views
        ))
expected_sale_names = ['Quotation / Order', 'PRO-FORMA Invoice', 'Delivery Note']
for name in expected_sale_names:
    if name not in sale_form_names:
        lines.append('  FAIL: missing sale.order form Print entry %r' % name)
        problems = problems + 1
for forbidden in ['Quotation / Order — 2026+', 'PRO-FORMA — 2026+', 'Delivery Note (DN) — 2026+']:
    if forbidden in sale_form_names:
        lines.append('  FAIL: duplicate sale.order Print entry still visible %r' % forbidden)
        problems = problems + 1

move_visible = Report.search([
    ('model', '=', 'account.move'),
    ('binding_model_id.model', '=', 'account.move'),
    ('binding_type', '=', 'report'),
], order='id asc')
move_form_names = []
for rr in move_visible:
    views = rr.binding_view_types or ''
    if not views or 'form' in views.split(','):
        move_form_names.append(rr.name or '')
        lines.append('  account.move id=%s name=%r report_name=%s views=%s' % (
            rr.id, rr.name or '', rr.report_name or '', views
        ))
if 'Invoices' not in move_form_names:
    lines.append('  FAIL: standard Invoices form Print entry missing.')
    problems = problems + 1
for forbidden in ['Invoices without Payment', 'VAT Invoices RI/DPI - 2026+']:
    if forbidden in move_form_names:
        lines.append('  FAIL: duplicate account.move Print entry still visible %r' % forbidden)
        problems = problems + 1
lines.append('')

lines.append('PREVIEW ACTION AND EFFECTIVE BUTTON')
preview_action_id = int(Param.get_param(C20_MARKER + '.report_action_id') or '0')
preview_view_id = int(Param.get_param(C20_MARKER + '.view_id') or '0')
preview_action = Report.browse(preview_action_id) if preview_action_id else Report.browse()
preview_view = View.browse(preview_view_id) if preview_view_id else View.browse()

if not preview_action.exists():
    lines.append('  FAIL: Preview action id=%s missing.' % preview_action_id)
    problems = problems + 1
else:
    preview_ok = (
        preview_action.name == 'Invoice Preview'
        and preview_action.model == 'account.move'
        and preview_action.report_type == 'qweb-html'
        and preview_action.report_name == BARANI_VAT
        and preview_action.report_file == BARANI_VAT
        and not preview_action.binding_model_id
    )
    lines.append(
        '  action id=%s name=%r report_type=%s report_name=%s bound=%s: %s'
        % (
            preview_action.id, preview_action.name or '',
            preview_action.report_type or '', preview_action.report_name or '',
            bool(preview_action.binding_model_id),
            'PASS' if preview_ok else 'FAIL'
        )
    )
    if not preview_ok:
        problems = problems + 1

if not preview_view.exists():
    lines.append('  FAIL: Preview inherited view id=%s missing.' % preview_view_id)
    problems = problems + 1
else:
    view_ok = (
        preview_view.active
        and preview_view.model == 'account.move'
        and preview_view.key == 'barani_runtime.account_move_preview_2026_button'
        and preview_view.priority == 999
    )
    lines.append(
        '  view id=%s name=%r key=%r active=%s priority=%s: %s'
        % (
            preview_view.id, preview_view.name or '', preview_view.key or '',
            preview_view.active, preview_view.priority,
            'PASS' if view_ok else 'FAIL'
        )
    )
    if not view_ok:
        problems = problems + 1

effective_arch = ''
try:
    effective_arch = (Move.get_view(view_type='form') or {}).get('arch') or ''
except Exception as exc:
    lines.append('  FAIL: effective account.move form could not be read: %s' % str(exc)[:500])
    problems = problems + 1

marker1 = 'name="%s"' % preview_action_id
marker2 = "name='%s'" % preview_action_id
pos = effective_arch.find(marker1)
if pos == -1:
    pos = effective_arch.find(marker2)
snippet = effective_arch[max(0, pos - 350):min(len(effective_arch), pos + 800)] if pos != -1 else ''
button_ok = (
    pos != -1
    and ('type="action"' in snippet or "type='action'" in snippet)
    and ('string="Preview"' in snippet or "string='Preview'" in snippet)
)
lines.append('  effective Preview button: %s' % ('PASS' if button_ok else 'FAIL'))
lines.append('  snippet=%r' % snippet.replace(NL, ' '))
if not button_ok:
    problems = problems + 1
lines.append('')

lines.append('ARCHIVED FORMER ODOO QWEB WRAPPERS')
archive_specs = [
    ('sale_qso', 'sale.report_saleorder', 'Archived — Odoo Quotation / Order'),
    ('sale_pf', 'sale.report_saleorder_pro_forma', 'Archived — Odoo Pro-Forma Invoice'),
    ('account_invoice', 'account.report_invoice_with_payments', 'Archived — Odoo Invoice with Payments'),
    ('account_invoice_without_payment', 'account.report_invoice', 'Archived — Odoo Invoice without Payments'),
]
for item in archive_specs:
    token = item[0]
    expected_key = item[1]
    expected_name = item[2]
    rs = View.search([('type', '=', 'qweb'), ('key', '=', expected_key)], order='id asc')
    if len(rs) != 1:
        lines.append('  %s: FAIL — expected one QWeb view, found=%s' % (expected_key, len(rs)))
        problems = problems + 1
    else:
        vw = rs[0]
        snap_key = Param.get_param(PREFIX + '.view.' + str(vw.id) + '.key') or ''
        arch_param = Param.search([('key', '=', PREFIX + '.view.' + str(vw.id) + '.arch_db')], limit=1)
        snap_arch = arch_param.value if arch_param else None
        ok = (
            vw.name == expected_name
            and vw.key == expected_key
            and snap_key == expected_key
            and snap_arch is not None
            and (vw.arch_db or '') == (snap_arch or '')
            and vw.active
        )
        lines.append(
            '  id=%s key=%s name=%r active=%s bytes_match_B10=%s: %s'
            % (
                vw.id, vw.key or '', vw.name or '', vw.active,
                snap_arch is not None and (vw.arch_db or '') == (snap_arch or ''),
                'PASS' if ok else 'FAIL'
            )
        )
        if not ok:
            problems = problems + 1
lines.append('')

lines.append('MAIL TEMPLATE REPORT REFERENCES')
if 'mail.template' not in env:
    lines.append('  WARN: mail.template unavailable.')
    warnings = warnings + 1
else:
    Template = env['mail.template'].sudo().with_context(active_test=False)
    templates = Template.search([('model', 'in', ('sale.order', 'account.move'))], order='model,id', limit=250)
    if 'report_template' not in Template._fields:
        lines.append('  WARN: report_template field unavailable.')
        warnings = warnings + 1
    else:
        for tmpl in templates:
            if tmpl.report_template:
                rr = tmpl.report_template
                aligned = (
                    (tmpl.model == 'sale.order' and rr.id == env.ref('sale.action_report_saleorder').id and rr.report_name == BARANI_QSO)
                    or
                    (tmpl.model == 'account.move' and rr.id == env.ref('account.account_invoices').id and rr.report_name == BARANI_VAT)
                )
                lines.append(
                    '  id=%s model=%s name=%r report_action=%s:%s:%s result=%s'
                    % (
                        tmpl.id, tmpl.model or '', tmpl.name or '',
                        rr.id, rr.name or '', rr.report_name or '',
                        'BARANI/ALIGNED' if aligned else 'REVIEW'
                    )
                )
                if not aligned:
                    warnings = warnings + 1
lines.append('')

lines.append('FINAL SUMMARY')
lines.append('  problems=%s' % problems)
lines.append('  warnings=%s' % warnings)
lines.append('  writes_performed=0')
lines.append('  accepted state=%s' % ('PASS' if problems == 0 else 'FAIL'))

full = NL.join(lines)
start = (PAGE - 1) * PAGE_SIZE
end = start + PAGE_SIZE
more = 'YES' if end < len(full) else 'NO'
raise UserError(('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s%s%s' % (
    PAGE, start, min(end, len(full)), len(full), more, NL, full[start:end]
))[:90000])
