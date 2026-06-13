# ============================================================================
# ACTION NAME : BARANI COMMERCIAL Q/SO/PF TUNE L1 — notes label, customer/delivery email, payment terms width
# MODEL       : Module (ir.module.module) or any model; selected records ignored.
# ACTION TO DO: Execute Python Code
# VISIBILITY  : Create/run from Settings > Technical > Server Actions. This
#               server action itself is normally run from its form. It updates
#               the existing BARANI sale.order PDF templates used by the Print
#               menu entries 'Quotation / Order — 2026+' and 'PRO-FORMA — 2026+'.
#
# OUTPUT      : APPLY=False dry-run output is raised via UserError and performs
#               no writes. APPLY=True stores technical output/backup in
#               ir.config_parameter while the template write remains gated by
#               APPLY and CONFIRM.
#
# PAGINATION  : PAGE/PAGE_SIZE control the dry-run dialog if output grows.
#
# PURPOSE     : Targeted body-template tune only. It does NOT reinstall the whole
#               commercial report family and does NOT touch stock Odoo/DDS/Studio
#               report actions or templates.
#
# CHANGES     :
#               1. Notes: o.note was already printed, but without a visible
#                  'Notes' heading. This tune adds a labelled Notes block so the
#                  order note is obvious in the PDF.
#               2. Customer block: add Tel and Email below the customer address,
#                  using partner phone/mobile/email with commercial-parent fallback.
#               3. Shipping Address block: add Tel and Email below the delivery
#                  address, using shipping contact phone/mobile/email with
#                  commercial-parent fallback.
#               4. Metadata row: widen Payment Terms from col-2 to col-4 and add
#                  a small right gutter so it does not run into Payment Method.
#
# SAFETY      : Standalone BARANI body view only:
#                 key = barani_commercial.report_saleorder_document
#               No create/unlink. One write to this view only, and only when
#               APPLY=True and CONFIRM='INSTALL_BARANI_COMMERCIAL_Q_SO_PF_TUNE_L1'.
#               A one-time backup of the current body arch is stored before write.
# ============================================================================

APPLY = False
CONFIRM = ''
PAGE = 1
PAGE_SIZE = 16000

CONFIRM_TOKEN = 'INSTALL_BARANI_COMMERCIAL_Q_SO_PF_TUNE_L1'
ACTION_NAME = 'BARANI COMMERCIAL Q/SO/PF TUNE L1 — notes/contact/payment-terms width'
OUTPUT_PARAMETER_KEY = 'barani.commercial_report.tune_l1.last_run'
BACKUP_PARAMETER_KEY = 'barani.commercial_report.backup.tune_l1.body.arch'
BACKUP_MARKER_KEY = 'barani.commercial_report.backup.tune_l1.body.marker'
BODY_VIEW_KEY = 'barani_commercial.report_saleorder_document'
SALE_WRAPPER_KEY = 'barani_commercial.report_saleorder'
PF_WRAPPER_KEY = 'barani_commercial.report_saleorder_proforma'
SALE_REPORT_KEY = SALE_WRAPPER_KEY
PF_REPORT_KEY = PF_WRAPPER_KEY

View = env['ir.ui.view'].sudo()
Report = env['ir.actions.report'].sudo()
Param = env['ir.config_parameter'].sudo()
Field = env['ir.model.fields'].sudo()

NL = chr(10)
lines = []
lines.append(ACTION_NAME)
lines.append('APPLY=%s CONFIRM=%s PAGE=%s PAGE_SIZE=%s' % (APPLY, CONFIRM, PAGE, PAGE_SIZE))
lines.append('Scope: targeted update to existing standalone BARANI sale.order body view only.')
lines.append('No stock Odoo/DDS/Studio actions/templates are touched.')
lines.append('')

body_views = View.search([('key', '=', BODY_VIEW_KEY), ('type', '=', 'qweb')])
sale_reports = Report.search([('report_name', '=', SALE_REPORT_KEY), ('model', '=', 'sale.order')])
pf_reports = Report.search([('report_name', '=', PF_REPORT_KEY), ('model', '=', 'sale.order')])

