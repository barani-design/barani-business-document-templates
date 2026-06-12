# ============================================================================
# ACTION NAME : BARANI VAT REPORT — RESTORE FROM CURRENT L22 FINAL RESTORE POINT SAFE
# MODEL       : Module (ir.module.module) or any model; selected records ignored.
# ACTION TO DO: Execute Python Code
# RUN BY      : Run APPLY=False first; then APPLY=True + CONFIRM='RESTORE_VAT_POINT'.
# PURPOSE     : Restore the isolated BARANI VAT report family from a named restore
#               point created in ir.config_parameter by the companion backup script.
#
# WRITES      : Only the four isolated VAT artifacts: VAT body view, custom layout
#               view, VAT report action binding/meta, and dedicated VAT paperformat.
#               Does NOT write invoices, accounting entries, taxes, products,
#               journals, sequences, or live buttons 234/236/842/900.
# ============================================================================

APPLY = False
CONFIRM = ''

DEFAULT_BACKUP_TAG = 'public_current_template'
CURRENT_BACKUP_KEY = 'barani.vat_report.restore_point.current'
# BACKUP_TAG is resolved after Param is available.
BACKUP_TAG = ''
BACKUP_PREFIX = ''

VAT_VIEW_KEY = 'barani_vat.report_invoice_document_vat'
VAT_VIEW_NAME = 'BARANI VAT report_invoice_document (commercial/VAT layout) v02'
# Display name is restored from backup meta when available; technical identity is report_name/report_file.
VAT_REPORT_NAME_FALLBACK = 'VAT Invoices RI/DPI - 2026+'
PAPERFORMAT_NAME = 'BARANI VAT A4 7mm'
LAYOUT_VIEW_KEY = 'barani_vat.external_layout_standard_titled'
LAYOUT_VIEW_NAME = 'BARANI VAT external_layout_standard_titled (logo + title header)'
IDS_PARAMETER_KEY = 'barani.vat_report.ids'
OUTPUT_PARAMETER_KEY = 'barani.vat_report.restore_point.restore.last_run'
ACTION_NAME = 'BARANI VAT REPORT — RESTORE FROM CURRENT L22 FINAL RESTORE POINT SAFE'
PRINT_REPORT_NAME_EXPR = "('Credit Note' if object.move_type == 'out_refund' else 'Vendor Credit Note' if object.move_type == 'in_refund' else 'Vendor Bill' if object.move_type == 'in_invoice' else 'Draft Invoice' if object.state == 'draft' else 'Cancelled Invoice' if object.state == 'cancel' else 'Invoice') + ((' ' + object.name) if object.name and object.name != '/' else '')"

View = env['ir.ui.view'].sudo()
Report = env['ir.actions.report'].sudo()
Paper = env['report.paperformat'].sudo()
Model = env['ir.model'].sudo()
Param = env['ir.config_parameter'].sudo()

BACKUP_TAG = Param.get_param(CURRENT_BACKUP_KEY, '') or DEFAULT_BACKUP_TAG
BACKUP_PREFIX = 'barani.vat_report.restore_point.' + BACKUP_TAG

lines = []
lines.append(ACTION_NAME)
lines.append('APPLY=%s CONFIRM=%s' % (APPLY, CONFIRM))
lines.append('BACKUP_TAG=%s' % BACKUP_TAG)
lines.append('')

# Savepoint/caches.
manual_sp_ok = False
cache_inv_method = ''
lines.append('TEST 0 - manual SQL savepoint recovery + ORM cache invalidation')
try:
    env.cr.execute('SAVEPOINT t0_ok')
    env.cr.execute('SELECT 1')
    env.cr.execute('RELEASE SAVEPOINT t0_ok')
    env.cr.execute('SAVEPOINT t0_fail')
    try:
        env.cr.execute('SELECT * FROM __barani_missing_table_for_rollback_probe__')
        env.cr.execute('RELEASE SAVEPOINT t0_fail')
    except Exception:
        env.cr.execute('ROLLBACK TO SAVEPOINT t0_fail')
        env.cr.execute('RELEASE SAVEPOINT t0_fail')
        try:
            env.invalidate_all()
            cache_inv_method = 'env.invalidate_all'
        except Exception:
            try:
                env.cache.invalidate()
                cache_inv_method = 'env.cache.invalidate'
            except Exception:
                cache_inv_method = ''
        if cache_inv_method:
            manual_sp_ok = True
            lines.append('PASS: SAVEPOINT recovery works; cache method=%s' % cache_inv_method)
