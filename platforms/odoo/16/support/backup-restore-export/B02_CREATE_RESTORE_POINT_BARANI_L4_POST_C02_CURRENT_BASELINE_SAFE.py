# ============================================================================
# ACTION NAME : B02 CREATE RESTORE POINT — BARANI L4 post-C02 current baseline SAFE
# MODEL       : Module (ir.module.module) recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
# CREATE AT   : Settings -> Technical -> Actions -> Server Actions.
# VISIBILITY  : Maintenance-only. Run from the Server Action form.
# PURPOSE     : Creates a one-time current-state rollback point after the validated
#               C02 commercial Q/SO/PF date-format hotfix, before further RI/DPI
#               or Delivery Note changes.
#
# CAPTURES:
#   - current BARANI commercial Q/SO/PF QWeb views.
#   - current BARANI VAT/RI/DPI QWeb views.
#   - current BARANI Delivery Note 2026 QWeb views.
#   - related commercial, VAT/RI/DPI, and Delivery Note report actions.
#   - related report paperformats.
#   - all customer invoices/refunds that resolve to exactly one sale.order source,
#     with current payment_reference and proposed numeric source reference.
#
# READ/WRITE: Writes only ir.config_parameter restore-point keys when DRY_RUN=False
#             and CONFIRM matches. No business records are modified.
# SAFETY    : DRY_RUN=True default; requires original B01 marker and C02 marker;
#             never overwrites a complete B02 restore point; exact read-back.
# PAGINATION: output normally one page.
#
# safe_eval : no import/def/lambda/comprehension/with/while/try/getattr/hasattr/
#             setattr/eval/exec/open in executable code.
# ============================================================================

DRY_RUN = True
CONFIRM = ''
CONFIRM_TOKEN = 'CREATE_BARANI_L4_POST_C02_CURRENT_BASELINE_RESTORE_POINT_B02'
PAGE = 1
PAGE_SIZE = 16000

RP_MARKER_B01 = 'barani.l4.restore_point.marker'
C02_MARKER = 'barani.l4.c02.date_format.comm.backup.marker'
RP_MARKER = 'barani.l4.post_c02.restore_point.marker'
RP_PREFIX = 'barani.l4.post_c02.restore_point.'
OUTPUT_KEY = 'barani.l4.post_c02.restore_point.output'

COMM_BODY_KEY = 'barani_commercial.report_saleorder_document'
COMM_LAYOUT_KEY = 'barani_commercial.external_layout_standard_titled'
COMM_QSO_KEY = 'barani_commercial.report_saleorder'
COMM_PF_KEY = 'barani_commercial.report_saleorder_proforma'
VAT_BODY_KEY = 'barani_vat.report_invoice_document_vat'
VAT_LAYOUT_KEY = 'barani_vat.external_layout_standard_titled'
DN_BODY_KEY = 'barani_delivery.report_delivery_note_2026'
DN_LAYOUT_KEY = 'barani_delivery.external_layout_delivery_2026'
DIGITS = '0123456789'
SEP = chr(31)
NL = chr(10)

Param = env['ir.config_parameter'].sudo()
ViewB = env['ir.ui.view'].sudo().with_context(lang=None)
Rep = env['ir.actions.report'].sudo().with_context(lang=None)
PF = env['report.paperformat'].sudo().with_context(lang=None)
Order = env['sale.order'].sudo().with_context(active_test=False)
Move = env['account.move'].sudo().with_context(active_test=False)
Field = env['ir.model.fields'].sudo()

lines = []
lines.append('B02 CREATE RESTORE POINT — BARANI L4 post-C02 current baseline SAFE')
lines.append('DRY_RUN=%s CONFIRM_OK=%s PAGE=%s' % (DRY_RUN, CONFIRM == CONFIRM_TOKEN, PAGE))
lines.append('Captures current Q/SO/PF + RI/DPI + Delivery Note 2026 views/actions/paperformats and payment refs.')
lines.append('Writes only ir.config_parameter keys; business records are not modified.')
lines.append('')

problems = 0
rp_values = []
expected_keys = []

# Required prior safety markers.
if Param.get_param(RP_MARKER_B01) != '1':
    lines.append('FAIL: original B01 L4 restore point marker missing: %s' % RP_MARKER_B01)
    problems = problems + 1
