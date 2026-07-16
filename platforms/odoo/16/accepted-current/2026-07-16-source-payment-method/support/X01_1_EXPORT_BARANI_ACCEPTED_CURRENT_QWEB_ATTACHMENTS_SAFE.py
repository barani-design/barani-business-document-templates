# ============================================================================
# ACTION NAME : X01.1 EXPORT — BARANI accepted-current QWeb attachments SAFE
# MODEL       : Module (ir.module.module) recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
#
# PURPOSE
#   Export the exact current live QWeb bodies as separate downloadable
#   attachments because Odoo Server Action safe_eval forbids imports and
#   context-manager opcodes needed by an in-memory ZIP implementation.
#
# OUTPUT
#   1. Commercial Q/SO/PF QWeb XML attachment.
#   2. VAT RI/DPI/Credit Note QWeb XML attachment.
#   3. Plain-text metadata/checksum attachment.
#
# WRITES
#   Creates only the three technical ir.attachment records after confirmation.
#
# NO TOUCH
#   QWeb views, business records, report actions, Print menus, Preview routing,
#   paperformats, Delivery Note, stored Payment References, taxes, totals, DDS.
# ============================================================================

CONFIRM = ''
CONFIRM_TOKEN = 'EXPORT_BARANI_ACCEPTED_CURRENT_QWEB_ATTACHMENTS_X01_1'

COMM_KEY = 'barani_commercial.report_saleorder_document'
VAT_KEY = 'barani_vat.report_invoice_document_vat'

REQUIRED_MARKERS = [
    ('barani.source_method.s00.restore.marker', 'S00'),
    ('barani.source_method.s01.commercial.marker', 'S01'),
    ('barani.source_method.s01a.customer_ref_wrap.marker', 'S01A'),
    ('barani.source_method.s01b.metadata_10pt.marker', 'S01B'),
    ('barani.source_method.s02.vat.marker', 'S02'),
]

COMM_FILENAME = 'BARANI_Q_SO_PF_ACCEPTED_CURRENT_QWEB_2026-07-16.xml'
VAT_FILENAME = 'BARANI_RI_DPI_CN_ACCEPTED_CURRENT_QWEB_2026-07-16.xml'
META_FILENAME = 'BARANI_SOURCE_PAYMENT_METHOD_ACCEPTED_CURRENT_METADATA_2026-07-16.txt'

NL = chr(10)

Param = env['ir.config_parameter'].sudo()
View = env['ir.ui.view'].sudo().with_context(lang=None, active_test=False)
Attachment = env['ir.attachment'].sudo()

lines = []
lines.append('X01.1 EXPORT — BARANI accepted-current QWeb attachments SAFE')
lines.append('CONFIRM_OK=%s' % (CONFIRM == CONFIRM_TOKEN))
lines.append('Safe-eval compatible: no imports, no context managers, no ZIP code.')
lines.append('Creates three technical attachments only after confirmation.')
lines.append('')

problems = 0

for key, label in REQUIRED_MARKERS:
    ok = Param.get_param(key) == '1'
    lines.append('%s marker: %s' % (label, 'PASS' if ok else 'FAIL'))
    if not ok:
        problems = problems + 1

specs = [
    ('commercial', COMM_KEY, COMM_FILENAME),
    ('vat', VAT_KEY, VAT_FILENAME),
]

rows = []
lines.append('')
lines.append('A) LIVE QWEB DISCOVERY')

for token, key, filename in specs:
    rs = View.search([('key', '=', key), ('type', '=', 'qweb')], limit=2)
    if len(rs) != 1:
        lines.append('  FAIL token=%s key=%s found=%s expected=1' % (token, key, len(rs)))
        problems = problems + 1
    else:
        rec = rs[0]
        arch = rec.arch_db or ''
        ok = bool(arch) and not rec.inherit_id
        lines.append(
            '  token=%s id=%s key=%s name=%r len_chars=%s write_date=%s standalone=%s'
            % (
                token,
                rec.id,
                rec.key,
                rec.name or '',
                len(arch),
                rec.write_date,
                not bool(rec.inherit_id),
            )
        )
        if not ok:
            problems = problems + 1
        rows.append((token, rec, arch, filename))

