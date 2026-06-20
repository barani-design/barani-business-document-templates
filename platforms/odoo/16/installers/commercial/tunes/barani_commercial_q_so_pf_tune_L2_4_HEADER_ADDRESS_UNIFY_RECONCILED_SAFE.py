# L2.4 (2026-06-17): reconciled final. Based on the Claude L2.1 export-aligned script, preserving its stricter live-layout check for barani_doc_number and the audited #ed1c24 heading colour. Renamed/versioned to avoid confusion with the earlier failed L2.1 self-check draft.
# ============================================================================
# ACTION NAME : BARANI COMMERCIAL Q/SO/PF TUNE L2.4 — header/address unification reconciled
# MODEL       : Module (ir.module.module) or any model; selected records ignored.
# ACTION TO DO: Execute Python Code
# VISIBILITY  : Create/run from Settings > Technical > Server Actions. This
#               server action itself is normally run from its form. It updates
#               the existing BARANI sale.order PDF templates used by the Print
#               menu entries 'Quotation / Order — 2026+' and 'PRO-FORMA — 2026+'.
#
# OUTPUT      : APPLY=False dry-run output is raised via UserError and performs
#               no writes. APPLY=True stores technical output/backup in
#               ir.config_parameter while writes remain gated by APPLY+CONFIRM.
#
# PAGINATION  : PAGE/PAGE_SIZE control the dry-run dialog if output grows.
#
# PURPOSE     : Targeted tune for commercial Q/SO/PF documents so their header
#               and address-block treatment follows the RI/DPI invoice direction:
#                 1. Remove duplicate centered document title from the header;
#                    keep right-side '<Document Type>: <Document No.>' only.
#                 2. Render address block labels as red labels with colon:
#                    'Customer:' and 'Shipping Address:'.
#                 3. Keep customer ID/VAT visible and use 'VAT:' label.
#                 4. Add ID/VAT to the Shipping Address block as well, using the
#                    shipping contact commercial parent fallback.
#
# SCOPE       : Standalone BARANI commercial layout and body views only:
#                 barani_commercial.external_layout_standard_titled
#                 barani_commercial.report_saleorder_document
#               No stock Odoo/DDS/Studio actions/templates are touched.
#
# SAFETY      : No create/unlink. Writes only the two BARANI-owned views, only
#               when APPLY=True and CONFIRM matches. Stores one-time backups of
#               the pre-tune layout/body arches before writing.
# ============================================================================

APPLY = False
CONFIRM = ''
PAGE = 1
PAGE_SIZE = 16000

CONFIRM_TOKEN = 'INSTALL_BARANI_COMMERCIAL_Q_SO_PF_TUNE_L2_4'
ACTION_NAME = 'BARANI COMMERCIAL Q/SO/PF TUNE L2.4 — header/address unification reconciled'
OUTPUT_PARAMETER_KEY = 'barani.commercial_report.tune_l2.last_run'
BACKUP_BODY_PARAMETER_KEY = 'barani.commercial_report.backup.tune_l2.body.arch'
BACKUP_LAYOUT_PARAMETER_KEY = 'barani.commercial_report.backup.tune_l2.layout.arch'
BACKUP_MARKER_KEY = 'barani.commercial_report.backup.tune_l2.marker'
LAYOUT_VIEW_KEY = 'barani_commercial.external_layout_standard_titled'
BODY_VIEW_KEY = 'barani_commercial.report_saleorder_document'
SALE_WRAPPER_KEY = 'barani_commercial.report_saleorder'
PF_WRAPPER_KEY = 'barani_commercial.report_saleorder_proforma'

View = env['ir.ui.view'].sudo()
Report = env['ir.actions.report'].sudo()
Param = env['ir.config_parameter'].sudo()
Field = env['ir.model.fields'].sudo()