else:
    lines.append('PRECHECK B01 marker: PASS')
if Param.get_param(C02_MARKER) != '1':
    lines.append('FAIL: C02 commercial date-format backup marker missing: %s' % C02_MARKER)
    problems = problems + 1
else:
    lines.append('PRECHECK C02 marker: PASS')

# ---- View capture -----------------------------------------------------------
view_items = [
    ('comm_body', COMM_BODY_KEY, 'required'),
    ('comm_layout', COMM_LAYOUT_KEY, 'required'),
    ('comm_qso_wrapper', COMM_QSO_KEY, 'required'),
    ('comm_pf_wrapper', COMM_PF_KEY, 'required'),
    ('vat_body', VAT_BODY_KEY, 'required'),
    ('vat_layout', VAT_LAYOUT_KEY, 'required'),
    ('dn_body', DN_BODY_KEY, 'required'),
    ('dn_layout', DN_LAYOUT_KEY, 'required'),
]

lines.append('')
lines.append('A) VIEW CAPTURE')
views = []
for vi in view_items:
    token = vi[0]
    key = vi[1]
    vs = ViewB.search([('key', '=', key), ('type', '=', 'qweb')], limit=2)
    if len(vs) != 1:
        lines.append('  FAIL view token=%s key=%s found=%s expected=1' % (token, key, len(vs)))
        problems = problems + 1
    else:
        v = vs[0]
        arch = v.arch_db or ''
        root_ok = arch.startswith('<t t-name="' + key + '"')
        standalone = not bool(v.inherit_id)
        lines.append('  VIEW token=%s id=%s key=%s len=%s standalone=%s root_ok=%s write_date=%s' % (
            token, v.id, key, len(arch), standalone, root_ok, v.write_date
        ))
        if (not standalone) or (not root_ok):
            problems = problems + 1
        views.append((token, key, v, arch))
        expected_keys.append(RP_PREFIX + 'view.' + token + '.id')
        expected_keys.append(RP_PREFIX + 'view.' + token + '.key')
        expected_keys.append(RP_PREFIX + 'view.' + token + '.arch')
        expected_keys.append(RP_PREFIX + 'view.' + token + '.write_date')

# ---- Current-state markers --------------------------------------------------
lines.append('')
lines.append('B) CURRENT-STATE MARKER CHECKS')
comm_arch = ''
vat_arch = ''
dn_arch = ''
for vv0 in views:
    if vv0[0] == 'comm_body':
        comm_arch = vv0[3]
    if vv0[0] == 'vat_body':
        vat_arch = vv0[3]
    if vv0[0] == 'dn_body':
        dn_arch = vv0[3]

checks = [
    ('commercial C02 month tuple present', 'barani_date_months' in comm_arch and 'JAN' in comm_arch and 'DEC' in comm_arch),
    ('commercial C02 document date display present', 'barani_doc_date_display' in comm_arch),
    ('commercial C02 valid-until display present', 'barani_valid_until_display' in comm_arch),
    ('commercial Payment Reference retained', 'Payment Reference' in comm_arch and 'barani_vs' in comm_arch),
    ('commercial Preferred Payment Method retained', 'Preferred Payment Method' in comm_arch),
    ('commercial fixed discount column retained', 'barani_discount_col_fixed' in comm_arch),
    ('commercial numeric VAT marker retained', 'barani_numeric_vat_rate_tax.amount' in comm_arch),
    ('VAT/RI-DPI body still BARANI VAT family', VAT_BODY_KEY in vat_arch),
    ('Delivery Note table marker retained', 'barani_delivery_line_table' in dn_arch),
    ('Delivery Note QR/barcode marker retained', 'move.product_id.barcode' in dn_arch and 'barcode_type=%s' in dn_arch),
    ('no stock sale body inside commercial body', 'sale.report_saleorder_document' not in comm_arch),
    ('no web.external_layout inside commercial body', 'web.external_layout' not in comm_arch),
    ('no DDS prefix in commercial body', 'dds_' not in comm_arch),
    ('no BRN prefix in commercial body', 'brn_' not in comm_arch),
    ('no DDS/BRN prefix in Delivery Note body', 'dds_' not in dn_arch and 'brn_' not in dn_arch),
]
for ck in checks:
    lines.append('  %s: %s' % (ck[0], 'PASS' if ck[1] else 'FAIL'))
    if not ck[1]:
        problems = problems + 1

