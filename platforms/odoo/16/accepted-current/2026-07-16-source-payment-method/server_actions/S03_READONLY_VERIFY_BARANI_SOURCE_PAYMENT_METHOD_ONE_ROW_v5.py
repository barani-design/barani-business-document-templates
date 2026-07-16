# VERSION: v5 — corrected 10pt seven-field width-map verification
# VERSION: v3 with S01A Customer Ref. wrap verification
# ============================================================================
# ACTION NAME : S03 READ-ONLY — Verify BARANI Source / Payment Method alignment
# MODEL       : Module (ir.module.module) recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
#
# READ-ONLY
#   Verifies the Q/SO/PF one-row layout, RI/DPI/CN Source normalization,
#   historical Payment Reference fallback, and report-routing no-drift.
# ============================================================================

PAGE = 1
PAGE_SIZE = 30000

S00_MARKER = 'barani.source_method.s00.restore.marker'
S01_MARKER = 'barani.source_method.s01.commercial.marker'
S02_MARKER = 'barani.source_method.s02.vat.marker'
S01A_MARKER = 'barani.source_method.s01a.customer_ref_wrap.marker'
S01B_MARKER = 'barani.source_method.s01b.metadata_10pt.marker'
PREFIX = 'barani.source_method.s00.restore.'

COMM_KEY = 'barani_commercial.report_saleorder_document'
VAT_KEY = 'barani_vat.report_invoice_document_vat'

NL = chr(10)

Param = env['ir.config_parameter'].sudo()
View = env['ir.ui.view'].sudo().with_context(lang=None, active_test=False)
Report = env['ir.actions.report'].sudo()

lines = []
lines.append('S03 READ-ONLY — Verify BARANI Source / Payment Method alignment')
lines.append('READ-ONLY:YES PAGE=%s PAGE_SIZE=%s' % (PAGE, PAGE_SIZE))
lines.append('No writes or report rendering.')
lines.append('Verifier v5: corrects stale v4 assertion that still expected the removed 8.5pt dense font.')
lines.append('')

problems = 0
warnings = 0

for marker, label in [
    (S00_MARKER, 'S00'),
    (S01_MARKER, 'S01'),
    (S01A_MARKER, 'S01A'),
    (S01B_MARKER, 'S01B'),
    (S02_MARKER, 'S02'),
]:
    ok = Param.get_param(marker) == '1'
    lines.append('%s marker: %s' % (label, 'PASS' if ok else 'FAIL'))
    if not ok:
        problems = problems + 1

lines.append('')
lines.append('A) COMMERCIAL Q/SO/PF TEMPLATE')

comm_rs = View.search([('key', '=', COMM_KEY), ('type', '=', 'qweb')], limit=2)
if len(comm_rs) != 1:
    lines.append('  FAIL: commercial view count=%s expected=1' % len(comm_rs))
    problems = problems + 1
else:
    arch = comm_rs[0].arch_db or ''
    checks = [
        ('Source field exactly once', arch.count('<div class="mb-2" name="source">') == 1),
        ('Source is SO-normalized', 'barani_source_so' in arch and "('SO' + barani_source_suffix)" in arch),
        ('single row forced', 'flex-wrap:nowrap' in arch and 'barani_commercial_meta' in arch),
        ('Customer Ref. wraps only inside its own cell', 'white-space:normal !important' in arch and 'word-wrap:break-word' in arch),
        ('Customer Ref. has right padding', 'padding-right:14px' in arch),
        ('commercial metadata uses standard 10pt', 'font-size:10pt; line-height:1.15' in arch),
        ('dense case does not shrink text', '#informations.barani_meta_7 { font-size:10pt; }' in arch and 'font-size:8.5pt' not in arch),
        ('Document Date label is consistent', arch.count('<strong>Document Date</strong>') == 1),
        ('7-field 10pt width map',
         'barani_meta_7' in arch
         and '#informations.barani_meta_7 { font-size:10pt; }' in arch
         and 'div[name="doc_date"] { flex:0 0 13%;' in arch
         and 'div[name="validity_date"] { flex:0 0 12.5%;' in arch
         and 'div[name="customer_ref"] { flex:0 0 12%;' in arch
         and 'div[name="payment_terms"] { flex:0 0 20%;' in arch
         and 'div[name="source"] { flex:0 0 12%;' in arch
         and 'div[name="barani_payment_reference_info"] { flex:0 0 16.5%;' in arch
         and 'div[name="payment_method"] { flex:0 0 14%;' in arch),
        ('6-field validity map', 'barani_meta_6v' in arch),
        ('6-field customer-ref map', 'barani_meta_6c' in arch),
        ('5-field PF map', 'barani_meta_5' in arch),
        ('Payment Method label', '<strong>Payment Method</strong>' in arch),
        ('old preferred label absent', 'Preferred Payment Method' not in arch),
        ('Wire transfer retained', '>Wire transfer<' in arch),
        ('historical Payment Reference fallback retained', 'barani_vs or \'N/A\'' in arch),
        ('10-column product table retained', 'barani_discount_col_fixed' in arch and 'barani_commercial_vat_rate_col_final' in arch),
        ('no DDS dependency', 'dds_' not in arch.lower()),
    ]
    for label, ok in checks:
        lines.append('  %s: %s' % (label, 'PASS' if ok else 'FAIL'))
        if not ok:
            problems = problems + 1

lines.append('')
lines.append('B) RI/DPI/CREDIT NOTE TEMPLATE')

