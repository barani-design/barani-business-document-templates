# ============================================================================
# ACTION NAME : C20 PHASE A — BARANI invoice Preview qweb-html route SAFE
# MODEL       : Module (ir.module.module) recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
#
# PURPOSE     : Preserve the visible standard Accounting "Preview" button but
#               change its action from portal preview_invoice() to a hidden
#               qweb-html report action using:
#                   barani_vat.report_invoice_document_vat
#
# PRECONDITION:
#   - B10 restore point exists.
#   - C10 standard report relink is applied.
#   - P01 read-only Preview audit was reviewed.
#
# WRITES:
#   - creates one hidden ir.actions.report qweb-html action;
#   - creates one inherited account.move form view changing only the Preview
#     button's name/type/title attributes.
# ============================================================================

APPLY = False
CONFIRM = ''
CONFIRM_TOKEN = 'INSTALL_BARANI_INVOICE_PREVIEW_HTML_C20'
PAGE = 1
PAGE_SIZE = 60000

SNAPSHOT_CODE = 'pre_standard_relink_preview_2026_07_14'
PREFIX = 'barani.report_routing_preview.restore.' + SNAPSHOT_CODE
B10_MARKER = PREFIX + '.marker'
C10_MARKER = 'barani.report_routing_preview.c10.standard_relink.marker'
C20_MARKER = 'barani.report_routing_preview.c20.preview_html.marker'
OUT_KEY = 'barani.report_routing_preview.c20.preview_html.output'

PREVIEW_REPORT_NAME = 'BARANI Invoice Preview 2026+ (hidden)'
PREVIEW_VIEW_NAME = 'BARANI Account Move Preview -> VAT 2026+ HTML'
PREVIEW_VIEW_KEY = 'barani_runtime.account_move_preview_2026_button'
BARANI_VAT_REPORT_NAME = 'barani_vat.report_invoice_document_vat'
NL = chr(10)

Param = env['ir.config_parameter'].sudo()
Report = env['ir.actions.report'].sudo().with_context(active_test=False)
View = env['ir.ui.view'].sudo().with_context(active_test=False, lang=None)
Move = env['account.move'].sudo()

lines = []
lines.append('C20 PHASE A — BARANI invoice Preview qweb-html route SAFE')
lines.append('APPLY=%s CONFIRM_OK=%s PAGE=%s' % (
    APPLY, CONFIRM == CONFIRM_TOKEN, PAGE
))
lines.append('Target: existing Preview button -> hidden qweb-html action -> BARANI VAT body.')
lines.append('')

problems = 0
warnings = 0

if (Param.get_param(B10_MARKER) or '') != '1':
    lines.append('FAIL: B10 restore point marker missing.')
    problems = problems + 1
if (Param.get_param(C10_MARKER) or '') != '1':
    lines.append('FAIL: C10 standard report relink marker missing.')
    problems = problems + 1
if Param.get_param(C20_MARKER) == '1':
    lines.append('FAIL: C20 marker already exists. Verify or restore; do not create duplicate Preview records.')
    problems = problems + 1

vat_view = View.search([('type', '=', 'qweb'), ('key', '=', BARANI_VAT_REPORT_NAME)])
lines.append('BARANI VAT BODY count=%s' % len(vat_view))
if len(vat_view) != 1:
    lines.append('FAIL: expected exactly one BARANI VAT body view.')
    problems = problems + 1
else:
    arch = vat_view.arch_db or ''
    checks = [
        ('DD MON YYYY markers', 'barani_month_abbr_en' in arch),
        ('Payment Reference marker', 'barani_pdf_payment_ref' in arch),
        ('Credit Note marker', 'Original Payment Reference' in arch),
        ('DPI/payment evidence marker', 'Payment received' in arch),
    ]
    for ck in checks:
        lines.append('  %s: %s' % (ck[0], 'PASS' if ck[1] else 'FAIL'))
        if not ck[1]:
            problems = problems + 1
lines.append('')

