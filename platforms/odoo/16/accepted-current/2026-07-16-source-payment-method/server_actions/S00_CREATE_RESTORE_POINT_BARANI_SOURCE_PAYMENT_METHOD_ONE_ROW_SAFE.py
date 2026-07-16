# ============================================================================
# ACTION NAME : S00 CREATE RESTORE POINT — BARANI Source / Payment Method SAFE
# MODEL       : Module (ir.module.module) recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
#
# PURPOSE
#   Capture the current accepted Q/SO/PF and RI/DPI/Credit Note QWeb bodies
#   before adding a one-row Source field and shortening the payment-method label.
#
# WRITES
#   Only ir.config_parameter restore metadata when DRY_RUN=False.
#
# NO TOUCH
#   Business records, report actions, Print menus, Preview routing, paperformats,
#   Delivery Note, stored Payment References, taxes, totals, or DDS fields.
# ============================================================================

DRY_RUN = True
CONFIRM = ''
CONFIRM_TOKEN = 'CREATE_BARANI_SOURCE_PAYMENT_METHOD_ONE_ROW_RESTORE_POINT_S00'

B02_MARKER = 'barani.l4.post_c02.restore_point.marker'
F01_MARKER = 'barani.future_ref_validity.f01.marker'
MARKER = 'barani.source_method.s00.restore.marker'
PREFIX = 'barani.source_method.s00.restore.'
OUTPUT_KEY = 'barani.source_method.s00.output'

COMM_KEY = 'barani_commercial.report_saleorder_document'
VAT_KEY = 'barani_vat.report_invoice_document_vat'

NL = chr(10)

Param = env['ir.config_parameter'].sudo()
View = env['ir.ui.view'].sudo().with_context(lang=None, active_test=False)
Report = env['ir.actions.report'].sudo()

lines = []
lines.append('S00 CREATE RESTORE POINT — BARANI Source / Payment Method SAFE')
lines.append('DRY_RUN=%s CONFIRM_OK=%s' % (DRY_RUN, CONFIRM == CONFIRM_TOKEN))
lines.append('Captures current commercial and VAT QWeb bodies plus routing signatures.')
lines.append('Writes only ir.config_parameter; business records and report routing remain untouched.')
lines.append('')

problems = 0
warnings = 0
values = []
expected = []

if Param.get_param(B02_MARKER) != '1':
    lines.append('FAIL: B02 current-template restore marker missing.')
    problems = problems + 1
else:
    lines.append('PRECHECK B02 marker: PASS')

lines.append('PRECHECK future Payment Ref / Valid Until marker: %s' % (
    'PASS' if Param.get_param(F01_MARKER) == '1' else 'NOT_PRESENT_INFORMATIONAL'
))

lines.append('')
lines.append('A) QWEB BODY CAPTURE')

view_specs = [
    ('commercial', COMM_KEY),
    ('vat', VAT_KEY),
]
view_rows = {}

for token, key in view_specs:
    rs = View.search([('key', '=', key), ('type', '=', 'qweb')], limit=2)
    if len(rs) != 1:
        lines.append('  FAIL token=%s key=%s found=%s expected=1' % (token, key, len(rs)))
        problems = problems + 1
        continue
    rec = rs[0]
    arch = rec.arch_db or ''
    view_rows[token] = rec
    lines.append(
        '  token=%s id=%s key=%s name=%r len=%s active=%s standalone=%s write_date=%s'
        % (token, rec.id, key, rec.name or '', len(arch), bool(rec.active), not bool(rec.inherit_id), rec.write_date)
    )
    if rec.inherit_id:
        problems = problems + 1

    for suffix, value in [
        ('id', str(rec.id)),
        ('key', rec.key or ''),
        ('name', rec.name or ''),
        ('active', '1' if rec.active else '0'),
        ('arch', arch),
    ]:
        pkey = PREFIX + 'view.' + token + '.' + suffix
        expected.append(pkey)
        values.append((pkey, value))

