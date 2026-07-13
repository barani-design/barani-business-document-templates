# ============================================================================
# ACTION NAME : E01.1 READ-ONLY EXPORT — BARANI L4 post-C02 current templates SANITIZED for GitHub SAFE
# MODEL       : Module (ir.module.module) recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
# CREATE AT   : Settings -> Technical -> Actions -> Server Actions.
# VISIBILITY  : Maintenance-only. Run from the Server Action form.
# PURPOSE     : Exports the latest current Odoo QWeb templates and report metadata
#               after the validated C02 commercial date-format hotfix and B02
#               post-C02 restore point.
#
# WHY E01.1    : E01 correctly confirmed B02 equality but aborted because its
#               Delivery Note marker was too strict for the current DN template.
#               E01.1 treats B02 equality as the hard DN identity gate and uses
#               DN markers as warnings only. It also emits PUBLIC-SANITIZED file
#               blocks so live bank identifiers are not copied into GitHub source.
#
# OUTPUT      : Paged UserError text only. Copy all pages back into the chat so
#               a GitHub package can be assembled from real live Odoo templates.
#               This action creates no files in Odoo and writes no database records.
#
# SCOPE       : current BARANI commercial Q/SO/PF, VAT/RI-DPI, and Delivery Note
#               2026 QWeb views + related report actions + paperformats.
#
# NO EXPORT   : customer PDFs, business records, account.move payment refs,
#               ir.config_parameter restore payloads, invoices, sales orders,
#               delivery orders, attachments, bank/account records.
#
# SAFETY      : read-only; refuses to output templates if B02 restore marker is
#               missing or if current QWeb arches no longer match the B02
#               post-C02 baseline captured immediately before this export.
#
# SANITIZER   : Output QWeb arches are sanitized before FILE_BEGIN emission.
#               The sanitizer builds exact replacement candidates from live
#               res.partner.bank / res.bank records and from the EXW literal
#               embedded in the QWeb expression. It reports only counts/tokens,
#               not the private values themselves.
#
# safe_eval   : no import/def/lambda/comprehension/with/while/try/getattr/hasattr/
#               setattr/eval/exec/open in executable code.
# ============================================================================

PAGE = 1
PAGE_SIZE = 50000
SANITIZE_FOR_PUBLIC_GITHUB = True

RP_MARKER_B02 = 'barani.l4.post_c02.restore_point.marker'
RP_PREFIX_B02 = 'barani.l4.post_c02.restore_point.'
C02_MARKER = 'barani.l4.c02.date_format.comm.backup.marker'
NL = chr(10)

COMM_BODY_KEY = 'barani_commercial.report_saleorder_document'
COMM_LAYOUT_KEY = 'barani_commercial.external_layout_standard_titled'
COMM_QSO_KEY = 'barani_commercial.report_saleorder'
COMM_PF_KEY = 'barani_commercial.report_saleorder_proforma'
VAT_BODY_KEY = 'barani_vat.report_invoice_document_vat'
VAT_LAYOUT_KEY = 'barani_vat.external_layout_standard_titled'
DN_BODY_KEY = 'barani_delivery.report_delivery_note_2026'
DN_LAYOUT_KEY = 'barani_delivery.external_layout_delivery_2026'

Param = env['ir.config_parameter'].sudo()
View = env['ir.ui.view'].sudo().with_context(lang=None)
Rep = env['ir.actions.report'].sudo().with_context(lang=None)
BankAcc = env['res.partner.bank'].sudo().with_context(active_test=False)

lines = []
lines.append('E01.1 READ-ONLY EXPORT — BARANI L4 post-C02 current templates SANITIZED for GitHub SAFE')
lines.append('READ-ONLY:YES PAGE=%s PAGE_SIZE=%s SANITIZE_FOR_PUBLIC_GITHUB=%s' % (PAGE, PAGE_SIZE, SANITIZE_FOR_PUBLIC_GITHUB))
lines.append('Exports current QWeb templates only after B02 equality check; no business records or restore payloads are exported.')
lines.append('')

problems = 0
if Param.get_param(C02_MARKER) != '1':
    lines.append('FAIL: C02 marker missing: %s' % C02_MARKER)
    problems = problems + 1
else:
    lines.append('PRECHECK C02 marker: PASS')

if Param.get_param(RP_MARKER_B02) != '1':
    lines.append('FAIL: B02 post-C02 restore marker missing: %s' % RP_MARKER_B02)
    problems = problems + 1
