# ============================================================================
# ACTION NAME : BARANI DELIVERY DOCS DEV STEP 33A — company report colour probe
#               v5.0 READ-ONLY
# MODEL       : Any model; selected records ignored. Module (ir.module.module)
#               is convenient.
# ACTION TO DO: Execute Python Code
# RUN BY      : Settings -> Technical -> Actions -> Server Actions -> Run
# PURPOSE     : Identify the company report colours used by Odoo document
#               layouts so DN/PickOps address headings can match RI/DPI/table
#               header colour instead of a hard-coded red.
# READ-ONLY   : search/read only. No create/write/unlink/set_param/commit.
# SAFE_EVAL   : no import/def/lambda/comprehensions/with/getattr/hasattr/
#               setattr/eval/exec/open/dir/isinstance.
# ============================================================================

ACTION_NAME = 'BARANI DELIVERY DOCS DEV STEP 33A — company report colour probe v5.0 READ-ONLY'
READ_ONLY = True
OUTPUT_MODE = 'paged'
PAGE = 1
PAGE_SIZE = 15000

lines = []
lines.append(ACTION_NAME)
lines.append('READ_ONLY=%s | OUTPUT_MODE=%s | PAGE=%s PAGE_SIZE=%s' % (READ_ONLY, OUTPUT_MODE, PAGE, PAGE_SIZE))
lines.append('Purpose: read company/report colour fields and layout colour references. No writes.')
lines.append('')

Param = env['ir.config_parameter'].sudo()
View = env['ir.ui.view'].sudo()
CompanyModel = env['res.company'].sudo()

# ---------------------------------------------------------------------------
# 1) DATABASE / ENVIRONMENT IDENTITY
# ---------------------------------------------------------------------------
lines.append('1) DATABASE / ENVIRONMENT IDENTITY')
try:
    lines.append('  env.cr.dbname: %s' % env.cr.dbname)
except Exception as e_db:
    lines.append('  env.cr.dbname: ERROR %s' % str(e_db)[:300])
base_url = Param.get_param('web.base.url', '') or ''
db_uuid = Param.get_param('database.uuid', '') or ''
db_create_date = Param.get_param('database.create_date', '') or ''
lines.append('  web.base.url: %s' % base_url)
lines.append('  database.uuid: %s' % db_uuid)
lines.append('  database.create_date: %s' % db_create_date)
lines.append('')

# ---------------------------------------------------------------------------
# 2) CURRENT USER / COMPANY
# ---------------------------------------------------------------------------
co = env.company.sudo()
lines.append('2) CURRENT USER / COMPANY')
lines.append("  user: id=%s name=%r login=%r" % (env.user.id, env.user.name, env.user.login))
lines.append("  company: id=%s name=%r vat=%r" % (co.id, co.name, co.vat or ''))
lines.append('')

# ---------------------------------------------------------------------------
# 3) COMPANY COLOUR FIELDS
# ---------------------------------------------------------------------------
lines.append('3) COMPANY COLOUR FIELDS')
colour_fields = ['primary_color', 'secondary_color', 'email_primary_color', 'email_secondary_color']
for fname in colour_fields:
    if fname in CompanyModel._fields:
        try:
            lines.append('  %s = %r' % (fname, co[fname] or ''))
        except Exception as e_col:
            lines.append('  %s = ERROR %s' % (fname, str(e_col)[:300]))
    else:
        lines.append('  %s = FIELD_NOT_FOUND' % fname)
lines.append('')

# ---------------------------------------------------------------------------
# 4) REPORT LAYOUT FIELD / ARCH COLOUR REFERENCES
# ---------------------------------------------------------------------------
lines.append('4) REPORT LAYOUT / TEMPLATE COLOUR REFERENCES')
if 'external_report_layout_id' in CompanyModel._fields:
    layout = co.external_report_layout_id
    if layout:
        lines.append("  company.external_report_layout_id: id=%s key=%s name=%r" % (layout.id, layout.key or '', layout.name))
        arch = layout.arch_db or ''
        lines.append('    arch_chars=%s contains primary_color=%s secondary_color=%s company_color=%s #B00020=%s #ff0000=%s' % (len(arch), 'YES' if 'primary_color' in arch else 'NO', 'YES' if 'secondary_color' in arch else 'NO', 'YES' if 'company_color' in arch else 'NO', 'YES' if '#B00020' in arch else 'NO', 'YES' if '#ff0000' in arch else 'NO'))
    else:
        lines.append('  company.external_report_layout_id: EMPTY')