existing_html = Report.search([
    ('model', '=', 'account.move'),
    ('report_type', '=', 'qweb-html'),
    '|',
    ('name', '=', PREVIEW_REPORT_NAME),
    ('report_name', '=', BARANI_VAT_REPORT_NAME),
], order='id asc')
existing_view = View.search([
    ('model', '=', 'account.move'),
    '|',
    ('key', '=', PREVIEW_VIEW_KEY),
    ('name', '=', PREVIEW_VIEW_NAME),
], order='id asc')
lines.append('COLLISION CHECK')
lines.append('  existing matching qweb-html actions=%s' % len(existing_html))
lines.append('  existing matching inherited views=%s' % len(existing_view))
if existing_html or existing_view:
    lines.append('FAIL: planned Preview action/view already exists. Reconcile P01 output before apply.')
    problems = problems + 1
lines.append('')

base_form = env.ref('account.view_move_form', raise_if_not_found=False)
if not base_form or base_form._name != 'ir.ui.view':
    lines.append('FAIL: account.view_move_form not found.')
    problems = problems + 1

effective_arch = ''
try:
    view_data = Move.get_view(view_type='form')
    effective_arch = (view_data or {}).get('arch') or ''
    lines.append('EFFECTIVE FORM len=%s' % len(effective_arch))
except Exception as exc:
    lines.append('FAIL: could not read effective account.move form: %s' % str(exc)[:500])
    problems = problems + 1

pos = effective_arch.find('name="preview_invoice"')
if pos == -1:
    pos = effective_arch.find("name='preview_invoice'")
snippet = ''
if pos != -1:
    snippet = effective_arch[max(0, pos - 350):min(len(effective_arch), pos + 800)]
lines.append('  Preview snippet=%r' % snippet.replace(NL, ' '))
if pos == -1 or ('type="object"' not in snippet and "type='object'" not in snippet):
    lines.append('FAIL: effective Preview button is not the audited standard object-method button.')
    problems = problems + 1
lines.append('')

standard_invoice_action = env.ref('account.account_invoices', raise_if_not_found=False)
if not standard_invoice_action or standard_invoice_action._name != 'ir.actions.report':
    lines.append('FAIL: account.account_invoices action missing.')
    problems = problems + 1
elif (standard_invoice_action.report_name or '') != BARANI_VAT_REPORT_NAME:
    lines.append('FAIL: C10 routing not present on account.account_invoices.')
    problems = problems + 1

lines.append('CREATE PLAN')
lines.append('  hidden qweb-html report action name=%r report_name=%s' % (
    PREVIEW_REPORT_NAME, BARANI_VAT_REPORT_NAME
))
lines.append('  inherited view name=%r key=%s inherit_id=%s priority=999' % (
    PREVIEW_VIEW_NAME, PREVIEW_VIEW_KEY, base_form.id if base_form else 0
))
lines.append('  QWeb body writes=0')
lines.append('  standard PDF action writes=0')
lines.append('  business record writes=0')
lines.append('  warnings=%s problems=%s' % (warnings, problems))