else:
    lines.append('PRECHECK B02 marker: PASS')

view_items = [
    ('comm_body', COMM_BODY_KEY, 'platforms/odoo/16/current_templates/qweb/commercial/report_saleorder_document.xml'),
    ('comm_layout', COMM_LAYOUT_KEY, 'platforms/odoo/16/current_templates/qweb/commercial/external_layout_standard_titled.xml'),
    ('comm_qso_wrapper', COMM_QSO_KEY, 'platforms/odoo/16/current_templates/qweb/commercial/report_saleorder.xml'),
    ('comm_pf_wrapper', COMM_PF_KEY, 'platforms/odoo/16/current_templates/qweb/commercial/report_saleorder_proforma.xml'),
    ('vat_body', VAT_BODY_KEY, 'platforms/odoo/16/current_templates/qweb/vat/report_invoice_document_vat.xml'),
    ('vat_layout', VAT_LAYOUT_KEY, 'platforms/odoo/16/current_templates/qweb/vat/external_layout_standard_titled.xml'),
    ('dn_body', DN_BODY_KEY, 'platforms/odoo/16/current_templates/qweb/delivery/report_delivery_note_2026.xml'),
    ('dn_layout', DN_LAYOUT_KEY, 'platforms/odoo/16/current_templates/qweb/delivery/external_layout_delivery_2026.xml'),
]

views = []
lines.append('')
lines.append('A) CURRENT VIEW DISCOVERY + B02 EQUALITY CHECK')
for vi in view_items:
    token = vi[0]
    key = vi[1]
    path = vi[2]
    rs = View.search([('key', '=', key), ('type', '=', 'qweb')], limit=2)
    if len(rs) != 1:
        lines.append('  FAIL view token=%s key=%s found=%s expected=1' % (token, key, len(rs)))
        problems = problems + 1
    else:
        v = rs[0]
        arch = v.arch_db or ''
        root_ok = arch.startswith('<t t-name="' + key + '"')
        standalone = not bool(v.inherit_id)
        b02_arch = Param.get_param(RP_PREFIX_B02 + 'view.' + token + '.arch') or ''
        b02_id = Param.get_param(RP_PREFIX_B02 + 'view.' + token + '.id') or ''
        b02_key = Param.get_param(RP_PREFIX_B02 + 'view.' + token + '.key') or ''
        b02_equal = (b02_arch == arch and b02_id == str(v.id) and b02_key == key)
        lines.append('  VIEW token=%s id=%s key=%s len=%s root_ok=%s standalone=%s b02_equal=%s write_date=%s' % (
            token, v.id, key, len(arch), root_ok, standalone, b02_equal, v.write_date
        ))
        if (not root_ok) or (not standalone):
            problems = problems + 1
        if not b02_equal:
            lines.append('    FAIL: current view no longer matches B02 restore point for token=%s. Do not export/push until reviewed.' % token)
            problems = problems + 1
        views.append((token, key, path, v, arch))

# Marker checks on key bodies. Commercial/VAT markers are hard checks; DN marker is warning because B02 equality is the hard DN identity gate.
comm_arch = ''
vat_arch = ''
dn_arch = ''
for vx in views:
    if vx[0] == 'comm_body':
        comm_arch = vx[4]
    if vx[0] == 'vat_body':
        vat_arch = vx[4]
    if vx[0] == 'dn_body':
        dn_arch = vx[4]

hard_checks = [
    ('commercial C02 month tuple present', 'barani_date_months' in comm_arch and 'JAN' in comm_arch and 'DEC' in comm_arch),
    ('commercial C02 document date marker present', 'barani_doc_date_display' in comm_arch),
    ('commercial C02 valid-until marker present', 'barani_valid_until_display' in comm_arch),
    ('commercial Payment Reference retained', 'Payment Reference' in comm_arch),
    ('commercial Preferred Payment Method retained', 'Preferred Payment Method' in comm_arch),
    ('commercial numeric VAT retained', 'barani_numeric_vat_rate_tax.amount' in comm_arch),
    ('commercial fixed discount retained', 'barani_discount_col_fixed' in comm_arch),
    ('VAT body still BARANI VAT family', 'barani_vat' in VAT_BODY_KEY and 'VAT' in vat_arch),
]