if 'commercial' in view_rows:
    arch = view_rows['commercial'].arch_db or ''
    checks = [
        ('commercial current metadata block', 'barani_meta_optional_cols' in arch and 'barani_meta_wide_class' in arch),
        ('commercial current Preferred Payment Method', 'Preferred Payment Method' in arch),
        ('commercial fixed Wire transfer', '>Wire transfer<' in arch),
        ('commercial source not yet installed', 'barani_source_so' not in arch and 'barani_commercial_meta' not in arch),
        ('commercial payment fallback retained', 'barani_vs' in arch),
        ('commercial fixed 10-column table retained', 'barani_discount_col_fixed' in arch and 'barani_commercial_vat_rate_col_final' in arch),
        ('commercial no DDS dependency', 'dds_' not in arch.lower()),
    ]
    for label, ok in checks:
        lines.append('  %s: %s' % (label, 'PASS' if ok else 'FAIL'))
        if not ok:
            problems = problems + 1

if 'vat' in view_rows:
    arch = view_rows['vat'].arch_db or ''
    checks = [
        ('VAT current Source from invoice_origin', 't-field="o.invoice_origin"' in arch),
        ('VAT current Preferred Payment Method', 'Preferred Payment Method' in arch),
        ('VAT fixed Wire transfer', '>Wire transfer<' in arch),
        ('VAT source normalization not yet installed', 'barani_source_display' not in arch),
        ('VAT historical payment fallback retained', 'barani_pdf_payment_ref' in arch),
        ('VAT credit-note metadata retained', 'barani_credit_original_payment_ref' in arch and 'Original Invoice' in arch),
        ('VAT fixed 10-column table retained', 'barani_discount_col_fixed' in arch and 'barani_vat_rate_col_final' in arch),
        ('VAT no DDS dependency', 'dds_' not in arch.lower()),
    ]
    for label, ok in checks:
        lines.append('  %s: %s' % (label, 'PASS' if ok else 'FAIL'))
        if not ok:
            problems = problems + 1

lines.append('')
lines.append('B) ACCEPTED REPORT ROUTING / PREVIEW SIGNATURES')

report_specs = [
    ('sale_qso', 'sale.action_report_saleorder', 'barani_commercial.report_saleorder'),
    ('sale_pf', 'sale.action_report_pro_forma_invoice', 'barani_commercial.report_saleorder_proforma'),
    ('invoice', 'account.account_invoices', VAT_KEY),
    ('invoice_no_payment', 'account.account_invoices_without_payment', VAT_KEY),
]

for token, xid, expected_report in report_specs:
    rec = env.ref(xid, raise_if_not_found=False)
    ok = bool(rec) and rec.report_name == expected_report
    lines.append(
        '  %s: %s id=%s report=%r binding=%r paper=%s'
        % (
            xid,
            'PASS' if ok else 'FAIL',
            rec.id if rec else 0,
            rec.report_name if rec else '',
            rec.binding_model_id.model if rec and rec.binding_model_id else '',
            rec.paperformat_id.id if rec and rec.paperformat_id else 0,
        )
    )
    if not ok:
        problems = problems + 1
    if rec:
        signature = '|'.join([
            str(rec.id),
            rec.name or '',
            rec.report_type or '',
            rec.report_name or '',
            rec.report_file or '',
            str(rec.binding_model_id.id if rec.binding_model_id else 0),
            str(rec.paperformat_id.id if rec.paperformat_id else 0),
        ])
        pkey = PREFIX + 'report.' + token + '.signature'
        expected.append(pkey)
        values.append((pkey, signature))