# ---- Report actions ---------------------------------------------------------
report_items = [
    ('comm_qso', COMM_QSO_KEY, ''),
    ('comm_pf', COMM_PF_KEY, ''),
    ('vat', VAT_BODY_KEY, ''),
    ('dn', DN_BODY_KEY, 'stock.picking'),
]
reports = []
lines.append('')
lines.append('C) REPORT ACTION CAPTURE')
for ri in report_items:
    token = ri[0]
    report_name = ri[1]
    model_required = ri[2]
    if model_required:
        rs = Rep.search([('report_name', '=', report_name), ('model', '=', model_required)], limit=2)
    else:
        rs = Rep.search([('report_name', '=', report_name)], limit=2)
    if len(rs) != 1:
        lines.append('  FAIL report token=%s report_name=%s model_filter=%s found=%s expected=1' % (token, report_name, model_required or 'ANY', len(rs)))
        problems = problems + 1
    else:
        r = rs[0]
        groups = []
        for g in r.groups_id:
            groups.append(str(g.id))
        groups.sort()
        bm = r.binding_model_id.model if r.binding_model_id else ''
        lines.append('  REPORT token=%s id=%s name=%r model=%s report_name=%s binding_model=%s paper=%s groups=%s' % (
            token, r.id, r.name, r.model, r.report_name, bm, r.paperformat_id.id if r.paperformat_id else 0, ','.join(groups)
        ))
        reports.append((token, r))
        for fn in ['id','name','model','report_type','report_name','report_file','binding_type','binding_view_types','binding_model_id','paperformat_id','groups_ids','print_report_name','attachment_use','attachment','multi']:
            expected_keys.append(RP_PREFIX + 'report.' + token + '.' + fn)

# ---- Paperformats from report actions ---------------------------------------
paperformats = []
seen_pf_ids = []
lines.append('')
lines.append('D) PAPERFORMAT CAPTURE')
for rr0 in reports:
    token = rr0[0]
    r0 = rr0[1]
    if r0.paperformat_id:
        pf0 = r0.paperformat_id
        already_seen = False
        for sid in seen_pf_ids:
            if sid == pf0.id:
                already_seen = True
        if not already_seen:
            seen_pf_ids.append(pf0.id)
            paperformats.append((token, pf0))
            lines.append('  PAPER token=%s id=%s name=%r margins=%s/%s/%s/%s header_spacing=%s dpi=%s' % (
                token, pf0.id, pf0.name, pf0.margin_top, pf0.margin_bottom, pf0.margin_left, pf0.margin_right, pf0.header_spacing, pf0.dpi
            ))
    else:
        lines.append('  WARN report token=%s has no paperformat_id' % token)

for pp in paperformats:
    for fn in ['id','name','format','orientation','margin_top','margin_bottom','margin_left','margin_right','header_line','header_spacing','dpi','disable_shrinking','page_width','page_height','default']:
        expected_keys.append(RP_PREFIX + 'paperformat.' + pp[0] + '.' + fn)

# ---- Move payment_reference backup, exact-one source only -------------------
lines.append('')
lines.append('E) ACCOUNT.MOVE PAYMENT_REFERENCE BACKUP CANDIDATE SET')
has_sale_line_ids = bool(Field.search([('model', '=', 'account.move.line'), ('name', '=', 'sale_line_ids')], limit=1))
has_payment_ref = bool(Field.search([('model', '=', 'account.move'), ('name', '=', 'payment_reference')], limit=1))
if not has_sale_line_ids or not has_payment_ref:
    lines.append('  FAIL required fields sale_line_ids=%s payment_reference=%s' % (has_sale_line_ids, has_payment_ref))
    problems = problems + 1

moves = Move.search([('move_type', 'in', ['out_invoice', 'out_refund'])], order='id')
payload_lines = []
exact_one = 0
zero_source = 0
multi_source = 0
would_change = 0
already_match = 0
source_no_digits = 0
examples = []
zero_examples = []
multi_examples = []

