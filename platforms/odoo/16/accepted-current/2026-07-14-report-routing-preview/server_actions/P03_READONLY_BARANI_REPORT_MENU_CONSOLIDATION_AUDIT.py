# ============================================================================
# ACTION NAME : P03 READ-ONLY — BARANI report-menu consolidation audit
# MODEL       : Module (ir.module.module) recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
# PURPOSE     : Inventory all sale.order and account.move report actions that
#               can appear in Print menus, identify the stock/default actions,
#               BARANI 2026+ actions, email-template report references, and the
#               safest consolidation target.
#
# TARGET UX   :
#   Sales Print:
#     - Quotation / Order          -> BARANI commercial Q/SO renderer
#     - PRO-FORMA Invoice          -> BARANI commercial PF renderer
#     - Delivery Note             -> BARANI delivery renderer
#   Accounting Print:
#     - one standard Invoice item  -> BARANI RI/DPI/Credit Note renderer
#
# IMPORTANT   :
#   - This action does NOT modify, unbind, rename, archive, or delete anything.
#   - It does NOT assume that changing a Print action changes the Preview button.
#   - Preview routing remains a separate P01 workstream.
#
# SAFETY      : READ-ONLY:YES. No create/write/unlink/set_param/SQL writes.
# ============================================================================

PAGE = 1
PAGE_SIZE = 60000

NL = chr(10)
lines = []
lines.append('P03 READ-ONLY — BARANI report-menu consolidation audit')
lines.append('READ-ONLY:YES — search/read only; no actions, templates, bindings, email templates, or records are changed. PAGE=%s PAGE_SIZE=%s' % (PAGE, PAGE_SIZE))
lines.append('Purpose: replace duplicate user-facing Print entries with standard labels routed to BARANI renderers; keep Preview as a separate route.')
lines.append('')

problems = 0
warnings = 0

required_models = ['ir.actions.report', 'ir.model.data', 'ir.ui.view', 'ir.model']
optional_models = ['mail.template']

lines.append('MODEL PREFLIGHT')
for model_name in required_models:
    ok = model_name in env
    lines.append('  %s: %s' % (model_name, 'PASS' if ok else 'FAIL'))
    if not ok:
        problems = problems + 1
for model_name in optional_models:
    ok = model_name in env
    lines.append('  %s: %s' % (model_name, 'PASS' if ok else 'WARN/ABSENT'))
    if not ok:
        warnings = warnings + 1
lines.append('')