except Exception as e0:
    lines.append('FATAL TEST 0: %s' % str(e0)[:500])
if not manual_sp_ok:
    lines.append('STOP: savepoint/cache mechanism unusable.')
    raise UserError('\n'.join(lines)[:90000])
lines.append('')

vat_key = BACKUP_PREFIX + '.vat_arch'
layout_key = BACKUP_PREFIX + '.layout_arch'
ids_key = BACKUP_PREFIX + '.ids'
created_key = BACKUP_PREFIX + '.created'
meta_key = BACKUP_PREFIX + '.meta'
backup_meta = Param.get_param(meta_key, '') or ''
backup_report_display_name = ''
if backup_meta:
    meta_rows = backup_meta.split('\n')
    for meta_row in meta_rows:
        if meta_row[:12] == 'report_name=':
            backup_report_display_name = meta_row[12:]
vat_arch = Param.get_param(vat_key, '') or ''
layout_arch = Param.get_param(layout_key, '') or ''
ids_text = Param.get_param(ids_key, '') or ''
created = Param.get_param(created_key, '') or ''

lines.append('RESTORE POINT')
lines.append('  created=%r' % created)
lines.append('  ids=%r' % ids_text)
lines.append('  vat_arch_len=%s layout_arch_len=%s' % (len(vat_arch), len(layout_arch)))
if not created or not vat_arch or not layout_arch or not ids_text:
    lines.append('ERROR: restore point is incomplete. Refusing.')
    raise UserError('\n'.join(lines)[:90000])

# Guard backup content itself.
marker_error = False
checks = [
    ('backup bank transfer band present', 'barani_bank_transfer_band' in vat_arch and 'Bank transfer:' in vat_arch),
    ('backup bank name/address present', 'Bank address:' in vat_arch and 'Bank: ' in vat_arch and 'barani_bank_address_clean' in vat_arch),
    ('backup QR omitted', 'o.display_qr_code' not in vat_arch and '_generate_qr_code' not in vat_arch),
    ('backup EORI present', 'EORI' in layout_arch),
    ('backup Prepared by / Issued by present', 'Prepared by / Issued by' in vat_arch and 'barani_issued_by_slot' in vat_arch),
    ('backup Fiscal position notes present', 'barani_fiscal_position_note' in vat_arch and 'fiscal_position_id.note' in vat_arch),
    ('backup Incoterms code/name + Not specified present', 'barani_incoterms_code_name' in vat_arch and 'invoice_incoterm_id' in vat_arch and 'Not specified' in vat_arch),
    ('backup Intrastat single-line present', vat_arch.count('name="barani_intrastat_transport_code"') == 1 and 'intrastat_transport_mode_id' in vat_arch),
    ('backup Credit-note cleanup present', 'Original Invoice / Reference' in vat_arch and 'Amount credited' in vat_arch and 'barani_credit_origin_reference' in vat_arch),
    ('backup Discount percent cleanup present', 'barani_discount_percent_cell' in vat_arch and '<span>Disc.</span>' in vat_arch),
    ('backup table markers present', 'width:32%' in vat_arch and 'barani_unit_col_wide' in vat_arch and 'barani_vat_rate_col_final' in vat_arch),
    ('backup address no-indent classes present', 'barani_customer_cell' in vat_arch and 'barani_has_shipping' in vat_arch and 'barani_shipping_cell' in vat_arch),
    ('backup Tel phone labels present', 'Tel:' in vat_arch and 'barani_customer_phone' in vat_arch and 'barani_shipping_phone' in vat_arch),
    ('backup customer/shipping email labels present', 'Email: ' in vat_arch and 'barani_customer_email' in vat_arch and 'barani_shipping_email' in vat_arch),
    ('backup invoice/SO note fallback present', 'barani_sale_order_note_fallback' in vat_arch and 'barani_note_source_orders' in vat_arch and 'sale_line_ids.order_id' in vat_arch),
    ('backup down-payment reconciliation present', 'barani_down_payment_reconciliation' in vat_arch and 'Down payment reconciliation' in vat_arch and 'Total Advances Received' not in vat_arch),
    ('backup confirmed company bank fallback present', 'barani_company_receiving_bank' in vat_arch and 'barani_effective_bank' in vat_arch),
    ('backup L21 header alignment present', 'name="company_registration"' in layout_arch and 'padding-left:18px' in layout_arch),
    ('backup right-side title/header present; centered title absent', 'bvt_type_label' in layout_arch and 't-field="o.name"' in layout_arch and 'barani_doc_title' not in layout_arch and 'company_registration' in layout_arch),
]
for chk in checks:
    lines.append('  %s: %s' % (chk[0], 'PASS' if chk[1] else 'FAIL'))
    if not chk[1]:
        marker_error = True
