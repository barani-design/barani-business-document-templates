# ============================================================================
# ACTION NAME : F02 READ-ONLY — Verify BARANI future Payment Ref + Valid Until UI
# MODEL       : Module (ir.module.module) recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
# PURPOSE     : Verifies the F01 runtime records, historical no-change hashes,
#               future sale.order.reference values, future invoice propagation,
#               and the standard Valid Until inherited form view.
# READ-ONLY   : No writes, no report rendering, no portal calls.
# ============================================================================

PAGE = 1
PAGE_SIZE = 30000

F00_MARKER = 'barani.future_ref_validity.f00.marker'
F00_PREFIX = 'barani.future_ref_validity.f00.'
F01_MARKER = 'barani.future_ref_validity.f01.marker'
F01_PREFIX = 'barani.future_ref_validity.f01.'

RUNTIME_MODULE = 'barani_runtime'
AUTO_XID = 'sale_order_future_payment_ref_automation'
SERVER_XID = 'sale_order_future_payment_ref_server_action'
VIEW_XID = 'view_order_form_valid_until_visible'
VIEW_KEY = 'barani_runtime.sale_order_valid_until_visible'

NL = chr(10)
SEP = chr(31)

Param = env['ir.config_parameter'].sudo()
Data = env['ir.model.data'].sudo().with_context(active_test=False)
Automation = env['base.automation'].sudo().with_context(active_test=False)
Server = env['ir.actions.server'].sudo().with_context(active_test=False)
View = env['ir.ui.view'].sudo().with_context(lang=None, active_test=False)
Report = env['ir.actions.report'].sudo().with_context(lang=None)
Sale = env['sale.order'].sudo().with_context(active_test=False)
Move = env['account.move'].sudo().with_context(active_test=False)

lines = []
lines.append('F02 READ-ONLY — Verify BARANI future Payment Ref + Valid Until UI')
lines.append('READ-ONLY:YES PAGE=%s PAGE_SIZE=%s' % (PAGE, PAGE_SIZE))
lines.append('')
problems = 0
warnings = 0

def digits_only(value):
    out = ''
    for ch in (value or ''):
        if ch >= '0' and ch <= '9':
            out = out + ch
    return out

def report_signature(rec):
    return SEP.join([
        str(rec.id), rec.name or '', rec.model or '', rec.report_type or '',
        rec.report_name or '', rec.report_file or '',
        str(rec.binding_model_id.id if rec.binding_model_id else 0),
        rec.binding_type or '', rec.binding_view_types or '',
        str(rec.paperformat_id.id if rec.paperformat_id else 0),
        ','.join([str(x) for x in sorted(rec.groups_id.ids)]),
    ])

for marker, label in [(F00_MARKER, 'F00'), (F01_MARKER, 'F01')]:
    ok = Param.get_param(marker) == '1'
    lines.append('%s marker: %s' % (label, 'PASS' if ok else 'FAIL'))
    if not ok:
        problems = problems + 1

# ---------------------------------------------------------------------------
# A) Runtime definitions
# ---------------------------------------------------------------------------
lines.append('')
lines.append('A) RUNTIME DEFINITION READ-BACK')
def resolve(module, name, model_name, model_obj):
    md = Data.search([('module', '=', module), ('name', '=', name), ('model', '=', model_name)], limit=1)
    return model_obj.browse(md.res_id).exists() if md else model_obj.browse([])

auto = resolve(RUNTIME_MODULE, AUTO_XID, 'base.automation', Automation)
server = resolve(RUNTIME_MODULE, SERVER_XID, 'ir.actions.server', Server)
validity_view = resolve(RUNTIME_MODULE, VIEW_XID, 'ir.ui.view', View)
sale_form = env.ref('sale.view_order_form', raise_if_not_found=False)
expected_code = Param.get_param(F01_PREFIX + 'automation_code') or ''
expected_view_arch = Param.get_param(F01_PREFIX + 'view_arch') or ''

auto_ok = bool(auto) and auto.active and auto.trigger == 'on_create' and (auto.filter_domain or '') == "[('reference', '=', False)]"
server_ok = bool(server) and server.model_id.model == 'sale.order' and (server.code or '') == expected_code and 'dds_' not in (server.code or '').lower()
view_ok = bool(validity_view) and validity_view.active and validity_view.inherit_id == sale_form and (validity_view.key or '') == VIEW_KEY and (validity_view.arch_db or '') == expected_view_arch and 'validity_date' in (validity_view.arch_db or '')
lines.append('  future Payment Ref automation: %s id=%s trigger=%r active=%s' % ('PASS' if auto_ok else 'FAIL', auto.id if auto else 0, auto.trigger if auto else '', bool(auto.active) if auto else False))
lines.append('  automation server action: %s id=%s no_DDS=%s' % ('PASS' if server_ok else 'FAIL', server.id if server else 0, 'dds_' not in (server.code or '').lower() if server else False))
lines.append('  standard Valid Until inherited view: %s id=%s key=%r' % ('PASS' if view_ok else 'FAIL', validity_view.id if validity_view else 0, validity_view.key if validity_view else ''))
if not auto_ok:
    problems = problems + 1