vat_rs = View.search([('key', '=', VAT_KEY), ('type', '=', 'qweb')], limit=2)
if len(vat_rs) != 1:
    lines.append('  FAIL: VAT view count=%s expected=1' % len(vat_rs))
    problems = problems + 1
else:
    arch = vat_rs[0].arch_db or ''
    checks = [
        ('linked Sales Order source lookup', "mapped('sale_line_ids.order_id')" in arch),
        ('single-source guard', 'len(barani_source_orders) == 1' in arch),
        ('SO-normalized Source', 'barani_source_display' in arch and "('SO' + barani_source_order_name[1:])" in arch),
        ('Source field uses normalized display', 't-esc="barani_source_display"' in arch),
        ('Payment Method label', '<strong>Payment Method</strong>' in arch),
        ('old preferred label absent', 'Preferred Payment Method' not in arch),
        ('Wire transfer retained', '>Wire transfer<' in arch),
        ('historical Payment Reference fallback retained', 'barani_payment_ref_raw' in arch and 'barani_pdf_payment_ref' in arch),
        ('credit-note original reference retained', 'barani_credit_original_payment_ref' in arch and 'Original Invoice' in arch),
        ('down-payment logic retained', 'barani_down_payment_reconciliation_table' in arch),
        ('10-column invoice table retained', 'barani_discount_col_fixed' in arch and 'barani_vat_rate_col_final' in arch),
        ('no DDS dependency', 'dds_' not in arch.lower()),
    ]
    for label, ok in checks:
        lines.append('  %s: %s' % (label, 'PASS' if ok else 'FAIL'))
        if not ok:
            problems = problems + 1

lines.append('')
lines.append('C) REPORT ROUTING / PREVIEW NO-DRIFT')

report_specs = [
    ('sale_qso', 'sale.action_report_saleorder'),
    ('sale_pf', 'sale.action_report_pro_forma_invoice'),
    ('invoice', 'account.account_invoices'),
    ('invoice_no_payment', 'account.account_invoices_without_payment'),
]
for token, xid in report_specs:
    rec = env.ref(xid, raise_if_not_found=False)
    current = ''
    if rec:
        current = '|'.join([
            str(rec.id),
            rec.name or '',
            rec.report_type or '',
            rec.report_name or '',
            rec.report_file or '',
            str(rec.binding_model_id.id if rec.binding_model_id else 0),
            str(rec.paperformat_id.id if rec.paperformat_id else 0),
        ])
    backup = Param.get_param(PREFIX + 'report.' + token + '.signature') or ''
    ok = bool(rec) and current == backup
    lines.append('  %s: %s' % (xid, 'PASS' if ok else 'FAIL'))
    if not ok:
        problems = problems + 1

preview_rs = Report.search([
    ('model', '=', 'account.move'),
    ('report_type', '=', 'qweb-html'),
    ('report_name', '=', VAT_KEY),
], limit=2)
preview_current = ''
if len(preview_rs) == 1:
    preview_current = '|'.join([
        str(preview_rs[0].id),
        preview_rs[0].name or '',
        preview_rs[0].report_type or '',
        preview_rs[0].report_name or '',
        str(preview_rs[0].binding_model_id.id if preview_rs[0].binding_model_id else 0),
        str(preview_rs[0].paperformat_id.id if preview_rs[0].paperformat_id else 0),
    ])
preview_backup = Param.get_param(PREFIX + 'report.preview.signature') or ''
preview_ok = len(preview_rs) == 1 and preview_current == preview_backup
lines.append('  BARANI invoice HTML Preview: %s' % ('PASS' if preview_ok else 'FAIL'))
if not preview_ok:
    problems = problems + 1

lines.append('')
lines.append('D) REQUIRED PDF ACCEPTANCE SET')
tests = [
    'Quotation with Valid Until, Immediate upon receipt, and no Customer Ref.',
    'Quotation or Sales Order with both Customer Ref. and Valid Until (densest 7-field case).',
    'Long Customer Ref. test: value wraps within its own cell and does not touch Payment Terms.',
    'Typography test: metadata labels and values match the normal 10pt document text; no reduced-font case.',
    'Confirmed Sales Order: Source must show SO/... and row must remain single-line.',
    'Pro-Forma: Source must show SO/... and Payment Method must show Wire transfer.',
    'Old Regular Invoice reprint: Source must show SO/...; Payment Reference fallback must remain correct.',
    'Old DPI reprint: Source must show SO/...; bank band and totals must remain correct.',
    'Credit Note: Original Invoice and Original Payment Reference must remain intact.',
    'Near-page-break commercial document: no metadata overlap and no table regression.',
]
for item in tests:
    lines.append('  [ ] ' + item)

lines.append('')
lines.append('SUMMARY problems=%s warnings=%s WRITE ACTIONS PERFORMED: NONE' % (problems, warnings))
if problems:
    lines.append('RESULT: FAIL — review before accepting.')
else:
    lines.append('RESULT: CONFIGURATION PASS — complete the PDF acceptance set.')

full = NL.join(lines)
if PAGE < 1 or PAGE_SIZE < 1000:
    raise UserError('ERROR: invalid PAGE/PAGE_SIZE')
start = (PAGE - 1) * PAGE_SIZE
end = min(start + PAGE_SIZE, len(full))
if start >= len(full) and PAGE > 1:
    raise UserError('ERROR: PAGE starts beyond output length=%s' % len(full))
more = end < len(full)
raise UserError(
    full[start:end]
    + NL + NL
    + 'PAGE %s | chars %s-%s of %s | MORE REMAINS: %s'
    % (PAGE, start, end, len(full), 'YES' if more else 'NO')
)