for mv in moves:
    source_orders = Order.browse()
    if has_sale_line_ids:
        source_orders = source_orders | mv.invoice_line_ids.mapped('sale_line_ids.order_id')
    origin = mv.invoice_origin or ''
    if origin:
        norm = origin.replace(';', ',').replace('\n', ',')
        pieces = norm.split(',')
        for pc in pieces:
            nm = pc.strip()
            if nm:
                found = Order.search([('name', '=', nm)], limit=1)
                if found:
                    source_orders = source_orders | found
    if len(source_orders) == 1:
        exact_one = exact_one + 1
        so = source_orders[0]
        raw = so.name or ''
        proposed = ''
        for ch in raw:
            if ch in DIGITS:
                proposed = proposed + ch
        if not proposed:
            source_no_digits = source_no_digits + 1
            if len(examples) < 25:
                examples.append('NO DIGITS move=%s id=%s source=%r current=%r' % (mv.name, mv.id, raw, mv.payment_reference or ''))
        cur = mv.payment_reference or ''
        if cur == proposed:
            already_match = already_match + 1
        else:
            would_change = would_change + 1
            if len(examples) < 25:
                examples.append('CHANGE move=%s id=%s state=%s source=%s current=%r proposed=%r residual=%s' % (
                    mv.name, mv.id, mv.state, raw, cur, proposed, mv.amount_residual
                ))
        payload_lines.append('%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s' % (
            mv.id, SEP, mv.name or '', SEP, mv.move_type or '', SEP, mv.state or '', SEP,
            so.id, SEP, raw, SEP, cur.replace('\n', '\\n').replace(SEP, ' '), SEP, proposed
        ))
    elif len(source_orders) == 0:
        zero_source = zero_source + 1
        if len(zero_examples) < 25:
            zero_examples.append('ZERO move=%s id=%s type=%s origin=%r current=%r' % (mv.name, mv.id, mv.move_type, origin, mv.payment_reference or ''))
    else:
        multi_source = multi_source + 1
        if len(multi_examples) < 25:
            multi_examples.append('MULTI move=%s id=%s sources=%s current=%r' % (
                mv.name, mv.id, ', '.join(source_orders.mapped('name')), mv.payment_reference or ''
            ))

payload = NL.join(payload_lines)
expected_keys.append(RP_PREFIX + 'moves.payment_reference.payload')
expected_keys.append(RP_PREFIX + 'moves.payment_reference.count_exact_one')
expected_keys.append(RP_PREFIX + 'moves.payment_reference.count_would_change')
expected_keys.append(RP_PREFIX + 'moves.payment_reference.count_zero_source')
expected_keys.append(RP_PREFIX + 'moves.payment_reference.count_multi_source')
expected_keys.append(RP_PREFIX + 'moves.payment_reference.count_source_no_digits')

lines.append('  customer moves scanned=%s' % len(moves))
lines.append('  exactly_one_source=%s zero_source=%s multi_source=%s source_no_digits=%s' % (exact_one, zero_source, multi_source, source_no_digits))
lines.append('  already_match=%s would_change=%s payload_len=%s' % (already_match, would_change, len(payload)))
if examples:
    lines.append('  sample exact-one changes/no-digits:')
    for ex in examples:
        lines.append('    %s' % ex)
if zero_examples:
    lines.append('  zero-source examples:')
    for ex in zero_examples:
        lines.append('    %s' % ex)
if multi_examples:
    lines.append('  multi-source examples:')
    for ex in multi_examples:
        lines.append('    %s' % ex)

# Keep D02-style safety: if future payment-reference tuning would refuse to guess,
# this restore-point action should surface the same blocker before taking a baseline.
if multi_source:
    lines.append('  FAIL: multiple-source moves exist. Future payment-reference action must not guess.')
    problems = problems + 1
if source_no_digits:
    lines.append('  FAIL: some exact-one source refs have no digits.')
    problems = problems + 1

# ---- Existing B02 restore point state ---------------------------------------
marker = bool(Param.get_param(RP_MARKER))
present = 0
missing = []
for key in expected_keys:
    if Param.search([('key', '=', key)], limit=1):
        present = present + 1
    else:
        missing.append(key)

state = 'ABSENT_READY'
if marker and missing:
    state = 'CORRUPT'
    problems = problems + 1