if marker_error:
    lines.append('ERROR: restore-point content does not look like the intended L22 final RI/DPI 2026+ baseline. Refusing.')
    raise UserError('\n'.join(lines)[:90000])
lines.append('')

# Resolve current artifacts by key/technical identity.
vat_view = View.search([('key', '=', VAT_VIEW_KEY)], limit=1)
layout_view = View.search([('key', '=', LAYOUT_VIEW_KEY)], limit=1)
vat_report_candidates = Report.search([('model', '=', 'account.move'), ('report_type', '=', 'qweb-pdf'), ('report_name', '=', VAT_VIEW_KEY), ('report_file', '=', VAT_VIEW_KEY)])
vat_report = Report.browse()
if len(vat_report_candidates) == 1:
    vat_report = vat_report_candidates
vat_paper = Paper.search([('name', '=', PAPERFORMAT_NAME)], limit=1)
move_model = Model.search([('model', '=', 'account.move')], limit=1)

identity_error = False
lines.append('CURRENT TARGET ARTIFACTS')
lines.append('  VAT view id=%s' % (vat_view.id if vat_view else 0))
lines.append('  Layout id=%s' % (layout_view.id if layout_view else 0))
lines.append('  Report id=%s name=%r' % (vat_report.id if vat_report else 0, vat_report.name if vat_report else ''))
if len(vat_report_candidates) > 1:
    identity_error = True
    lines.append('ERROR: duplicate BARANI VAT technical reports found; refusing to guess.')
lines.append('  Paper id=%s' % (vat_paper.id if vat_paper else 0))

if not vat_view or not vat_view.exists() or vat_view.key != VAT_VIEW_KEY or vat_view.type != 'qweb' or vat_view.inherit_id:
    identity_error = True
    lines.append('ERROR: VAT view identity mismatch or missing.')
if not layout_view or not layout_view.exists() or layout_view.key != LAYOUT_VIEW_KEY or layout_view.type != 'qweb' or layout_view.inherit_id:
    identity_error = True
    lines.append('ERROR: layout view identity mismatch or missing.')
if not vat_report or not vat_report.exists() or vat_report.model != 'account.move' or vat_report.report_type != 'qweb-pdf' or vat_report.report_name != VAT_VIEW_KEY or vat_report.report_file != VAT_VIEW_KEY:
    identity_error = True
    lines.append('ERROR: report identity mismatch or missing.')
if not vat_paper or not vat_paper.exists() or vat_paper.name != PAPERFORMAT_NAME:
    identity_error = True
    lines.append('ERROR: paperformat identity mismatch or missing.')
if not move_model:
    identity_error = True
    lines.append('ERROR: account.move ir.model missing.')
if identity_error:
    raise UserError('\n'.join(lines)[:90000])
if not backup_report_display_name:
    backup_report_display_name = vat_report.name or VAT_REPORT_NAME_FALLBACK
lines.append('  restore report display name=%r' % backup_report_display_name)
lines.append('PASS: current artifact identity checks passed.')
lines.append('')

# Parse stored paper values.
try:
    margin_top = float(Param.get_param(BACKUP_PREFIX + '.paper.margin_top', '') or vat_paper.margin_top or 0.0)
except Exception:
    margin_top = vat_paper.margin_top
try:
    margin_bottom = float(Param.get_param(BACKUP_PREFIX + '.paper.margin_bottom', '') or vat_paper.margin_bottom or 0.0)
except Exception:
    margin_bottom = vat_paper.margin_bottom
try:
    margin_left = float(Param.get_param(BACKUP_PREFIX + '.paper.margin_left', '') or vat_paper.margin_left or 0.0)
except Exception:
    margin_left = vat_paper.margin_left
try:
    margin_right = float(Param.get_param(BACKUP_PREFIX + '.paper.margin_right', '') or vat_paper.margin_right or 0.0)
except Exception:
    margin_right = vat_paper.margin_right
try:
    header_spacing = float(Param.get_param(BACKUP_PREFIX + '.paper.header_spacing', '') or vat_paper.header_spacing or 0.0)
except Exception:
    header_spacing = vat_paper.header_spacing
try:
    dpi_val = int(float(Param.get_param(BACKUP_PREFIX + '.paper.dpi', '') or vat_paper.dpi or 90))