dn_marker_ok = ('barani_delivery_line_table' in dn_arch) or ('QR' in dn_arch) or ('barcode' in dn_arch) or ('Lot / Serial' in dn_arch) or ('lot_serial' in dn_arch)

lines.append('')
lines.append('B) CURRENT MARKER CHECKS')
for ck in hard_checks:
    lines.append('  %s: %s' % (ck[0], 'PASS' if ck[1] else 'FAIL'))
    if not ck[1]:
        problems = problems + 1
lines.append('  Delivery Note body marker retained: %s' % ('PASS' if dn_marker_ok else 'WARN'))
if not dn_marker_ok:
    lines.append('    WARN: DN marker not found by flexible scan, but export may continue when B02 equality is true for dn_body and dn_layout.')

# Build sanitizer replacements from bank records and dynamic EXW literal candidates.
sensitive_replacements = []
sensitive_count_candidates = 0
bank_accounts = BankAcc.search([])
for ba in bank_accounts:
    if ba.acc_number and len(ba.acc_number) > 3:
        sensitive_replacements.append((ba.acc_number, '__PUBLIC_PLACEHOLDER_RECEIVING_IBAN__'))
        sensitive_count_candidates = sensitive_count_candidates + 1
    if 'sanitized_acc_number' in ba._fields and ba.sanitized_acc_number and len(ba.sanitized_acc_number) > 3:
        sensitive_replacements.append((ba.sanitized_acc_number, '__PUBLIC_PLACEHOLDER_RECEIVING_ACCOUNT__'))
        sensitive_count_candidates = sensitive_count_candidates + 1
    if ba.bank_id:
        if 'bic' in ba.bank_id._fields and ba.bank_id.bic and len(ba.bank_id.bic) > 3:
            sensitive_replacements.append((ba.bank_id.bic, '__PUBLIC_PLACEHOLDER_RECEIVING_BIC__'))
            sensitive_count_candidates = sensitive_count_candidates + 1
        if ba.bank_id.name and len(ba.bank_id.name) > 3:
            sensitive_replacements.append((ba.bank_id.name, '__PUBLIC_PLACEHOLDER_RECEIVING_BANK_NAME__'))
            sensitive_count_candidates = sensitive_count_candidates + 1
        bank_street = ba.bank_id.street or ''
        bank_zip = ba.bank_id.zip or ''
        bank_city = ba.bank_id.city or ''
        bank_country = ba.bank_id.country.name if ba.bank_id.country else ''
        if bank_street and len(bank_street) > 3:
            sensitive_replacements.append((bank_street, '__PUBLIC_PLACEHOLDER_RECEIVING_BANK_STREET__'))
            sensitive_count_candidates = sensitive_count_candidates + 1
        bank_zip_city = (bank_zip + ' ' + bank_city).strip()
        if bank_zip_city and len(bank_zip_city) > 3:
            sensitive_replacements.append((bank_zip_city, '__PUBLIC_PLACEHOLDER_RECEIVING_BANK_CITY__'))
            sensitive_count_candidates = sensitive_count_candidates + 1
        bank_addr_1 = ''
        if bank_street and bank_zip_city and bank_country:
            bank_addr_1 = bank_street + ', ' + bank_zip_city + ', ' + bank_country
        if bank_addr_1 and len(bank_addr_1) > 3:
            sensitive_replacements.append((bank_addr_1, '__PUBLIC_PLACEHOLDER_RECEIVING_BANK_ADDRESS__'))
            sensitive_count_candidates = sensitive_count_candidates + 1

# Detect EXW default literal in commercial body expression without hardcoding the private value.
exw_marker = "' if barani_incoterm_code == 'EXW'"
idx_exw = comm_arch.find(exw_marker)
if idx_exw > 0:
    start_exw = comm_arch.rfind("'", 0, idx_exw)
    if start_exw >= 0:
        exw_val = comm_arch[start_exw + 1:idx_exw]
        if exw_val and len(exw_val) > 3:
            sensitive_replacements.append((exw_val, '__PUBLIC_PLACEHOLDER_EXW_DEFAULT_LOCATION__'))
            sensitive_count_candidates = sensitive_count_candidates + 1

# Public-source caution scan against raw arches, but do not print private values.
sensitive_hits = []
for sx in views:
    arch_s = sx[4]
    token_s = sx[0]
    hit_count = 0
    for sr in sensitive_replacements:
        if sr[0] and sr[0] in arch_s:
            hit_count = hit_count + 1
    if hit_count:
        sensitive_hits.append(token_s + ': %s sensitive literal(s) sanitized in export' % hit_count)