if problems:
    full_text = NL.join(lines)
    start = (PAGE - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    more = end < len(full_text)
    raise UserError('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s%s%s' % (
        PAGE, start, min(end, len(full_text)), len(full_text), 'YES' if more else 'NO', NL, full_text[start:end]
    ))

Report = env['ir.actions.report'].sudo().with_context(active_test=False)
ModelData = env['ir.model.data'].sudo().with_context(active_test=False)
View = env['ir.ui.view'].sudo().with_context(active_test=False, lang=None)

def xmlids_for(model_name, res_id):
    rows = ModelData.search([('model', '=', model_name), ('res_id', '=', res_id)], order='module,name')
    vals = []
    for row in rows:
        vals.append('%s.%s' % (row.module, row.name))
    return vals

def field_value(record, field_name, default=''):
    if field_name not in record._fields:
        return default
    value = record[field_name]
    if hasattr(value, '_name'):
        return value
    return value

def report_line(rr):
    binding_model = rr.binding_model_id.model if ('binding_model_id' in rr._fields and rr.binding_model_id) else ''
    binding_type = rr.binding_type if 'binding_type' in rr._fields else ''
    binding_views = rr.binding_view_types if 'binding_view_types' in rr._fields else ''
    active_value = rr.active if 'active' in rr._fields else 'n/a'
    visible = bool(binding_model == rr.model and binding_type == 'report')
    groups = []
    if 'groups_id' in rr._fields:
        groups = rr.groups_id.mapped('display_name')
    xmlids = xmlids_for('ir.actions.report', rr.id)
    return (
        '  id=%s name=%r model=%s report_name=%s report_file=%s report_type=%s '
        'visible_in_Print=%s binding_model=%s binding_type=%s binding_views=%s '
        'paperformat=%r active=%s groups=%s attachment_use=%s xmlids=%s'
    ) % (
        rr.id,
        rr.name or '',
        rr.model or '',
        rr.report_name or '',
        rr.report_file or '' if 'report_file' in rr._fields else '',
        rr.report_type or '',
        'YES' if visible else 'NO',
        binding_model,
        binding_type or '',
        binding_views or '',
        rr.paperformat_id.name if rr.paperformat_id else '',
        active_value,
        ','.join(groups) if groups else 'NONE',
        rr.attachment_use if 'attachment_use' in rr._fields else 'n/a',
        ','.join(xmlids) if xmlids else 'NONE',
    )

lines.append('ALL SALE.ORDER REPORT ACTIONS')
sale_reports = Report.search([('model', '=', 'sale.order')], order='id asc')
if not sale_reports:
    lines.append('  NONE')
    problems = problems + 1
for rr in sale_reports:
    lines.append(report_line(rr))
lines.append('')

lines.append('ALL ACCOUNT.MOVE REPORT ACTIONS')
move_reports = Report.search([('model', '=', 'account.move')], order='id asc')
if not move_reports:
    lines.append('  NONE')
    problems = problems + 1
for rr in move_reports:
    lines.append(report_line(rr))
lines.append('')

expected_xmlids = [
    ('sale.action_report_saleorder', 'stock/default Q/SO action'),
    ('sale.action_report_pro_forma_invoice', 'stock/default PF action'),
    ('account.account_invoices', 'stock/default invoice action'),
    ('account.account_invoices_without_payment', 'stock/default invoice-without-payment action'),
]
lines.append('EXPECTED STOCK/DEFAULT REPORT ACTION XMLIDS')
stock_actions = {}
for xmlid, label in expected_xmlids:
    rec = env.ref(xmlid, raise_if_not_found=False)
    if rec and rec._name == 'ir.actions.report':
        stock_actions[xmlid] = rec
        lines.append('  %s (%s): PASS id=%s name=%r report_name=%s visible=%s' % (
            xmlid,
            label,
            rec.id,
            rec.name or '',
            rec.report_name or '',
            'YES' if (rec.binding_model_id and rec.binding_model_id.model == rec.model and rec.binding_type == 'report') else 'NO',
        ))
    else:
        lines.append('  %s (%s): WARN/NOT FOUND' % (xmlid, label))
        warnings = warnings + 1
lines.append('')

target_reports = [
    ('BARANI Q/SO', 'sale.order', 'barani_commercial.report_saleorder'),
    ('BARANI PF', 'sale.order', 'barani_commercial.report_saleorder_proforma'),
    ('BARANI Delivery Note', 'sale.order', 'barani_delivery.report_sale_order_delivery_note_2026'),
    ('BARANI RI/DPI/Credit Note', 'account.move', 'barani_vat.report_invoice_document_vat'),
]
lines.append('BARANI TARGET REPORT ACTIONS')
barani_targets = {}
for label, model_name, report_name in target_reports:
    rs = Report.search([('model', '=', model_name), ('report_name', '=', report_name)], order='id asc')
    barani_targets[report_name] = rs
    if not rs:
        lines.append('  %s: FAIL — no action for %s' % (label, report_name))
        problems = problems + 1
    else:
        lines.append('  %s count=%s' % (label, len(rs)))
        for rr in rs:
            lines.append(report_line(rr))
lines.append('')

lines.append('VISIBLE PRINT-MENU SUMMARY')
for model_name, reports in [('sale.order', sale_reports), ('account.move', move_reports)]:
    visible_reports = reports.filtered(
        lambda r: r.binding_model_id and r.binding_model_id.model == model_name and r.binding_type == 'report'
    )
    lines.append('  %s visible report count=%s' % (model_name, len(visible_reports)))
    for rr in visible_reports:
        lines.append('    id=%s name=%r report_name=%s' % (rr.id, rr.name or '', rr.report_name or ''))
    if model_name == 'sale.order' and len(visible_reports) > 3:
        lines.append('    FINDING: duplicate/extra Sales Print entries exist; target is three user-facing entries.')
        warnings = warnings + 1
    if model_name == 'account.move' and len(visible_reports) > 1:
        lines.append('    FINDING: duplicate/extra Accounting Print entries exist; target is one user-facing invoice entry.')
        warnings = warnings + 1
lines.append('')

lines.append('ROUTING GAP CHECKS')
routing_checks = [
    ('sale.action_report_saleorder', 'barani_commercial.report_saleorder'),
    ('sale.action_report_pro_forma_invoice', 'barani_commercial.report_saleorder_proforma'),
    ('account.account_invoices', 'barani_vat.report_invoice_document_vat'),
    ('account.account_invoices_without_payment', 'barani_vat.report_invoice_document_vat'),
]
for xmlid, desired_report_name in routing_checks:
    rr = stock_actions.get(xmlid)
    if not rr:
        lines.append('  %s: NOT PROVEN — stock/default action absent' % xmlid)
        continue
    ok = (rr.report_name or '') == desired_report_name
    lines.append('  %s current=%s desired=%s: %s' % (
        xmlid, rr.report_name or '', desired_report_name, 'ALREADY ALIGNED' if ok else 'RELINK NEEDED'
    ))
lines.append('')

lines.append('CUSTOM DUPLICATE ACTION BINDING CHECK')
custom_binding_targets = [
    ('barani_commercial.report_saleorder', 'Q/SO custom action'),
    ('barani_commercial.report_saleorder_proforma', 'PF custom action'),
    ('barani_vat.report_invoice_document_vat', 'RI/DPI custom action'),
]
for report_name, label in custom_binding_targets:
    rs = barani_targets.get(report_name) or Report.browse([])
    for rr in rs:
        visible = bool(rr.binding_model_id and rr.binding_model_id.model == rr.model and rr.binding_type == 'report')
        lines.append('  %s id=%s name=%r visible_in_Print=%s -> %s' % (
            label, rr.id, rr.name or '', 'YES' if visible else 'NO',
            'UNBIND CANDIDATE after stock action relink' if visible else 'already hidden'
        ))
lines.append('')

lines.append('DELIVERY NOTE USER-FACING NAME CHECK')
dn_rs = barani_targets.get('barani_delivery.report_sale_order_delivery_note_2026') or Report.browse([])
for rr in dn_rs:
    lines.append('  id=%s current_name=%r target_user_name=%r result=%s' % (
        rr.id,
        rr.name or '',
        'Delivery Note',
        'RENAME CANDIDATE' if (rr.name or '') != 'Delivery Note' else 'ALREADY SIMPLE',
    ))
lines.append('')

lines.append('QWEB TEMPLATE PRESERVATION CHECK')
template_keys = [
    'barani_commercial.report_saleorder',
    'barani_commercial.report_saleorder_proforma',
    'barani_commercial.report_saleorder_document',
    'barani_vat.report_invoice_document_vat',
    'barani_delivery.report_sale_order_delivery_note_2026',
    'barani_delivery.report_delivery_note_2026',
]
for key in template_keys:
    rs = View.search([('type', '=', 'qweb'), ('key', '=', key)], order='id asc')
    lines.append('  key=%s count=%s ids=%s' % (
        key, len(rs), ','.join([str(x.id) for x in rs]) if rs else 'NONE'
    ))
    if len(rs) != 1:
        warnings = warnings + 1
lines.append('  POLICY: BARANI QWeb templates are renderers/source-of-truth and are NOT deletion candidates.')
lines.append('  POLICY: stock/module-owned QWeb templates should remain installed even when their report actions are rerouted.')
lines.append('')

lines.append('UNBOUND TEST/LEGACY REPORT ACTIONS')
legacy_rs = Report.search([
    '|', '|',
    ('name', 'ilike', 'TEST'),
    ('name', 'ilike', '2026+'),
    ('report_name', 'ilike', 'barani_test'),
], order='id asc')
if not legacy_rs:
    lines.append('  NONE')
for rr in legacy_rs:
    visible = bool(rr.binding_model_id and rr.binding_model_id.model == rr.model and rr.binding_type == 'report')
    lines.append('  id=%s name=%r report_name=%s visible_in_Print=%s xmlids=%s' % (
        rr.id, rr.name or '', rr.report_name or '', 'YES' if visible else 'NO',
        ','.join(xmlids_for('ir.actions.report', rr.id)) or 'NONE'
    ))
lines.append('  POLICY: unbound test/legacy actions can be retained for rollback until a dependency audit proves safe removal.')
lines.append('')

lines.append('MAIL TEMPLATE REPORT REFERENCES')
if 'mail.template' not in env:
    lines.append('  mail.template model absent — skipped')
else:
    Template = env['mail.template'].sudo().with_context(active_test=False)
    field_names = Template._fields
    report_fields = []
    for candidate in ['report_template', 'report_template_ids']:
        if candidate in field_names:
            report_fields.append(candidate)
    lines.append('  discovered dynamic report fields=%s' % (','.join(report_fields) if report_fields else 'NONE'))
    templates = Template.search([('model', 'in', ('sale.order', 'account.move'))], order='model,id', limit=200)
    if not templates:
        lines.append('  NONE for sale.order/account.move')
    for tmpl in templates:
        refs = []
        if 'report_template' in report_fields and tmpl.report_template:
            rr = tmpl.report_template
            refs.append('%s:%s:%s' % (rr.id, rr.name or '', rr.report_name or ''))
        if 'report_template_ids' in report_fields and tmpl.report_template_ids:
            for rr in tmpl.report_template_ids:
                refs.append('%s:%s:%s' % (rr.id, rr.name or '', rr.report_name or ''))
        if refs or ('report_name' in tmpl._fields and tmpl.report_name):
            lines.append('  id=%s name=%r model=%s report_refs=%s report_name_expr=%r' % (
                tmpl.id,
                tmpl.name or '',
                tmpl.model or '',
                '; '.join(refs) if refs else 'NONE',
                tmpl.report_name if 'report_name' in tmpl._fields else '',
            ))
    lines.append('  AUDIT PURPOSE: confirm Send by Email / Send & Print attachments follow the relinked standard actions or BARANI renderer.')
lines.append('')

lines.append('RECOMMENDED END STATE — READ-ONLY FINDING')
lines.append('  Sales Print visible:')
lines.append('    1. Quotation / Order -> barani_commercial.report_saleorder')
lines.append('    2. PRO-FORMA Invoice -> barani_commercial.report_saleorder_proforma')
lines.append('    3. Delivery Note -> barani_delivery.report_sale_order_delivery_note_2026')
lines.append('  Accounting Print visible:')
lines.append('    1. Invoices (or Invoice / Credit Note) -> barani_vat.report_invoice_document_vat')
lines.append('  Hidden/unbound but retained:')
lines.append('    - custom duplicate Q/SO/PF/RI-DPI report action bindings')
lines.append('    - account.account_invoices_without_payment binding, while its underlying action remains aligned for code paths')
lines.append('    - test/legacy actions until dependency audit')
lines.append('  Separate requirement:')
lines.append('    - Preview button routing is NOT solved by Print-menu relinking; use P01 evidence and a BARANI qweb-html route/button override.')
lines.append('')

lines.append('SAFETY SUMMARY')
lines.append('  writes_performed=0')
lines.append('  report_actions_modified=0')
lines.append('  qweb_views_modified=0')
lines.append('  mail_templates_modified=0')
lines.append('  business_records_modified=0')
lines.append('  warnings=%s problems=%s' % (warnings, problems))

full_text = NL.join(lines)
start = (PAGE - 1) * PAGE_SIZE
end = start + PAGE_SIZE
more = end < len(full_text)
page_text = full_text[start:end]
raise UserError('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s%s%s' % (
    PAGE, start, min(end, len(full_text)), len(full_text), 'YES' if more else 'NO', NL, page_text
))