if not server_ok:
    problems = problems + 1
if not view_ok:
    problems = problems + 1

# ---------------------------------------------------------------------------
# B) Historical no-change hashes
# ---------------------------------------------------------------------------
lines.append('')
lines.append('B) HISTORICAL VALUE-PRESERVATION CHECK')
cutoff_sale_id = int(Param.get_param(F01_PREFIX + 'cutoff_sale_id') or '0')
cutoff_move_id = int(Param.get_param(F01_PREFIX + 'cutoff_move_id') or '0')
expected_sale_hash = Param.get_param(F01_PREFIX + 'sale_reference_hash_before') or ''
expected_move_hash = Param.get_param(F01_PREFIX + 'move_payment_reference_hash_before') or ''
env.cr.execute("SELECT COALESCE(md5(string_agg(id::text || ':' || COALESCE(reference, ''), '|' ORDER BY id)), md5('')) FROM sale_order WHERE id <= %s", (cutoff_sale_id,))
current_sale_hash = (env.cr.fetchone() or ('',))[0] or ''
env.cr.execute("SELECT COALESCE(md5(string_agg(id::text || ':' || COALESCE(payment_reference, ''), '|' ORDER BY id)), md5('')) FROM account_move WHERE id <= %s AND move_type IN ('out_invoice','out_refund')", (cutoff_move_id,))
current_move_hash = (env.cr.fetchone() or ('',))[0] or ''
sale_hist_ok = bool(expected_sale_hash) and current_sale_hash == expected_sale_hash
move_hist_ok = bool(expected_move_hash) and current_move_hash == expected_move_hash
lines.append('  existing sale.order.reference through id %s: %s' % (cutoff_sale_id, 'UNCHANGED_PASS' if sale_hist_ok else 'FAIL_CHANGED'))
lines.append('  existing account.move.payment_reference through id %s: %s' % (cutoff_move_id, 'UNCHANGED_PASS' if move_hist_ok else 'FAIL_CHANGED'))
if not sale_hist_ok:
    problems = problems + 1
if not move_hist_ok:
    problems = problems + 1

# ---------------------------------------------------------------------------
# C) Future sale orders
# ---------------------------------------------------------------------------
lines.append('')
lines.append('C) FUTURE SALE.ORDER PAYMENT REF CHECK')
future_sales = Sale.search([('id', '>', cutoff_sale_id)], order='id')
correct = 0
blank = 0
mismatch = 0
no_digits = 0
for so in future_sales:
    proposed = digits_only(so.name or '')
    if not proposed:
        no_digits = no_digits + 1
        if no_digits <= 20:
            lines.append('  NO_DIGITS id=%s name=%r reference=%r' % (so.id, so.name or '', so.reference or ''))
    elif (so.reference or '') == proposed:
        correct = correct + 1
        if correct <= 20:
            lines.append('  PASS id=%s name=%r reference=%r validity_date=%s state=%s' % (so.id, so.name or '', so.reference or '', so.validity_date or '', so.state or ''))
    elif not so.reference:
        blank = blank + 1
        if blank <= 20:
            lines.append('  FAIL_BLANK id=%s name=%r expected=%r' % (so.id, so.name or '', proposed))
    else:
        mismatch = mismatch + 1
        if mismatch <= 20:
            lines.append('  FAIL_MISMATCH id=%s name=%r reference=%r expected=%r' % (so.id, so.name or '', so.reference or '', proposed))
lines.append('  future sale orders=%s correct=%s blank=%s mismatch=%s no_digits=%s' % (len(future_sales), correct, blank, mismatch, no_digits))
if blank or mismatch:
    problems = problems + blank + mismatch
if no_digits:
    problems = problems + no_digits
if not future_sales:
    lines.append('  NO FUTURE TEST RECORDS YET — create one new quotation after F01 and rerun F02.')
    warnings = warnings + 1

# ---------------------------------------------------------------------------
# D) Future invoice propagation
# ---------------------------------------------------------------------------
lines.append('')
lines.append('D) FUTURE INVOICE STANDARD PROPAGATION CHECK')
future_moves = Move.search([('id', '>', cutoff_move_id), ('move_type', 'in', ['out_invoice', 'out_refund'])], order='id')
prop_correct = 0
prop_mismatch = 0
zero_source = 0
multi_source = 0
for move in future_moves:
    sales = move.invoice_line_ids.mapped('sale_line_ids.order_id')
    future_linked = sales.filtered(lambda s: s.id > cutoff_sale_id)
    if len(future_linked) == 1 and len(sales) == 1:
        so = future_linked[0]
        expected = so.reference or ''
        if expected and (move.payment_reference or '') == expected:
            prop_correct = prop_correct + 1
            if prop_correct <= 20:
                lines.append('  PASS move=%r id=%s source=%r payment_reference=%r' % (move.name or '', move.id, so.name or '', move.payment_reference or ''))
        else:
            prop_mismatch = prop_mismatch + 1
            if prop_mismatch <= 20:
                lines.append('  FAIL move=%r id=%s source=%r source_reference=%r payment_reference=%r' % (move.name or '', move.id, so.name or '', expected, move.payment_reference or ''))
    elif len(sales) == 0:
        zero_source = zero_source + 1
    elif len(sales) > 1:
        multi_source = multi_source + 1