NL = chr(10)
lines = []
lines.append(ACTION_NAME)
lines.append('APPLY=%s CONFIRM=%s PAGE=%s PAGE_SIZE=%s' % (APPLY, CONFIRM, PAGE, PAGE_SIZE))
lines.append('Scope: targeted update to existing standalone BARANI commercial layout/body views only.')
lines.append('No stock Odoo/DDS/Studio actions/templates are touched.')
lines.append('')

layout_views = View.search([('key', '=', LAYOUT_VIEW_KEY), ('type', '=', 'qweb')])
body_views = View.search([('key', '=', BODY_VIEW_KEY), ('type', '=', 'qweb')])
sale_reports = Report.search([('report_name', '=', SALE_WRAPPER_KEY), ('model', '=', 'sale.order')])
pf_reports = Report.search([('report_name', '=', PF_WRAPPER_KEY), ('model', '=', 'sale.order')])

lines.append('DISCOVERY')
lines.append('  layout views key=%s: %s' % (LAYOUT_VIEW_KEY, len(layout_views)))
lines.append('  body views key=%s: %s' % (BODY_VIEW_KEY, len(body_views)))
lines.append('  sale reports report_name=%s: %s' % (SALE_WRAPPER_KEY, len(sale_reports)))
lines.append('  PF reports report_name=%s: %s' % (PF_WRAPPER_KEY, len(pf_reports)))
if len(layout_views) != 1 or len(body_views) != 1:
    lines.append('ERROR: expected exactly one BARANI commercial layout and one body view. Refusing.')
    text = NL.join(lines)
    start = (PAGE - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    raise UserError(('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s' % (PAGE, start, min(end, len(text)), len(text), 'YES' if end < len(text) else 'NO')) + NL + text[start:end])
if len(sale_reports) > 1 or len(pf_reports) > 1:
    lines.append('ERROR: duplicate BARANI commercial report action detected. Refusing.')
    text = NL.join(lines)
    start = (PAGE - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    raise UserError(('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s' % (PAGE, start, min(end, len(text)), len(text), 'YES' if end < len(text) else 'NO')) + NL + text[start:end])

layout_view = layout_views[0]
body_view = body_views[0]
old_layout_arch = layout_view.arch_db or ''
old_body_arch = body_view.arch_db or ''
lines.append('  layout view id=%s name=%r inherit_id=%s arch_len=%s write_date=%s' % (layout_view.id, layout_view.name, layout_view.inherit_id.id if layout_view.inherit_id else '', len(old_layout_arch), layout_view.write_date))
lines.append('  body view id=%s name=%r inherit_id=%s arch_len=%s write_date=%s' % (body_view.id, body_view.name, body_view.inherit_id.id if body_view.inherit_id else '', len(old_body_arch), body_view.write_date))
lines.append('')

if layout_view.inherit_id or body_view.inherit_id:
    lines.append('ERROR: expected standalone BARANI views with inherit_id empty. Refusing.')
    text = NL.join(lines)
    start = (PAGE - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    raise UserError(('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s' % (PAGE, start, min(end, len(text)), len(text), 'YES' if end < len(text) else 'NO')) + NL + text[start:end])

# Layout patch: remove duplicate centered title. The right-side title+number remains.
OLD_CENTER_TITLE = '''      <div t-if="o and o._name == 'sale.order'" name="barani_doc_title" style="position:absolute; left:0; right:0; top:0; height:41px; line-height:41px; text-align:center; z-index:15;">
        <span style="font-size:15pt; font-weight:bold; white-space:nowrap; vertical-align:middle;" t-esc="barani_doc_title"/>
      </div>
'''
NEW_CENTER_TITLE = ''

# Body patches: red colon labels, VAT label normalization, shipping ID/VAT.
OLD_CUSTOMER_LABEL = '<strong>Customer</strong>'
NEW_CUSTOMER_LABEL = '<strong name="barani_customer_label" style="color:#ed1c24;">Customer:</strong>'
OLD_SHIPPING_LABEL = '<strong>Shipping Address</strong>'
NEW_SHIPPING_LABEL = '<strong name="barani_shipping_label" style="color:#ed1c24;">Shipping Address:</strong>'

OLD_CUSTOMER_ID_LINE = '<div t-if="barani_customer_partner.company_registry or o.partner_id.company_registry" class="mt-1">ID: <span t-esc="barani_customer_partner.company_registry or o.partner_id.company_registry"/></div>'
NEW_CUSTOMER_ID_LINE = '<div t-if="barani_customer_partner.company_registry or o.partner_id.company_registry" name="barani_customer_id_line" class="mt-1">ID: <span t-esc="barani_customer_partner.company_registry or o.partner_id.company_registry"/></div>'
OLD_CUSTOMER_VAT_BLOCK = '''        <div t-if="barani_customer_partner.vat or o.partner_id.vat" class="mt-1">
          <t t-if="o.company_id.account_fiscal_country_id.vat_label" t-esc="o.company_id.account_fiscal_country_id.vat_label"/>
          <t t-else="">Tax ID</t>: <span t-esc="barani_customer_partner.vat or o.partner_id.vat"/>
        </div>'''
NEW_CUSTOMER_VAT_BLOCK = '        <div t-if="barani_customer_partner.vat or o.partner_id.vat" name="barani_customer_vat_line" class="mt-1">VAT: <span t-esc="barani_customer_partner.vat or o.partner_id.vat"/></div>'

SHIPPING_ID_VAT_BLOCK = '''
        <div t-if="barani_shipping_parent.company_registry or barani_shipping_partner.company_registry" name="barani_shipping_id_line" class="mt-1">ID: <span t-esc="barani_shipping_parent.company_registry or barani_shipping_partner.company_registry"/></div>
        <div t-if="barani_shipping_parent.vat or barani_shipping_partner.vat" name="barani_shipping_vat_line" class="mt-1">VAT: <span t-esc="barani_shipping_parent.vat or barani_shipping_partner.vat"/></div>'''

# Insertion point when L1 contact tune already exists.
OLD_SHIPPING_EMAIL_LINE = '<div t-if="barani_shipping_email" name="barani_shipping_email_line">Email: <span t-esc="barani_shipping_email"/></div>'
NEW_SHIPPING_EMAIL_PLUS_ID_VAT = OLD_SHIPPING_EMAIL_LINE + SHIPPING_ID_VAT_BLOCK

# Fallback insertion point if L1 was not applied.
OLD_SHIPPING_WIDGET = '<div t-field="o.partner_shipping_id" t-options="{&quot;widget&quot;: &quot;contact&quot;, &quot;fields&quot;: [&quot;address&quot;, &quot;name&quot;], &quot;no_marker&quot;: true}"/>'
NEW_SHIPPING_WIDGET_PLUS_ID_VAT = OLD_SHIPPING_WIDGET + '''
        <t t-set="barani_shipping_partner" t-value="o.partner_shipping_id"/>
        <t t-set="barani_shipping_parent" t-value="barani_shipping_partner.commercial_partner_id or barani_shipping_partner"/>''' + SHIPPING_ID_VAT_BLOCK

new_layout_arch = old_layout_arch
new_body_arch = old_body_arch
layout_changed = False
body_changed = False
replace_error = False

lines.append('PATCH ANALYSIS')
if 'name="barani_doc_title"' not in new_layout_arch:
    lines.append('  center duplicate title: already removed')
else:
    if OLD_CENTER_TITLE in new_layout_arch:
        new_layout_arch = new_layout_arch.replace(OLD_CENTER_TITLE, NEW_CENTER_TITLE, 1)
        layout_changed = True
        lines.append('  center duplicate title: WILL REMOVE from layout')
    else:
        replace_error = True
        lines.append('  center duplicate title: FAIL - expected exact layout block not found')

if 'name="barani_customer_label"' in new_body_arch and 'Customer:' in new_body_arch:
    lines.append('  Customer label red/colon: already present')
else:
    if OLD_CUSTOMER_LABEL in new_body_arch:
        new_body_arch = new_body_arch.replace(OLD_CUSTOMER_LABEL, NEW_CUSTOMER_LABEL, 1)
        body_changed = True
        lines.append('  Customer label red/colon: WILL UPDATE')
    else:
        replace_error = True
        lines.append('  Customer label red/colon: FAIL - old Customer label not found')

if 'name="barani_shipping_label"' in new_body_arch and 'Shipping Address:' in new_body_arch:
    lines.append('  Shipping label red/colon: already present')
else:
    if OLD_SHIPPING_LABEL in new_body_arch:
        new_body_arch = new_body_arch.replace(OLD_SHIPPING_LABEL, NEW_SHIPPING_LABEL, 1)
        body_changed = True
        lines.append('  Shipping label red/colon: WILL UPDATE')
    else:
        replace_error = True
        lines.append('  Shipping label red/colon: FAIL - old Shipping Address label not found')

if 'name="barani_customer_id_line"' in new_body_arch:
    lines.append('  Customer ID line marker: already present')
else:
    if OLD_CUSTOMER_ID_LINE in new_body_arch:
        new_body_arch = new_body_arch.replace(OLD_CUSTOMER_ID_LINE, NEW_CUSTOMER_ID_LINE, 1)
        body_changed = True
        lines.append('  Customer ID line marker: WILL ADD')
    else:
        lines.append('  Customer ID line marker: expected old snippet not found; continuing if ID line exists')

if 'name="barani_customer_vat_line"' in new_body_arch:
    lines.append('  Customer VAT label normalized: already present')
else:
    if OLD_CUSTOMER_VAT_BLOCK in new_body_arch:
        new_body_arch = new_body_arch.replace(OLD_CUSTOMER_VAT_BLOCK, NEW_CUSTOMER_VAT_BLOCK, 1)
        body_changed = True
        lines.append('  Customer VAT label normalized: WILL CHANGE to VAT')
    else:
        replace_error = True
        lines.append('  Customer VAT label normalized: FAIL - old customer VAT block not found')

if 'name="barani_shipping_vat_line"' in new_body_arch and 'name="barani_shipping_id_line"' in new_body_arch:
    lines.append('  Shipping ID/VAT lines: already present')
else:
    if OLD_SHIPPING_EMAIL_LINE in new_body_arch and 'barani_shipping_parent' in new_body_arch:
        new_body_arch = new_body_arch.replace(OLD_SHIPPING_EMAIL_LINE, NEW_SHIPPING_EMAIL_PLUS_ID_VAT, 1)
        body_changed = True
        lines.append('  Shipping ID/VAT lines: WILL ADD after shipping email')
    elif OLD_SHIPPING_WIDGET in new_body_arch:
        new_body_arch = new_body_arch.replace(OLD_SHIPPING_WIDGET, NEW_SHIPPING_WIDGET_PLUS_ID_VAT, 1)
        body_changed = True
        lines.append('  Shipping ID/VAT lines: WILL ADD after shipping address widget')
    else:
        replace_error = True
        lines.append('  Shipping ID/VAT lines: FAIL - insertion point not found')
lines.append('')

# Field preflight for referenced fields.
field_checks = [
    ['res.partner', 'commercial_partner_id'],
    ['res.partner', 'company_registry'],
    ['res.partner', 'vat'],
]
missing_field = False
lines.append('FIELD PREFLIGHT')
for fc in field_checks:
    cnt = Field.search_count([('model', '=', fc[0]), ('name', '=', fc[1])])
    lines.append('  %s.%s: %s' % (fc[0], fc[1], 'PASS' if cnt else 'MISSING'))
    if not cnt:
        missing_field = True
lines.append('')

# Safety/self-check after patching.
all_bad = False
self_checks = [
    ['layout still standalone BARANI t-name', 'barani_commercial.external_layout_standard_titled' in new_layout_arch],
    ['body still standalone BARANI t-name', 'barani_commercial.report_saleorder_document' in new_body_arch],
    ['center duplicate title removed from layout', 'name="barani_doc_title"' not in new_layout_arch],
    ['right-side document title remains', '<t t-esc="barani_doc_title"/>: <span t-esc="barani_doc_number"/>' in new_layout_arch],
    ['Customer label red/colon present', 'name="barani_customer_label"' in new_body_arch and 'Customer:' in new_body_arch],
    ['Shipping label red/colon present', 'name="barani_shipping_label"' in new_body_arch and 'Shipping Address:' in new_body_arch],
    ['Customer ID/VAT present', 'barani_customer_id_line' in new_body_arch and 'barani_customer_vat_line' in new_body_arch],
    ['Shipping ID/VAT present', 'barani_shipping_id_line' in new_body_arch and 'barani_shipping_vat_line' in new_body_arch],
    ['does not call stock sale body', 'sale.report_saleorder_document' not in new_body_arch and 'sale.report_saleorder_document' not in new_layout_arch],
    ['does not call web.external_layout', 'web.external_layout' not in new_body_arch and 'web.external_layout' not in new_layout_arch],
    ['does not call account.document_tax_totals', 'account.document_tax_totals' not in new_body_arch and 'account.document_tax_totals' not in new_layout_arch],
    ['no explicit DDS prefix', 'dds_' not in new_body_arch and 'dds_' not in new_layout_arch],
    ['no Studio custom field path', 'x_studio_' not in new_body_arch and 'x_studio_' not in new_layout_arch and '.x_' not in new_body_arch and '.x_' not in new_layout_arch],
    ['no BRN prefix', 'brn_' not in new_body_arch and 'brn_' not in new_layout_arch],
]
lines.append('TEMPLATE SELF-CHECK')
for chk in self_checks:
    ok = chk[1]
    lines.append('  %s: %s' % (chk[0], 'PASS' if ok else 'FAIL'))
    if not ok:
        all_bad = True
lines.append('')

if replace_error or missing_field or all_bad:
    lines.append('ERROR: tune preflight failed. Refusing before any write.')
    text = NL.join(lines)
    start = (PAGE - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    raise UserError(('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s' % (PAGE, start, min(end, len(text)), len(text), 'YES' if end < len(text) else 'NO')) + NL + text[start:end])

lines.append('PLAN')
if layout_changed:
    lines.append('  - update layout view id=%s key=%s to remove centered duplicate title' % (layout_view.id, LAYOUT_VIEW_KEY))
else:
    lines.append('  - layout already has no centered duplicate title')
if body_changed:
    lines.append('  - update body view id=%s key=%s for red address labels and shipping ID/VAT' % (body_view.id, BODY_VIEW_KEY))
else:
    lines.append('  - body already contains L2 address markers')
lines.append('  - preserve right-side document title + number')
lines.append('  - preserve L1 Tel/Email/Notes/Payment-Terms fixes if present')
lines.append('  - keep existing report actions, wrappers, paperformat, stock Odoo/DDS untouched')
lines.append('  old layout arch length=%s new layout arch length=%s delta=%s' % (len(old_layout_arch), len(new_layout_arch), len(new_layout_arch) - len(old_layout_arch)))
lines.append('  old body arch length=%s new body arch length=%s delta=%s' % (len(old_body_arch), len(new_body_arch), len(new_body_arch) - len(old_body_arch)))
lines.append('')

if not APPLY:
    lines.append('DRY RUN COMPLETE: no writes performed.')
    lines.append('Set APPLY=True and CONFIRM=%s to apply.' % CONFIRM_TOKEN)
    text = NL.join(lines)
    start = (PAGE - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    raise UserError(('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s' % (PAGE, start, min(end, len(text)), len(text), 'YES' if end < len(text) else 'NO')) + NL + text[start:end])

if CONFIRM != CONFIRM_TOKEN:
    lines.append('ERROR: APPLY=True but CONFIRM does not match %s. Refusing.' % CONFIRM_TOKEN)
    text = NL.join(lines)
    start = (PAGE - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    raise UserError(('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s' % (PAGE, start, min(end, len(text)), len(text), 'YES' if end < len(text) else 'NO')) + NL + text[start:end])

try:
    env.cr.execute('SAVEPOINT sp_barani_commercial_tune_l2')
    if layout_changed or body_changed:
        if not Param.get_param(BACKUP_MARKER_KEY, ''):
            Param.set_param(BACKUP_LAYOUT_PARAMETER_KEY, old_layout_arch)
            Param.set_param(BACKUP_BODY_PARAMETER_KEY, old_body_arch)
            Param.set_param(BACKUP_MARKER_KEY, '1')
            lines.append('PASS: stored one-time pre-L2 layout/body arch backups.')
        else:
            lines.append('NOTE: pre-L2 backup marker already exists; not overwriting backup.')
        if layout_changed:
            layout_view.write({'arch_db': new_layout_arch})
            lines.append('PASS: updated layout view id=%s key=%s.' % (layout_view.id, LAYOUT_VIEW_KEY))
        if body_changed:
            body_view.write({'arch_db': new_body_arch})
            lines.append('PASS: updated body view id=%s key=%s.' % (body_view.id, BODY_VIEW_KEY))
    else:
        lines.append('PASS: no write needed; current views already contain L2 markers.')

    try:
        env.flush_all()
        env.invalidate_all()
    except AttributeError:
        View.flush_model()
        env.cache.invalidate()
    lines.append('PASS: flushed pending writes and invalidated cache where available.')

    check_layout = View.browse(layout_view.id)
    check_body = View.browse(body_view.id)
    check_layout_arch = check_layout.arch_db or ''
    check_body_arch = check_body.arch_db or ''
    if check_layout.inherit_id or check_body.inherit_id:
        raise Exception('layout/body became inherited; expected standalone')
    if 'name="barani_doc_title"' in check_layout_arch:
        raise Exception('center duplicate title still present after write')
    if '<t t-esc="barani_doc_title"/>: <span t-esc="barani_doc_number"/>' not in check_layout_arch:
        raise Exception('right-side document title+number missing after write')
    if 'name="barani_customer_label"' not in check_body_arch or 'name="barani_shipping_label"' not in check_body_arch:
        raise Exception('red address label markers missing after write')
    if 'barani_shipping_vat_line' not in check_body_arch or 'barani_shipping_id_line' not in check_body_arch:
        raise Exception('shipping ID/VAT markers missing after write')
    if 'sale.report_saleorder_document' in check_body_arch or 'web.external_layout' in check_body_arch or 'account.document_tax_totals' in check_body_arch:
        raise Exception('forbidden stock/DDS-prone report reference found after write')
    lines.append('PASS: read-back verification passed.')
    env.cr.execute('RELEASE SAVEPOINT sp_barani_commercial_tune_l2')
    lines.append('TUNE COMPLETE.')
    lines.append("TEST: Print Q/PF/SO with 2026+ actions. Confirm no centered duplicate title, red 'Customer:'/'Shipping Address:' labels, and Shipping Address ID/VAT where data exists.")
except Exception as e_apply:
    try:
        env.cr.execute('ROLLBACK TO SAVEPOINT sp_barani_commercial_tune_l2')
        env.cr.execute('RELEASE SAVEPOINT sp_barani_commercial_tune_l2')
        lines.append('PASS: rolled back savepoint after failure.')
    except Exception as e_rb:
        lines.append('ROLLBACK PROBLEM: %s' % str(e_rb)[:500])
    lines.append('TUNE FAILED: %s' % str(e_apply)[:1500])
    text = NL.join(lines)
    start = (PAGE - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    raise UserError(('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s' % (PAGE, start, min(end, len(text)), len(text), 'YES' if end < len(text) else 'NO')) + NL + text[start:end])

text = NL.join(lines)
Param.set_param(OUTPUT_PARAMETER_KEY, text)
param = Param.search([('key', '=', OUTPUT_PARAMETER_KEY)], limit=1)
action = {'type': 'ir.actions.act_window', 'name': ACTION_NAME, 'res_model': 'ir.config_parameter', 'view_mode': 'form', 'res_id': param.id, 'target': 'current'}