lines.append('')
lines.append('C) PUBLIC-SANITATION SCAN')
lines.append('  sanitizer candidate literals=%s' % sensitive_count_candidates)
if sensitive_hits:
    lines.append('  PASS/WARN: raw arches contained private literals; sanitized FILE_BEGIN output will use placeholders:')
    for sh in sensitive_hits:
        lines.append('    %s' % sh)
else:
    lines.append('  PASS: no sanitizer candidate literal appeared in the current QWeb arches.')

# Report actions.
report_items = [
    ('comm_qso', COMM_QSO_KEY),
    ('comm_pf', COMM_PF_KEY),
    ('vat', VAT_BODY_KEY),
    ('dn', DN_BODY_KEY),
]
reports = []
lines.append('')
lines.append('D) REPORT ACTION DISCOVERY')
for ri in report_items:
    token_r = ri[0]
    report_name = ri[1]
    rs_r = Rep.search([('report_name', '=', report_name)], limit=2)
    if len(rs_r) != 1:
        lines.append('  FAIL report token=%s report_name=%s found=%s expected=1' % (token_r, report_name, len(rs_r)))
        problems = problems + 1
    else:
        r = rs_r[0]
        groups = []
        for g in r.groups_id:
            groups.append(str(g.id))
        groups.sort()
        bm = r.binding_model_id.model if r.binding_model_id else ''
        pfn = r.paperformat_id.name if r.paperformat_id else ''
        lines.append('  REPORT token=%s id=%s name=%r model=%s report_name=%s binding_model=%s paper=%s groups=%s' % (
            token_r, r.id, r.name, r.model, r.report_name, bm, pfn, ','.join(groups)
        ))
        reports.append((token_r, r))

if problems:
    lines.append('')
    lines.append('ABORT: %s hard problem(s). No template file blocks emitted. Fix/review before GitHub export.' % problems)
    text_abort = NL.join(lines)
    total_abort = len(text_abort)
    pages_abort = int((total_abort + PAGE_SIZE - 1) / PAGE_SIZE)
    if PAGE < 1:
        PAGE = 1
    start_abort = (PAGE - 1) * PAGE_SIZE
    end_abort = start_abort + PAGE_SIZE
    out_abort = text_abort[start_abort:end_abort]
    out_abort = out_abort + NL + NL + 'PAGE %s/%s | TOTAL_CHARS=%s | MORE_REMAINS=%s' % (PAGE, pages_abort, total_abort, 'YES' if PAGE < pages_abort else 'NO')
    raise UserError(out_abort[:90000])

# Emit metadata and sanitized file blocks.
lines.append('')
lines.append('E) EXPORT FILE BLOCKS')
lines.append('Copy every page of this output back into the chat. FILE_BEGIN blocks are sanitized for public GitHub review.')
lines.append('')

lines.append('@@FILE_BEGIN: platforms/odoo/16/current_templates/README.md')
lines.append('# BARANI Odoo 16 current template export — post-C02 / B02 baseline')
lines.append('')
lines.append('Source: live Odoo ir.ui.view / ir.actions.report after C02 date-format hotfix and B02 restore point.')
lines.append('Safety: this export excludes customer PDFs, business records, account.move payment-reference payloads, and private ir.config_parameter restore values.')
lines.append('Sanitization: private bank/account and EXW-default literals in QWeb arches are replaced with public placeholders before this export is emitted.')
lines.append('Use: review/diff before publishing to a public repository.')
lines.append('')
lines.append('Included QWeb view keys:')
for vi2 in view_items:
    lines.append('- `%s` -> `%s`' % (vi2[1], vi2[2]))
lines.append('@@FILE_END')
lines.append('')

# View arch files, sanitized before output.
post_sanitize_hits = []
for vf in views:
    arch_out = vf[4]
    if SANITIZE_FOR_PUBLIC_GITHUB:
        for sr2 in sensitive_replacements:
            if sr2[0] and sr2[0] in arch_out:
                arch_out = arch_out.replace(sr2[0], sr2[1])
    # Verify no sanitizer candidate literal remains in this emitted arch.
    remain_count = 0
    for sr3 in sensitive_replacements:
        if sr3[0] and sr3[0] in arch_out:
            remain_count = remain_count + 1
    if remain_count:
        post_sanitize_hits.append(vf[0] + ': %s literal(s) remain' % remain_count)
    lines.append('@@FILE_BEGIN: ' + vf[2])
    lines.append(arch_out)
    lines.append('@@FILE_END')
    lines.append('')