elif marker and (not missing):
    state = 'COMPLETE_PRESERVED'
elif (not marker) and present:
    state = 'ORPHAN'
    problems = problems + 1

lines.append('')
lines.append('F) RESTORE POINT STATE')
lines.append('  state=%s marker=%s present=%s expected=%s missing=%s' % (
    state, marker, present, len(expected_keys), len(missing)
))
if missing and len(missing) <= 15:
    for m in missing:
        lines.append('    missing=%s' % m)

if problems:
    lines.append('')
    lines.append('ABORT: %s problem(s). No writes. Fix before creating post-C02 restore point.' % problems)
    raise UserError(NL.join(lines)[:90000])

if state == 'COMPLETE_PRESERVED':
    lines.append('')
    lines.append('NO-OP: complete B02 post-C02 restore point already exists and will not be overwritten.')
    raise UserError(NL.join(lines)[:90000])

lines.append('')
lines.append('PLAN')
lines.append('  capture %s QWeb view arches' % len(views))
lines.append('  capture %s report actions' % len(reports))
lines.append('  capture %s paperformats from report actions' % len(paperformats))
lines.append('  capture %s exact-one-source account.move payment_reference rows' % exact_one)
lines.append('  zero-source legacy moves are reported but not included in payment-reference update scope')
lines.append('  no business records changed by this action')

if DRY_RUN or CONFIRM != CONFIRM_TOKEN:
    lines.append('')
    lines.append('DRY RUN — no parameters written.')
    lines.append('Apply with DRY_RUN=False and CONFIRM=%s.' % CONFIRM_TOKEN)
    raise UserError(NL.join(lines)[:90000])

# ---- Build restore point key/value set --------------------------------------
rp_values = []

rp_values.append((RP_PREFIX + 'meta.created_by_action', 'B02'))
rp_values.append((RP_PREFIX + 'meta.purpose', 'post-C02 validated current baseline before RI/DPI/DN follow-up changes'))
rp_values.append((RP_PREFIX + 'meta.requires_b01_marker', RP_MARKER_B01))
rp_values.append((RP_PREFIX + 'meta.requires_c02_marker', C02_MARKER))

for vv in views:
    token = vv[0]
    key = vv[1]
    v = vv[2]
    arch = vv[3]
    rp_values.append((RP_PREFIX + 'view.' + token + '.id', str(v.id)))
    rp_values.append((RP_PREFIX + 'view.' + token + '.key', key))
    rp_values.append((RP_PREFIX + 'view.' + token + '.arch', arch))
    rp_values.append((RP_PREFIX + 'view.' + token + '.write_date', str(v.write_date)))

for rr in reports:
    token = rr[0]
    r = rr[1]
    gs = []
    for g in r.groups_id:
        gs.append(str(g.id))
    gs.sort()
    multi_val = '0'
    if 'multi' in r._fields:
        if r.multi:
            multi_val = '1'
    rp_values.append((RP_PREFIX + 'report.' + token + '.id', str(r.id)))
    rp_values.append((RP_PREFIX + 'report.' + token + '.name', r.name or ''))
    rp_values.append((RP_PREFIX + 'report.' + token + '.model', r.model or ''))
    rp_values.append((RP_PREFIX + 'report.' + token + '.report_type', r.report_type or ''))
    rp_values.append((RP_PREFIX + 'report.' + token + '.report_name', r.report_name or ''))
    rp_values.append((RP_PREFIX + 'report.' + token + '.report_file', r.report_file or ''))
    rp_values.append((RP_PREFIX + 'report.' + token + '.binding_type', r.binding_type or ''))
    rp_values.append((RP_PREFIX + 'report.' + token + '.binding_view_types', r.binding_view_types or ''))
    rp_values.append((RP_PREFIX + 'report.' + token + '.binding_model_id', str(r.binding_model_id.id if r.binding_model_id else 0)))
    rp_values.append((RP_PREFIX + 'report.' + token + '.paperformat_id', str(r.paperformat_id.id if r.paperformat_id else 0)))
    rp_values.append((RP_PREFIX + 'report.' + token + '.groups_ids', ','.join(gs)))
    rp_values.append((RP_PREFIX + 'report.' + token + '.print_report_name', r.print_report_name or ''))
    rp_values.append((RP_PREFIX + 'report.' + token + '.attachment_use', '1' if r.attachment_use else '0'))
    rp_values.append((RP_PREFIX + 'report.' + token + '.attachment', r.attachment or ''))
    rp_values.append((RP_PREFIX + 'report.' + token + '.multi', multi_val))