lines.append('DISCOVERY')
lines.append('  body views key=%s: %s' % (BODY_VIEW_KEY, len(body_views)))
lines.append('  sale reports report_name=%s: %s' % (SALE_REPORT_KEY, len(sale_reports)))
lines.append('  PF reports report_name=%s: %s' % (PF_REPORT_KEY, len(pf_reports)))
if len(body_views) != 1:
    lines.append('ERROR: expected exactly one BARANI commercial body view. Refusing.')
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
body_view = body_views[0]
old_arch = body_view.arch_db or ''
lines.append('  body view id=%s name=%r inherit_id=%s arch_len=%s write_date=%s' % (body_view.id, body_view.name, body_view.inherit_id.id if body_view.inherit_id else '', len(old_arch), body_view.write_date))
lines.append('')

if body_view.inherit_id:
    lines.append('ERROR: body view is inherited; expected standalone BARANI-owned body. Refusing.')
    text = NL.join(lines)
    start = (PAGE - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    raise UserError(('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s' % (PAGE, start, min(end, len(text)), len(text), 'YES' if end < len(text) else 'NO')) + NL + text[start:end])

# Current exact snippets from the Q-SO-PF-2026 production body. If a future body
# has drifted, the tune refuses instead of overwriting unrelated changes.
OLD_CUSTOMER_PAIR = '<div t-field="o.partner_id" t-options="{&quot;widget&quot;: &quot;contact&quot;, &quot;fields&quot;: [&quot;address&quot;, &quot;name&quot;], &quot;no_marker&quot;: true}"/>\n        <t t-set="barani_customer_partner" t-value="o.partner_id.commercial_partner_id or o.partner_id"/>'
NEW_CUSTOMER_PAIR = '<div t-field="o.partner_id" t-options="{&quot;widget&quot;: &quot;contact&quot;, &quot;fields&quot;: [&quot;address&quot;, &quot;name&quot;], &quot;no_marker&quot;: true}"/>\n        <t t-set="barani_customer_partner" t-value="o.partner_id.commercial_partner_id or o.partner_id"/>\n        <t t-set="barani_customer_phone" t-value="o.partner_id.phone or o.partner_id.mobile or barani_customer_partner.phone or barani_customer_partner.mobile"/>\n        <t t-set="barani_customer_email" t-value="o.partner_id.email or barani_customer_partner.email"/>\n        <div t-if="barani_customer_phone" name="barani_customer_tel_line" class="mt-1">Tel: <span t-esc="barani_customer_phone"/></div>\n        <div t-if="barani_customer_email" name="barani_customer_email_line">Email: <span t-esc="barani_customer_email"/></div>'

OLD_SHIPPING_WIDGET = '<div t-field="o.partner_shipping_id" t-options="{&quot;widget&quot;: &quot;contact&quot;, &quot;fields&quot;: [&quot;address&quot;, &quot;name&quot;], &quot;no_marker&quot;: true}"/>'
NEW_SHIPPING_WIDGET = '<div t-field="o.partner_shipping_id" t-options="{&quot;widget&quot;: &quot;contact&quot;, &quot;fields&quot;: [&quot;address&quot;, &quot;name&quot;], &quot;no_marker&quot;: true}"/>\n        <t t-set="barani_shipping_partner" t-value="o.partner_shipping_id"/>\n        <t t-set="barani_shipping_parent" t-value="barani_shipping_partner.commercial_partner_id or barani_shipping_partner"/>\n        <t t-set="barani_shipping_phone" t-value="barani_shipping_partner.phone or barani_shipping_partner.mobile or barani_shipping_parent.phone or barani_shipping_parent.mobile"/>\n        <t t-set="barani_shipping_email" t-value="barani_shipping_partner.email or barani_shipping_parent.email"/>\n        <div t-if="barani_shipping_phone" name="barani_shipping_tel_line" class="mt-1">Tel: <span t-esc="barani_shipping_phone"/></div>\n        <div t-if="barani_shipping_email" name="barani_shipping_email_line">Email: <span t-esc="barani_shipping_email"/></div>'

OLD_PAYMENT_TERMS_DIV = '<div class="col-2 mb-2" t-if="o.payment_term_id" name="payment_terms">'
NEW_PAYMENT_TERMS_DIV = '<div class="col-4 mb-2" t-if="o.payment_term_id" name="payment_terms" style="padding-right:12px;">'

OLD_NOTE_DIV = '<div t-if="not is_html_empty(o.note)" name="comment"><span t-field="o.note"/></div>'
NEW_NOTE_DIV = '<div t-if="not is_html_empty(o.note)" name="comment" style="margin-top:12px; font-size:10pt; line-height:1.25;">\n        <strong>Notes</strong>\n        <div name="barani_order_note_text" style="margin-top:2px;" t-field="o.note"/>\n      </div>'

new_arch = old_arch
replace_error = False
changed = False
lines.append('PATCH ANALYSIS')

if 'barani_customer_email_line' in new_arch and 'barani_customer_tel_line' in new_arch:
    lines.append('  customer Tel/Email block: already present')
else:
    if OLD_CUSTOMER_PAIR in new_arch:
        new_arch = new_arch.replace(OLD_CUSTOMER_PAIR, NEW_CUSTOMER_PAIR, 1)
        changed = True
        lines.append('  customer Tel/Email block: WILL ADD')
    else:
        replace_error = True
        lines.append('  customer Tel/Email block: FAIL - expected insertion point not found')

if 'barani_shipping_email_line' in new_arch and 'barani_shipping_tel_line' in new_arch:
    lines.append('  shipping Tel/Email block: already present')
else:
    if OLD_SHIPPING_WIDGET in new_arch:
        new_arch = new_arch.replace(OLD_SHIPPING_WIDGET, NEW_SHIPPING_WIDGET, 1)
        changed = True
        lines.append('  shipping Tel/Email block: WILL ADD')
    else:
        replace_error = True
        lines.append('  shipping Tel/Email block: FAIL - expected insertion point not found')

if 'barani_order_note_text' in new_arch and '<strong>Notes</strong>' in new_arch:
    lines.append('  Notes label block: already present')
else:
    if OLD_NOTE_DIV in new_arch:
        new_arch = new_arch.replace(OLD_NOTE_DIV, NEW_NOTE_DIV, 1)
        changed = True
        lines.append('  Notes label block: WILL ADD')
    else:
        replace_error = True
        lines.append('  Notes label block: FAIL - expected o.note block not found')

if 'name="payment_terms" style="padding-right:12px;"' in new_arch and 'class="col-4 mb-2" t-if="o.payment_term_id" name="payment_terms"' in new_arch:
    lines.append('  Payment Terms width: already col-4 with gutter')
else:
    if OLD_PAYMENT_TERMS_DIV in new_arch:
        new_arch = new_arch.replace(OLD_PAYMENT_TERMS_DIV, NEW_PAYMENT_TERMS_DIV, 1)
        changed = True
        lines.append('  Payment Terms width: WILL CHANGE col-2 -> col-4')
    else:
        replace_error = True
        lines.append('  Payment Terms width: FAIL - expected col-2 payment_terms div not found')
lines.append('')

# Field preflight for newly referenced fields.
field_checks = [
    ['res.partner', 'phone'],
    ['res.partner', 'mobile'],
    ['res.partner', 'email'],
    ['res.partner', 'commercial_partner_id'],
    ['sale.order', 'note'],
    ['sale.order', 'payment_term_id'],
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
    ['still standalone BARANI sale body t-name', 'barani_commercial.report_saleorder_document' in new_arch],
    ['does not call stock sale body', 'sale.report_saleorder_document' not in new_arch],
    ['does not call web.external_layout', 'web.external_layout' not in new_arch],
    ['does not call account.document_tax_totals', 'account.document_tax_totals' not in new_arch],
    ['no explicit DDS prefix', 'dds_' not in new_arch],
    ['no Studio custom field path', 'x_studio_' not in new_arch and '.x_' not in new_arch],
    ['no BRN prefix', 'brn_' not in new_arch],
    ['customer email/tel markers present', 'barani_customer_email_line' in new_arch and 'barani_customer_tel_line' in new_arch],
    ['shipping email/tel markers present', 'barani_shipping_email_line' in new_arch and 'barani_shipping_tel_line' in new_arch],
    ['Notes heading + o.note preserved', '<strong>Notes</strong>' in new_arch and 'barani_order_note_text' in new_arch and 'o.note' in new_arch],
    ['Payment Terms widened', 'class="col-4 mb-2" t-if="o.payment_term_id" name="payment_terms"' in new_arch],
]
lines.append('TEMPLATE SELF-CHECK')
for chk in self_checks:
    ok = chk[1]
    lines.append('  %s: %s' % (chk[0], 'PASS' if ok else 'FAIL'))
    if not ok:
        all_bad = True
lines.append('')

lines.append('OBSERVED NOTE BEHAVIOR')
lines.append('  The current attached Q20XXNNN PDFs already print sale.order note text below the totals;')
lines.append('  the missing piece is the visible Notes label/header. This tune preserves o.note and labels it.')
lines.append('')

if replace_error or missing_field or all_bad:
    lines.append('ERROR: tune preflight failed. Refusing before any write.')
    text = NL.join(lines)
    start = (PAGE - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    raise UserError(('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s' % (PAGE, start, min(end, len(text)), len(text), 'YES' if end < len(text) else 'NO')) + NL + text[start:end])

lines.append('PLAN')
if changed:
    lines.append('  - update body view id=%s key=%s only' % (body_view.id, BODY_VIEW_KEY))
    lines.append('  - add customer Tel/Email lines')
    lines.append('  - add shipping Tel/Email lines')
    lines.append('  - add visible Notes heading above o.note')
    lines.append('  - widen Payment Terms metadata column to col-4')
    lines.append('  - keep existing report actions, wrappers, layout, paperformat, stock Odoo/DDS untouched')
else:
    lines.append('  - no update needed; all tune markers already present')
lines.append('  old arch length=%s new arch length=%s delta=%s' % (len(old_arch), len(new_arch), len(new_arch) - len(old_arch)))
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
    env.cr.execute('SAVEPOINT sp_barani_commercial_tune_l1')
    if changed:
        if not Param.get_param(BACKUP_MARKER_KEY, ''):
            Param.set_param(BACKUP_PARAMETER_KEY, old_arch)
            Param.set_param(BACKUP_MARKER_KEY, '1')
            lines.append('PASS: stored one-time pre-tune body arch backup in %s.' % BACKUP_PARAMETER_KEY)
        else:
            lines.append('NOTE: pre-tune backup marker already exists; not overwriting backup.')
        body_view.write({'arch_db': new_arch})
        lines.append('PASS: updated body view id=%s key=%s.' % (body_view.id, BODY_VIEW_KEY))
    else:
        lines.append('PASS: no write needed; current body already contains tune markers.')

    try:
        env.flush_all()
        env.invalidate_all()
    except AttributeError:
        View.flush_model()
        env.cache.invalidate()
    lines.append('PASS: flushed pending writes and invalidated cache where available.')

    check_view = View.browse(body_view.id)
    check_arch = check_view.arch_db or ''
    if check_view.inherit_id:
        raise Exception('body view became inherited; expected standalone')
    if 'barani_customer_email_line' not in check_arch or 'barani_shipping_email_line' not in check_arch:
        raise Exception('contact email/tel markers missing after write')
    if 'barani_order_note_text' not in check_arch or '<strong>Notes</strong>' not in check_arch:
        raise Exception('Notes heading markers missing after write')
    if 'class="col-4 mb-2" t-if="o.payment_term_id" name="payment_terms"' not in check_arch:
        raise Exception('Payment Terms col-4 marker missing after write')
    if 'sale.report_saleorder_document' in check_arch or 'web.external_layout' in check_arch or 'account.document_tax_totals' in check_arch:
        raise Exception('forbidden stock/DDS-prone report reference found after write')
    lines.append('PASS: read-back verification passed.')
    env.cr.execute('RELEASE SAVEPOINT sp_barani_commercial_tune_l1')
    lines.append('TUNE COMPLETE.')
    lines.append('TEST: Print Q20XXNNN with both 2026+ actions. Confirm Customer and Shipping Address show Tel and Email when data exists, Notes is visibly labelled, and Payment Terms no longer runs into Payment Method.')
except Exception as e_apply:
    try:
        env.cr.execute('ROLLBACK TO SAVEPOINT sp_barani_commercial_tune_l1')
        env.cr.execute('RELEASE SAVEPOINT sp_barani_commercial_tune_l1')
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