preview_rs = Report.search([
    ('model', '=', 'account.move'),
    ('report_type', '=', 'qweb-html'),
    ('report_name', '=', VAT_KEY),
], limit=2)
preview_ok = len(preview_rs) == 1 and not preview_rs[0].binding_model_id
lines.append(
    '  BARANI invoice HTML Preview: %s count=%s id=%s'
    % ('PASS' if preview_ok else 'FAIL', len(preview_rs), preview_rs[0].id if len(preview_rs) == 1 else 0)
)
if not preview_ok:
    problems = problems + 1
elif len(preview_rs) == 1:
    pkey = PREFIX + 'report.preview.signature'
    expected.append(pkey)
    values.append((
        pkey,
        '|'.join([
            str(preview_rs[0].id),
            preview_rs[0].name or '',
            preview_rs[0].report_type or '',
            preview_rs[0].report_name or '',
            str(preview_rs[0].binding_model_id.id if preview_rs[0].binding_model_id else 0),
            str(preview_rs[0].paperformat_id.id if preview_rs[0].paperformat_id else 0),
        ])
    ))

for suffix, value in [
    ('meta.action', 'S00'),
    ('meta.scope', 'commercial + VAT QWeb display-only Source / Payment Method'),
]:
    pkey = PREFIX + suffix
    expected.append(pkey)
    values.append((pkey, value))

marker = Param.get_param(MARKER) or ''
present = 0
missing = []
for key in expected:
    row = Param.search([('key', '=', key)], limit=1)
    if row:
        present = present + 1
    else:
        missing.append(key)

lines.append('')
lines.append('C) RESTORE POINT STATE')
if marker == '1' and not missing:
    state = 'COMPLETE_PRESERVED'
elif marker or present:
    state = 'PARTIAL_INVALID'
    problems = problems + 1
else:
    state = 'ABSENT_READY'
lines.append(
    '  state=%s marker=%r present=%s expected=%s missing=%s'
    % (state, marker, present, len(expected), len(missing))
)

if problems:
    lines.append('')
    lines.append('ERROR: %s preflight problem(s); no writes performed.' % problems)
    raise UserError(NL.join(lines)[:90000])

if state == 'COMPLETE_PRESERVED':
    lines.append('')
    lines.append('NO-OP: complete S00 restore point already exists and will not be overwritten.')
    raise UserError(NL.join(lines)[:90000])

lines.append('')
lines.append('PLAN')
lines.append('  capture exact commercial and VAT QWeb bytes')
lines.append('  capture standard report-routing and HTML Preview signatures')
lines.append('  write only ir.config_parameter restore keys')
lines.append('  no business records, report actions, paperformats, or QWeb views changed')

if DRY_RUN or CONFIRM != CONFIRM_TOKEN:
    lines.append('')
    lines.append('DRY RUN — no parameters written.')
    lines.append('Apply with DRY_RUN=False and CONFIRM=%s.' % CONFIRM_TOKEN)
    raise UserError(NL.join(lines)[:90000])

for key, value in values:
    Param.set_param(key, value)
Param.set_param(MARKER, '1')

readback_fail = 0
for key, value in values:
    row = Param.search([('key', '=', key)], limit=1)
    if not row or (row.value or '') != value:
        lines.append('READ-BACK FAIL key=%s' % key)
        readback_fail = readback_fail + 1
if Param.get_param(MARKER) != '1':
    lines.append('READ-BACK FAIL marker')
    readback_fail = readback_fail + 1

if readback_fail:
    raise UserError((NL.join(lines) + NL + 'READ-BACK FAILED; transaction rolled back.')[:90000])

lines.append('')
lines.append('S00 COMPLETE: Source / Payment Method QWeb restore point created; exact read-back PASS.')
text = NL.join(lines)[:90000]
Param.set_param(OUTPUT_KEY, text)
out = Param.search([('key', '=', OUTPUT_KEY)], limit=1)
action = {
    'type': 'ir.actions.act_window',
    'name': 'S00 BARANI Source / Payment Method restore result',
    'res_model': 'ir.config_parameter',
    'view_mode': 'form',
    'res_id': out.id,
    'target': 'current',
}