for pp in paperformats:
    token = pp[0]
    pf = pp[1]
    rp_values.append((RP_PREFIX + 'paperformat.' + token + '.id', str(pf.id)))
    rp_values.append((RP_PREFIX + 'paperformat.' + token + '.name', pf.name or ''))
    rp_values.append((RP_PREFIX + 'paperformat.' + token + '.format', pf.format or ''))
    rp_values.append((RP_PREFIX + 'paperformat.' + token + '.orientation', pf.orientation or ''))
    rp_values.append((RP_PREFIX + 'paperformat.' + token + '.margin_top', str(pf.margin_top)))
    rp_values.append((RP_PREFIX + 'paperformat.' + token + '.margin_bottom', str(pf.margin_bottom)))
    rp_values.append((RP_PREFIX + 'paperformat.' + token + '.margin_left', str(pf.margin_left)))
    rp_values.append((RP_PREFIX + 'paperformat.' + token + '.margin_right', str(pf.margin_right)))
    rp_values.append((RP_PREFIX + 'paperformat.' + token + '.header_line', '1' if pf.header_line else '0'))
    rp_values.append((RP_PREFIX + 'paperformat.' + token + '.header_spacing', str(pf.header_spacing)))
    rp_values.append((RP_PREFIX + 'paperformat.' + token + '.dpi', str(pf.dpi)))
    rp_values.append((RP_PREFIX + 'paperformat.' + token + '.disable_shrinking', '1' if pf.disable_shrinking else '0'))
    rp_values.append((RP_PREFIX + 'paperformat.' + token + '.page_width', str(pf.page_width)))
    rp_values.append((RP_PREFIX + 'paperformat.' + token + '.page_height', str(pf.page_height)))
    rp_values.append((RP_PREFIX + 'paperformat.' + token + '.default', '1' if pf.default else '0'))

rp_values.append((RP_PREFIX + 'moves.payment_reference.payload', payload))
rp_values.append((RP_PREFIX + 'moves.payment_reference.count_exact_one', str(exact_one)))
rp_values.append((RP_PREFIX + 'moves.payment_reference.count_would_change', str(would_change)))
rp_values.append((RP_PREFIX + 'moves.payment_reference.count_zero_source', str(zero_source)))
rp_values.append((RP_PREFIX + 'moves.payment_reference.count_multi_source', str(multi_source)))
rp_values.append((RP_PREFIX + 'moves.payment_reference.count_source_no_digits', str(source_no_digits)))

for kv in rp_values:
    Param.set_param(kv[0], kv[1])
Param.set_param(RP_MARKER, '1')

readback_fail = 0
for kv in rp_values:
    p = Param.search([('key', '=', kv[0])], limit=1)
    if (not p) or ((p.value or '') != kv[1]):
        lines.append('READ-BACK FAIL key=%s' % kv[0])
        readback_fail = readback_fail + 1
if Param.get_param(RP_MARKER) != '1':
    lines.append('READ-BACK FAIL marker')
    readback_fail = readback_fail + 1
if readback_fail:
    raise UserError((NL.join(lines) + NL + 'READ-BACK FAILED count=%s; transaction rolled back.' % readback_fail)[:90000])

lines.append('')
lines.append('RESTORE POINT CREATED: B02 post-C02 current baseline captured; exact parameter read-back PASS.')
lines.append('Captured: commercial Q/SO/PF, VAT/RI-DPI, Delivery Note 2026, report actions, paperformats, and exact-one-source payment references.')
text = NL.join(lines)[:90000]
Param.set_param(OUTPUT_KEY, text)
out = Param.search([('key', '=', OUTPUT_KEY)], limit=1)
action = {
    'type': 'ir.actions.act_window',
    'name': 'B02 BARANI L4 post-C02 restore point result',
    'res_model': 'ir.config_parameter',
    'view_mode': 'form',
    'res_id': out.id,
    'target': 'current',
}