except Exception:
    dpi_val = vat_paper.dpi or 90

lines.append('PLAN')
lines.append('  - restore VAT body view arch len=%s to id=%s' % (len(vat_arch), vat_view.id))
lines.append('  - restore custom layout arch len=%s to id=%s' % (len(layout_arch), layout_view.id))
lines.append('  - restore dedicated paper margins T/B/L/R=%s/%s/%s/%s header_spacing=%s dpi=%s' % (margin_top, margin_bottom, margin_left, margin_right, header_spacing, dpi_val))
lines.append('  - reassert report action binding to account.move and this paperformat')
lines.append('  - NO live buttons 234/236/842/900 or invoice/accounting records touched')
lines.append('')

if not APPLY:
    lines.append('DRY RUN COMPLETE: no writes performed.')
    lines.append("Set APPLY=True and CONFIRM='RESTORE_VAT_POINT' to restore.")
    raise UserError('\n'.join(lines)[:90000])
if CONFIRM != 'RESTORE_VAT_POINT':
    lines.append("ERROR: APPLY=True but CONFIRM != 'RESTORE_VAT_POINT'. Refusing.")
    raise UserError('\n'.join(lines)[:90000])

try:
    env.cr.execute('SAVEPOINT sp_restore_vat_point')
    vat_paper.write({
        'name': PAPERFORMAT_NAME,
        'format': 'A4',
        'orientation': 'Portrait',
        'margin_top': margin_top,
        'margin_bottom': margin_bottom,
        'margin_left': margin_left,
        'margin_right': margin_right,
        'header_spacing': header_spacing,
        'header_line': False,
        'dpi': dpi_val,
    })
    layout_view.write({'name': LAYOUT_VIEW_NAME, 'type': 'qweb', 'inherit_id': False, 'arch_db': layout_arch})
    vat_view.write({'name': VAT_VIEW_NAME, 'type': 'qweb', 'inherit_id': False, 'arch_db': vat_arch})
    report_vals = {
        'name': backup_report_display_name,
        'model': 'account.move',
        'report_type': 'qweb-pdf',
        'report_name': VAT_VIEW_KEY,
        'report_file': VAT_VIEW_KEY,
        'binding_model_id': move_model.id,
        'binding_type': 'report',
        'paperformat_id': vat_paper.id,
        'print_report_name': Param.get_param(BACKUP_PREFIX + '.report.print_report_name', '') or PRINT_REPORT_NAME_EXPR,
    }
    group_text = Param.get_param(BACKUP_PREFIX + '.report.groups_id', '') or ''
    group_ids = []
    if group_text:
        parts = group_text.split(',')
        for part in parts:
            try:
                gid = int(part or '0')
            except Exception:
                gid = 0
            if gid:
                group_ids.append(gid)
    if group_ids:
        report_vals['groups_id'] = [(6, 0, group_ids)]
    vat_report.write(report_vals)
    Param.set_param(IDS_PARAMETER_KEY, '%s,%s,%s,%s' % (vat_view.id, vat_report.id, vat_paper.id, layout_view.id))
    if cache_inv_method == 'env.invalidate_all':
        env.invalidate_all()
    else:
        env.cache.invalidate()
    env.cr.execute('RELEASE SAVEPOINT sp_restore_vat_point')
    lines.append('PASS: restored VAT report family from restore point %s.' % BACKUP_TAG)
    lines.append('PASS: ORM cache invalidated via %s.' % cache_inv_method)
except Exception as e_apply:
    try:
        env.cr.execute('ROLLBACK TO SAVEPOINT sp_restore_vat_point')
        env.cr.execute('RELEASE SAVEPOINT sp_restore_vat_point')
    except Exception as e_rb:
        lines.append('ROLLBACK PROBLEM: %s' % str(e_rb)[:500])
    lines.append('RESTORE FAILED: %s' % str(e_apply)[:1500])
    raise UserError('\n'.join(lines)[:90000])

lines.append('RESTORE COMPLETE. Print a fresh VAT Invoices RI/DPI - 2026+ PDF to verify.')
text = '\n'.join(lines)
Param.set_param(OUTPUT_PARAMETER_KEY, text)
param = Param.search([('key', '=', OUTPUT_PARAMETER_KEY)], limit=1)
action = {'type': 'ir.actions.act_window', 'name': ACTION_NAME, 'res_model': 'ir.config_parameter', 'view_mode': 'form', 'res_id': param.id, 'target': 'current'}