# Report metadata file.
lines.append('@@FILE_BEGIN: platforms/odoo/16/current_templates/report_actions/report_actions_snapshot.txt')
for rp in reports:
    token_p = rp[0]
    rr = rp[1]
    groups_p = []
    for gg in rr.groups_id:
        groups_p.append(str(gg.id))
    groups_p.sort()
    lines.append('[%s]' % token_p)
    lines.append('id=%s' % rr.id)
    lines.append('name=%s' % (rr.name or ''))
    lines.append('model=%s' % (rr.model or ''))
    lines.append('report_type=%s' % (rr.report_type or ''))
    lines.append('report_name=%s' % (rr.report_name or ''))
    lines.append('report_file=%s' % (rr.report_file or ''))
    lines.append('binding_type=%s' % (rr.binding_type or ''))
    lines.append('binding_view_types=%s' % (rr.binding_view_types or ''))
    lines.append('binding_model=%s' % (rr.binding_model_id.model if rr.binding_model_id else ''))
    lines.append('paperformat=%s' % (rr.paperformat_id.name if rr.paperformat_id else ''))
    lines.append('groups_ids=%s' % ','.join(groups_p))
    lines.append('print_report_name=%s' % (rr.print_report_name or ''))
    lines.append('attachment_use=%s' % ('1' if rr.attachment_use else '0'))
    lines.append('attachment=%s' % (rr.attachment or ''))
    lines.append('')
lines.append('@@FILE_END')
lines.append('')

# Paperformat metadata file, only paperformats linked to reports.
lines.append('@@FILE_BEGIN: platforms/odoo/16/current_templates/report_actions/paperformats_snapshot.txt')
seen_pf_ids = []
for rp2 in reports:
    rr2 = rp2[1]
    pf2 = rr2.paperformat_id
    if pf2 and str(pf2.id) not in seen_pf_ids:
        seen_pf_ids.append(str(pf2.id))
        lines.append('[paperformat id=%s]' % pf2.id)
        lines.append('name=%s' % (pf2.name or ''))
        lines.append('format=%s' % (pf2.format or ''))
        lines.append('orientation=%s' % (pf2.orientation or ''))
        lines.append('margin_top=%s' % pf2.margin_top)
        lines.append('margin_bottom=%s' % pf2.margin_bottom)
        lines.append('margin_left=%s' % pf2.margin_left)
        lines.append('margin_right=%s' % pf2.margin_right)
        lines.append('header_line=%s' % ('1' if pf2.header_line else '0'))
        lines.append('header_spacing=%s' % pf2.header_spacing)
        lines.append('dpi=%s' % pf2.dpi)
        lines.append('disable_shrinking=%s' % ('1' if pf2.disable_shrinking else '0'))
        lines.append('page_width=%s' % pf2.page_width)
        lines.append('page_height=%s' % pf2.page_height)
        lines.append('default=%s' % ('1' if pf2.default else '0'))
        lines.append('')
lines.append('@@FILE_END')
lines.append('')

lines.append('F) SANITIZATION READ-BACK')
if post_sanitize_hits:
    lines.append('  FAIL: sanitizer candidate literals remain in emitted output:')
    for ps in post_sanitize_hits:
        lines.append('    %s' % ps)
else:
    lines.append('  PASS: no sanitizer candidate literal remains in emitted QWeb file blocks.')
lines.append('')
lines.append('E01.1 COMPLETE: sanitized FILE_BEGIN blocks emitted from live B02-matching templates.')

text = NL.join(lines)
full_len = len(text)
pages = int((full_len + PAGE_SIZE - 1) / PAGE_SIZE)
if pages < 1:
    pages = 1
if PAGE < 1:
    PAGE = 1
start = (PAGE - 1) * PAGE_SIZE
end = start + PAGE_SIZE
out = text[start:end]
out = out + NL + NL + 'PAGE %s/%s | TOTAL_CHARS=%s | MORE_REMAINS=%s' % (PAGE, pages, full_len, 'YES' if PAGE < pages else 'NO')
raise UserError(out[:90000])