else:
    lines.append('  company.external_report_layout_id: FIELD_NOT_FOUND')

# Check common web layout templates for colour references.
keys = ['web.external_layout_standard', 'web.external_layout_boxed', 'web.external_layout_bold', 'barani_vat.external_layout_standard_titled', 'barani_delivery.external_layout_delivery_2026', 'barani_delivery.external_layout_picking_operations_2026']
for key in keys:
    vv = View.search([('key', '=', key)])
    ids_text = ''
    for v in vv:
        ids_text = (ids_text + ',' if ids_text else '') + str(v.id)
    lines.append("  VIEW key=%s count=%s ids=%s" % (key, len(vv), ids_text))
    if len(vv) == 1:
        arch = vv.arch_db or ''
        lines.append('    name=%r arch_chars=%s contains primary_color=%s secondary_color=%s #B00020=%s #ff0000=%s' % (vv.name, len(arch), 'YES' if 'primary_color' in arch else 'NO', 'YES' if 'secondary_color' in arch else 'NO', 'YES' if '#B00020' in arch else 'NO', 'YES' if '#ff0000' in arch else 'NO'))
lines.append('')

# ---------------------------------------------------------------------------
# 5) CURRENT BARANI BODY MARKERS
# ---------------------------------------------------------------------------
lines.append('5) CURRENT BARANI BODY COLOUR MARKERS')
for key in ['barani_delivery.report_delivery_note_2026', 'barani_delivery.report_picking_operations_2026']:
    vv = View.search([('key', '=', key)])
    ids_text = ''
    for v in vv:
        ids_text = (ids_text + ',' if ids_text else '') + str(v.id)
    lines.append('  VIEW key=%s count=%s ids=%s' % (key, len(vv), ids_text))
    if len(vv) == 1:
        arch = vv.arch_db or ''
        lines.append('    name=%r arch_chars=%s #B00020=%s #ff0000=%s primary_color=%s secondary_color=%s Customer_colon=%s Shipping_colon=%s Delivery_Address_colon=%s' % (vv.name, len(arch), 'YES' if '#B00020' in arch else 'NO', 'YES' if '#ff0000' in arch else 'NO', 'YES' if 'primary_color' in arch else 'NO', 'YES' if 'secondary_color' in arch else 'NO', 'YES' if 'Customer:' in arch else 'NO', 'YES' if 'Shipping Address:' in arch else 'NO', 'YES' if 'Delivery Address:' in arch else 'NO'))
lines.append('')

# ---------------------------------------------------------------------------
# 6) INTERPRETATION
# ---------------------------------------------------------------------------
lines.append('6) INTERPRETATION')
lines.append('  Use the colour field whose hex value matches the existing table/header Barani red.')
lines.append('  If primary_color/secondary_color are available and one matches the table-header red, Step 33 can use a dynamic company-field style.')
lines.append('  If neither field is reliable, Step 33 should hard-code the exact audited hex from this output / Document Layout colour picker.')
lines.append('  Parent-company VAT fallback can be bundled into Step 33 because it modifies the same address blocks.')
lines.append('')
lines.append('END OF READ-ONLY COLOUR PROBE')

text = '\n'.join(lines)
full_len = len(text)
pages_int = int(full_len / PAGE_SIZE)
if pages_int * PAGE_SIZE < full_len:
    pages_int = pages_int + 1
if pages_int < 1:
    pages_int = 1
start_idx = (PAGE - 1) * PAGE_SIZE
if start_idx < 0:
    start_idx = 0
end_idx = start_idx + PAGE_SIZE
more = 'NO'
if start_idx >= full_len:
    body = '(PAGE %s past end; full length %s chars.)' % (PAGE, full_len)
else:
    body = text[start_idx:end_idx]
    if end_idx < full_len:
        more = 'YES'
head = []
head.append('============ PAGED OUTPUT ============')
head.append('FULL = %s chars | PAGE %s of %s | SHOWING %s-%s | MORE REMAINS: %s' % (full_len, PAGE, pages_int, start_idx, end_idx, more))
head.append('======================================')
head.append('')
raise UserError('\n'.join(head) + '\n' + body)
