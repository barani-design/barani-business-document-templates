# ============================================================================
# ACTION NAME : READ-ONLY: BARANI Delivery Note 2026 template export v2
# MODEL       : Any model; selected records ignored.
# ACTION TO DO: Execute Python Code
# PURPOSE     : Export the current stored QWeb XML for the isolated BARANI
#               Delivery Note 2026 body and custom layout views.
#
# READ-ONLY   : YES. Performs no create/write/unlink/set_param/commit/SQL.
# OUTPUT      : raises UserError with paged output.
# SAFE_EVAL   : no import/def/lambda/comprehension/with/getattr/hasattr/setattr/
#               eval/exec/open/dir/isinstance in executable code.
# ============================================================================

WHICH = 'both'  # both / body / layout
PAGE = 1
PAGE_SIZE = 80000
ACTION_NAME = 'READ-ONLY: BARANI Delivery Note 2026 template export v2'

BODY_KEY = 'barani_delivery.report_delivery_note_2026'
LAYOUT_KEY = 'barani_delivery.external_layout_delivery_2026'

View = env['ir.ui.view'].sudo()
Report = env['ir.actions.report'].sudo()
Paper = env['report.paperformat'].sudo()
Param = env['ir.config_parameter'].sudo()

lines = []
lines.append(ACTION_NAME)
lines.append('READ-ONLY:YES — search/read only; no writes. WHICH=%s PAGE=%s PAGE_SIZE=%s' % (WHICH, PAGE, PAGE_SIZE))
if WHICH not in ['both', 'body', 'layout']:
    raise UserError('Invalid WHICH; use both/body/layout')

body = View.search([('key', '=', BODY_KEY)])
layout = View.search([('key', '=', LAYOUT_KEY)])
if len(body) > 1 or len(layout) > 1:
    raise UserError('Duplicate BARANI delivery views; refusing export.')
report = Report.search([('report_name', '=', BODY_KEY), ('model', '=', 'stock.picking')])
if len(report) > 1:
    raise UserError('Duplicate BARANI delivery reports; refusing export.')

lines.append('BODY view: %s' % ('id=%s name=%r type=%s inherit=%s len=%s' % (body.id, body.name, body.type, bool(body.inherit_id), len(body.arch_db or '')) if body else 'MISSING'))
lines.append('LAYOUT view: %s' % ('id=%s name=%r type=%s inherit=%s len=%s' % (layout.id, layout.name, layout.type, bool(layout.inherit_id), len(layout.arch_db or '')) if layout else 'MISSING'))
lines.append('REPORT: %s' % ('id=%s name=%r report_name=%s paper=%s' % (report.id, report.name, report.report_name, report.paperformat_id.name if report.paperformat_id else '') if report else 'MISSING'))
lines.append('')
if WHICH in ['both', 'body']:
    lines.append('===== BEGIN DELIVERY_BODY_ARCH key=%s =====' % BODY_KEY)
    lines.append(body.arch_db or '' if body else '')
    lines.append('===== END DELIVERY_BODY_ARCH =====')
if WHICH in ['both', 'layout']:
    lines.append('===== BEGIN DELIVERY_LAYOUT_ARCH key=%s =====' % LAYOUT_KEY)
    lines.append(layout.arch_db or '' if layout else '')
    lines.append('===== END DELIVERY_LAYOUT_ARCH =====')
text = '\n'.join(lines)
start = (PAGE - 1) * PAGE_SIZE
end = start + PAGE_SIZE
slice_text = text[start:end]
more = 'YES' if end < len(text) else 'NO'
raise UserError('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s\n%s\n--- END PAGE %s | MORE REMAINS: %s ---' % (PAGE, start, min(end, len(text)), len(text), more, slice_text, PAGE, more))