lines.append('  future customer moves=%s exact-one-future-source correct=%s mismatch=%s zero_source=%s multi_source=%s' % (len(future_moves), prop_correct, prop_mismatch, zero_source, multi_source))
if prop_mismatch:
    problems = problems + prop_mismatch
if not future_moves:
    lines.append('  NO FUTURE INVOICE TEST RECORDS YET — create an invoice from the new quotation and rerun F02.')
    warnings = warnings + 1

# ---------------------------------------------------------------------------
# E) Routing no-drift check
# ---------------------------------------------------------------------------
lines.append('')
lines.append('E) REPORT ROUTING / PREVIEW NO-DRIFT CHECK')
preview_actions = Report.search([('model', '=', 'account.move'), ('report_type', '=', 'qweb-html'), ('report_name', '=', 'barani_vat.report_invoice_document_vat')], limit=2)
preview_views = View.search([('key', '=', 'barani_runtime.account_move_preview_2026_button')], limit=2)
preview_action_ok = len(preview_actions) == 1 and report_signature(preview_actions[0]) == (Param.get_param(F00_PREFIX + 'preview.action.signature') or '')
preview_view_current = ''
if len(preview_views) == 1:
    pv = preview_views[0]
    preview_view_current = SEP.join([str(pv.id), pv.key or '', pv.name or '', pv.model or '', pv.type or '', str(pv.inherit_id.id if pv.inherit_id else 0), str(pv.priority), '1' if pv.active else '0'])
preview_view_ok = len(preview_views) == 1 and preview_view_current == (Param.get_param(F00_PREFIX + 'preview.view.signature') or '')
lines.append('  accepted invoice Preview action: %s' % ('PASS' if preview_action_ok else 'FAIL_DRIFT'))
lines.append('  accepted invoice Preview view: %s' % ('PASS' if preview_view_ok else 'FAIL_DRIFT'))
if not preview_action_ok:
    problems = problems + 1
if not preview_view_ok:
    problems = problems + 1

for token, xid in [
    ('std_sale', 'sale.action_report_saleorder'),
    ('std_pf', 'sale.action_report_pro_forma_invoice'),
    ('std_inv', 'account.account_invoices'),
    ('std_inv_np', 'account.account_invoices_without_payment'),
]:
    rec = env.ref(xid, raise_if_not_found=False)
    expected = Param.get_param(F00_PREFIX + 'report.' + token + '.signature') or ''
    ok = bool(rec) and report_signature(rec) == expected
    lines.append('  %s: %s' % (xid, 'PASS' if ok else 'FAIL_DRIFT'))
    if not ok:
        problems = problems + 1

lines.append('')
lines.append('F) MANUAL UI / WORKFLOW ACCEPTANCE')
manual = [
    'Create a NEW quotation after F01; confirm its technical Payment Ref. equals digits-only Q number.',
    'Draft/Sent quotation shows Valid Until and allows editing.',
    'Confirmed/Locked/Cancelled Sales Order shows Valid Until read-only.',
    'Create invoice from the new quotation; invoice Payment Reference equals the Sales Order Payment Ref.',
    'Historical invoice 2026233 remains RF19 5113 08 in the stored UI field.',
    'BARANI PDFs still show the existing source-derived historical fallback correctly.',
    'Print menus and Invoice Preview remain exactly as accepted by V40.',
]
for item in manual:
    lines.append('  [ ] ' + item)

lines.append('')
lines.append('SUMMARY problems=%s warnings=%s WRITE ACTIONS PERFORMED: NONE' % (problems, warnings))
if problems:
    lines.append('RESULT: FAIL — review before closing.')
elif not future_sales or not future_moves:
    lines.append('RESULT: CONFIGURATION PASS / FUTURE RECORD MANUAL TEST PENDING.')
else:
    lines.append('RESULT: PASS — future standard-field propagation and Valid Until runtime state verified.')

full = NL.join(lines)
if PAGE < 1 or PAGE_SIZE < 1000:
    raise UserError('ERROR: invalid PAGE/PAGE_SIZE')
start = (PAGE - 1) * PAGE_SIZE
end = min(start + PAGE_SIZE, len(full))
if start >= len(full) and PAGE > 1:
    raise UserError('ERROR: PAGE starts beyond output length=%s' % len(full))
more = end < len(full)
raise UserError(full[start:end] + NL + NL + 'PAGE %s | chars %s-%s of %s | MORE REMAINS: %s' % (PAGE, start, end, len(full), 'YES' if more else 'NO'))