if len(rows) == 2:
    comm_arch = rows[0][2]
    vat_arch = rows[1][2]

    checks = [
        ('commercial Source present', 'barani_source_so' in comm_arch and '<strong>Source</strong>' in comm_arch),
        ('commercial Document Date present', '<strong>Document Date</strong>' in comm_arch),
        ('commercial 10pt metadata present', 'font-size:10pt; line-height:1.15' in comm_arch),
        ('commercial Customer Ref. wrap present', 'white-space:normal !important' in comm_arch and 'padding-right:14px' in comm_arch),
        ('commercial Payment Method present', '<strong>Payment Method</strong>' in comm_arch and '>Wire transfer<' in comm_arch),
        ('commercial old preferred label absent', 'Preferred Payment Method' not in comm_arch),
        ('commercial 10-column table retained', 'barani_discount_col_fixed' in comm_arch and 'barani_commercial_vat_rate_col_final' in comm_arch),
        ('VAT normalized Source present', 'barani_source_display' in vat_arch and 't-esc="barani_source_display"' in vat_arch),
        ('VAT Payment Method present', '<strong>Payment Method</strong>' in vat_arch and '>Wire transfer<' in vat_arch),
        ('VAT old preferred label absent', 'Preferred Payment Method' not in vat_arch),
        ('VAT historical Payment Reference fallback retained', 'barani_pdf_payment_ref' in vat_arch and 'barani_payment_ref_raw' in vat_arch),
        ('VAT credit-note metadata retained', 'barani_credit_original_payment_ref' in vat_arch and 'Original Invoice' in vat_arch),
        ('VAT down-payment logic retained', 'barani_down_payment_reconciliation_table' in vat_arch),
        ('VAT 10-column table retained', 'barani_discount_col_fixed' in vat_arch and 'barani_vat_rate_col_final' in vat_arch),
        ('no DDS dependency', 'dds_' not in (comm_arch + vat_arch).lower()),
    ]

    lines.append('')
    lines.append('B) ACCEPTED-CURRENT MARKER CHECKS')
    for label, ok in checks:
        lines.append('  %s: %s' % (label, 'PASS' if ok else 'FAIL'))
        if not ok:
            problems = problems + 1

if problems:
    lines.append('')
    lines.append('ERROR: %s problem(s); no attachments created.' % problems)
    raise UserError(NL.join(lines)[:90000])

lines.append('')
lines.append('PLAN')
lines.append('  create exact commercial XML attachment: %s' % COMM_FILENAME)
lines.append('  create exact VAT XML attachment: %s' % VAT_FILENAME)
lines.append('  create metadata/checksum text attachment: %s' % META_FILENAME)
lines.append('  Odoo will calculate attachment file_size and checksum automatically')
lines.append('  SHA-256 will be calculated after the files are uploaded for packaging')
lines.append('  no QWeb or business-record writes')

if CONFIRM != CONFIRM_TOKEN:
    lines.append('')
    lines.append('DRY RUN — no attachments created.')
    lines.append('Apply with CONFIRM=%s.' % CONFIRM_TOKEN)
    raise UserError(NL.join(lines)[:90000])

attachment_vals = []

for token, rec, arch, filename in rows:
    attachment_vals.append({
        'name': filename,
        'type': 'binary',
        'raw': arch.encode('utf-8'),
        'mimetype': 'application/xml',
        'res_model': 'ir.ui.view',
        'res_id': rec.id,
        'public': False,
        'description': (
            'Exact accepted-current live arch_db bytes. '
            'token=%s key=%s view_id=%s write_date=%s'
            % (token, rec.key or '', rec.id, rec.write_date or '')
        ),
    })

xml_attachments = Attachment.create(attachment_vals)

metadata_lines = []
metadata_lines.append('BARANI accepted-current QWeb export')
metadata_lines.append('Export date label: 2026-07-16')
metadata_lines.append('Scope: Source / Payment Method accepted-current live QWeb')
metadata_lines.append('S03 v5: problems=0 warnings=0')
metadata_lines.append('')

index = 0
for token, rec, arch, filename in rows:
    attach = xml_attachments[index]
    metadata_lines.append('token=%s' % token)
    metadata_lines.append('view_id=%s' % rec.id)
    metadata_lines.append('key=%s' % (rec.key or ''))
    metadata_lines.append('name=%s' % (rec.name or ''))
    metadata_lines.append('write_date=%s' % (rec.write_date or ''))
    metadata_lines.append('filename=%s' % filename)
    metadata_lines.append('chars=%s' % len(arch))
    metadata_lines.append('attachment_id=%s' % attach.id)
    metadata_lines.append('attachment_file_size=%s' % attach.file_size)
    metadata_lines.append('attachment_checksum_sha1=%s' % (attach.checksum or ''))
    metadata_lines.append('')
    index = index + 1

metadata_lines.append('No customer documents, business records, credentials,')
metadata_lines.append('restore payloads, or DDS business fields are included.')
metadata_raw = (NL.join(metadata_lines) + NL).encode('utf-8')

metadata_attachment = Attachment.create({
    'name': META_FILENAME,
    'type': 'binary',
    'raw': metadata_raw,
    'mimetype': 'text/plain',
    'res_model': 'ir.ui.view',
    'res_id': rows[0][1].id,
    'public': False,
    'description': 'Metadata for the accepted-current BARANI commercial and VAT QWeb export.',
})

attachments = xml_attachments | metadata_attachment

lines.append('')
lines.append('X01.1 COMPLETE: three technical export attachments created.')
for attach in attachments:
    lines.append(
        '  attachment_id=%s name=%r file_size=%s checksum_sha1=%s'
        % (attach.id, attach.name or '', attach.file_size, attach.checksum or '')
    )
lines.append('  QWeb/business writes performed: NONE')
lines.append('  Download all three files and upload them for GitHub packaging.')

action = {
    'type': 'ir.actions.act_window',
    'name': 'BARANI accepted-current QWeb export attachments',
    'res_model': 'ir.attachment',
    'view_mode': 'tree,form',
    'domain': [('id', 'in', attachments.ids)],
    'target': 'current',
}