if problems:
    full = NL.join(lines)
    start = (PAGE - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    more = 'YES' if end < len(full) else 'NO'
    raise UserError(('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s%s%s' % (
        PAGE, start, min(end, len(full)), len(full), more, NL, full[start:end]
    ))[:90000])

if (not APPLY) or CONFIRM != CONFIRM_TOKEN:
    lines.append('')
    lines.append('DRY RUN COMPLETE: no writes performed.')
    lines.append('Apply only after P01 output and manual current Preview evidence are reviewed.')
    lines.append('Set APPLY=True and CONFIRM=%s to apply.' % CONFIRM_TOKEN)
    full2 = NL.join(lines)
    start2 = (PAGE - 1) * PAGE_SIZE
    end2 = start2 + PAGE_SIZE
    more2 = 'YES' if end2 < len(full2) else 'NO'
    raise UserError(('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s%s%s' % (
        PAGE, start2, min(end2, len(full2)), len(full2), more2, NL, full2[start2:end2]
    ))[:90000])

try:
    env.cr.execute('SAVEPOINT sp_barani_c20_preview')

    html_vals = {
        'name': PREVIEW_REPORT_NAME,
        'model': 'account.move',
        'report_type': 'qweb-html',
        'report_name': BARANI_VAT_REPORT_NAME,
        'report_file': BARANI_VAT_REPORT_NAME,
        'paperformat_id': standard_invoice_action.paperformat_id.id if standard_invoice_action.paperformat_id else False,
        'print_report_name': standard_invoice_action.print_report_name or False,
        'binding_model_id': False,
        'binding_type': 'report',
        'binding_view_types': 'form',
        'attachment_use': False,
        'multi': False,
    }
    html_action = Report.create(html_vals)

    preview_arch = '<data>' + NL
    preview_arch = preview_arch + '  <xpath expr="//button[@name=' + "'" + 'preview_invoice' + "'" + ' and @type=' + "'" + 'object' + "'" + ']" position="attributes">' + NL
    preview_arch = preview_arch + '    <attribute name="name">%s</attribute>' % html_action.id + NL
    preview_arch = preview_arch + '    <attribute name="type">action</attribute>' + NL
    preview_arch = preview_arch + '    <attribute name="title">Preview BARANI 2026+ invoice</attribute>' + NL
    preview_arch = preview_arch + '  </xpath>' + NL
    preview_arch = preview_arch + '</data>'

    view_vals = {
        'name': PREVIEW_VIEW_NAME,
        'key': PREVIEW_VIEW_KEY,
        'type': 'form',
        'model': 'account.move',
        'inherit_id': base_form.id,
        'mode': 'extension',
        'priority': 999,
        'active': True,
        'arch_db': preview_arch,
    }
    preview_view = View.create(view_vals)

    env.flush_all()
    try:
        View.clear_caches()
    except Exception as cache1:
        View.invalidate_model()

    effective_after = (Move.get_view(view_type='form') or {}).get('arch') or ''
    action_marker = 'name="%s"' % html_action.id
    action_marker_alt = "name='%s'" % html_action.id
    if action_marker not in effective_after and action_marker_alt not in effective_after:
        raise Exception('effective Preview button does not reference created qweb-html action id=%s' % html_action.id)

    pos2 = effective_after.find(action_marker)
    if pos2 == -1:
        pos2 = effective_after.find(action_marker_alt)
    snippet2 = effective_after[max(0, pos2 - 350):min(len(effective_after), pos2 + 800)]
    if 'type="action"' not in snippet2 and "type='action'" not in snippet2:
        raise Exception('effective Preview button is not type=action after create')

    rb_action = Report.browse(html_action.id)
    rb_view = View.browse(preview_view.id)
    if rb_action.report_type != 'qweb-html' or rb_action.report_name != BARANI_VAT_REPORT_NAME or rb_action.binding_model_id:
        raise Exception('hidden qweb-html action read-back failed')
    if rb_view.inherit_id.id != base_form.id or not rb_view.active:
        raise Exception('Preview inherited view read-back failed')

    Param.set_param(C20_MARKER, '1')
    Param.set_param(C20_MARKER + '.report_action_id', str(html_action.id))
    Param.set_param(C20_MARKER + '.view_id', str(preview_view.id))
    if (Param.get_param(C20_MARKER) or '') != '1':
        raise Exception('C20 marker read-back failed')

    env.cr.execute('RELEASE SAVEPOINT sp_barani_c20_preview')
    lines.append('')
    lines.append('READ-BACK PASS: hidden BARANI qweb-html action id=%s' % html_action.id)
    lines.append('READ-BACK PASS: inherited Preview view id=%s' % preview_view.id)
    lines.append('READ-BACK PASS: effective Preview button is type=action and references the hidden BARANI action')
    lines.append('C20 COMPLETE: Accounting Preview now routes to BARANI RI/DPI/Credit Note HTML.')
    lines.append('NEXT: run V30 read-only and perform manual Print / Send & Print / email / Preview verification before hiding anything.')
except Exception as exc:
    try:
        env.cr.execute('ROLLBACK TO SAVEPOINT sp_barani_c20_preview')
        env.cr.execute('RELEASE SAVEPOINT sp_barani_c20_preview')
        try:
            env.invalidate_all()
        except Exception as inv1:
            try:
                env.cache.invalidate()
            except Exception as inv2:
                pass
    except Exception as rb:
        lines.append('ROLLBACK PROBLEM: %s' % str(rb)[:500])
    raise UserError((NL.join(lines) + NL + 'C20 APPLY FAILED AND ROLLED BACK: %s' % str(exc))[:90000])

text = NL.join(lines)[:90000]
Param.set_param(OUT_KEY, text)
out_rec = Param.search([('key', '=', OUT_KEY)], limit=1)
action = {
    'type': 'ir.actions.act_window',
    'name': 'C20 BARANI Preview result',
    'res_model': 'ir.config_parameter',
    'view_mode': 'form',
    'res_id': out_rec.id,
    'target': 'current',
}
