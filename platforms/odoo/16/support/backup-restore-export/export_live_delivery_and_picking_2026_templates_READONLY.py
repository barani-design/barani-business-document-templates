# ============================================================================
# ACTION NAME : READ-ONLY — BARANI live Delivery Note / Picking Operations
#               2026+ template export v5.0
# MODEL       : Any model is acceptable; selected records are ignored.
# ACTION TO DO: Execute Python Code
# RUN BY      : Settings -> Technical -> Actions -> Server Actions -> New/Run
# PURPOSE     : Pull the CURRENT live DB QWeb/report/paperformat artifacts for:
#                 - Delivery Note (DN) — 2026+ on stock.picking
#                 - sale.order bridge to Delivery Note (DN) — 2026+
#                 - Picking Operations — 2026+ on stock.picking
#               so canonical scripts/GitHub can be reconciled from the real DB.
#
# READ-ONLY   : Performs NO create/write/unlink/set_param/commit/SQL. It only
#               reads ir.ui.view, ir.actions.report, report.paperformat, and
#               ir.config_parameter, then raises UserError for paged output.
# PAGINATION  : If MORE REMAINS: YES, set PAGE = 2, 3, ... and rerun.
# SAFE_EVAL   : no import / def / lambda / comprehension / with / getattr /
#               hasattr / setattr / eval / exec / open / dir / isinstance.
# ============================================================================

ACTION_NAME = 'READ-ONLY — BARANI live Delivery Note / Picking Operations 2026+ template export v5.0'
READ_ONLY = True
OUTPUT_MODE = 'paged'
PAGE = 1
PAGE_SIZE = 45000

# Selector: 'all' | 'dn' | 'so_bridge' | 'pickops' | 'metadata'
WHICH = 'all'

DN_IDS_KEY = 'barani.delivery_note_2026.ids'
DN_BODY_KEY = 'barani_delivery.report_delivery_note_2026'
DN_LAYOUT_KEY = 'barani_delivery.external_layout_delivery_2026'
DN_REPORT_NAME = 'Delivery Note (DN) — 2026+'
DN_PAPER_NAME = 'BARANI Delivery A4 7mm'

SO_IDS_KEY = 'barani.delivery_note_2026.sale_order_menu.ids'
SO_WRAPPER_KEY = 'barani_delivery.report_sale_order_delivery_note_2026'
SO_REPORT_NAME = 'Delivery Note (DN) — 2026+'

PICK_IDS_KEY = 'barani.picking_operations_2026.ids'
PICK_BODY_KEY = 'barani_delivery.report_picking_operations_2026'
PICK_LAYOUT_KEY = 'barani_delivery.external_layout_picking_operations_2026'
PICK_REPORT_NAME = 'Picking Operations — 2026+'
PICK_PAPER_NAME = 'BARANI Picking Operations A4 7mm'

View = env['ir.ui.view'].sudo()
Report = env['ir.actions.report'].sudo()
Paper = env['report.paperformat'].sudo()
Param = env['ir.config_parameter'].sudo()
Model = env['ir.model'].sudo()

lines = []
lines.append(ACTION_NAME)
lines.append('READ_ONLY=%s | OUTPUT_MODE=%s | WHICH=%r | PAGE=%s PAGE_SIZE=%s' % (READ_ONLY, OUTPUT_MODE, WHICH, PAGE, PAGE_SIZE))
lines.append('No writes. Copy XML between BEGIN/END markers into the repo/canonical installer worktree.')
lines.append('')

valid = False
for opt in ['all', 'dn', 'so_bridge', 'pickops', 'metadata']:
    if WHICH == opt:
        valid = True
if not valid:
    lines.append("ERROR: WHICH must be 'all', 'dn', 'so_bridge', 'pickops', or 'metadata'.")
    raise UserError('\n'.join(lines)[:60000])

# ---------------------------------------------------------------------------
# Resolve models.
# ---------------------------------------------------------------------------
stock_model = Model.search([('model', '=', 'stock.picking')], limit=1)
sale_model = Model.search([('model', '=', 'sale.order')], limit=1)
lines.append('MODEL IDS')
lines.append('  stock.picking: %s' % (stock_model.id if stock_model else 'MISSING'))
lines.append('  sale.order:    %s' % (sale_model.id if sale_model else 'MISSING'))
lines.append('')

# ---------------------------------------------------------------------------
# Discovery helpers in explicit blocks; no def/hasattr/list comprehensions.
# ---------------------------------------------------------------------------
lines.append('STORED IDS')
for key in [DN_IDS_KEY, SO_IDS_KEY, PICK_IDS_KEY]:
    val = Param.get_param(key, '') or ''
    lines.append('  %s = %r' % (key, val))
lines.append('')

# DN artifacts.
dn_body = View.search([('key', '=', DN_BODY_KEY)])
dn_layout = View.search([('key', '=', DN_LAYOUT_KEY)])
dn_reports_by_tech = Report.search([('report_name', '=', DN_BODY_KEY)])
dn_reports_by_name = Report.search([('name', '=', DN_REPORT_NAME), ('model', '=', 'stock.picking')])
dn_reports = dn_reports_by_tech | dn_reports_by_name
dn_papers = Paper.search([('name', '=', DN_PAPER_NAME)])

# SO bridge artifacts.
so_view = View.search([('key', '=', SO_WRAPPER_KEY)])
so_reports_by_tech = Report.search([('report_name', '=', SO_WRAPPER_KEY)])
so_reports_by_name = Report.search([('name', '=', SO_REPORT_NAME), ('model', '=', 'sale.order')])
so_reports = so_reports_by_tech | so_reports_by_name

# Picking Operations artifacts.
pick_body = View.search([('key', '=', PICK_BODY_KEY)])
pick_layout = View.search([('key', '=', PICK_LAYOUT_KEY)])
pick_reports_by_tech = Report.search([('report_name', '=', PICK_BODY_KEY)])
pick_reports_by_name = Report.search([('name', '=', PICK_REPORT_NAME), ('model', '=', 'stock.picking')])
pick_reports = pick_reports_by_tech | pick_reports_by_name
pick_papers = Paper.search([('name', '=', PICK_PAPER_NAME)])

dn_body_ids = ''
for rec_id in dn_body.ids:
    dn_body_ids = (dn_body_ids + ',' if dn_body_ids else '') + str(rec_id)
dn_layout_ids = ''
for rec_id in dn_layout.ids:
    dn_layout_ids = (dn_layout_ids + ',' if dn_layout_ids else '') + str(rec_id)
dn_report_ids = ''
for rec_id in dn_reports.ids:
    dn_report_ids = (dn_report_ids + ',' if dn_report_ids else '') + str(rec_id)
dn_paper_ids = ''
for rec_id in dn_papers.ids:
    dn_paper_ids = (dn_paper_ids + ',' if dn_paper_ids else '') + str(rec_id)
so_view_ids = ''
for rec_id in so_view.ids:
    so_view_ids = (so_view_ids + ',' if so_view_ids else '') + str(rec_id)
so_report_ids = ''
for rec_id in so_reports.ids:
    so_report_ids = (so_report_ids + ',' if so_report_ids else '') + str(rec_id)
pick_body_ids = ''
for rec_id in pick_body.ids:
    pick_body_ids = (pick_body_ids + ',' if pick_body_ids else '') + str(rec_id)
pick_layout_ids = ''
for rec_id in pick_layout.ids:
    pick_layout_ids = (pick_layout_ids + ',' if pick_layout_ids else '') + str(rec_id)
pick_report_ids = ''
for rec_id in pick_reports.ids:
    pick_report_ids = (pick_report_ids + ',' if pick_report_ids else '') + str(rec_id)
pick_paper_ids = ''
for rec_id in pick_papers.ids:
    pick_paper_ids = (pick_paper_ids + ',' if pick_paper_ids else '') + str(rec_id)

lines.append('ARTIFACT COUNTS')
lines.append('  DN body views:       %s ids=%s' % (len(dn_body), dn_body_ids))
lines.append('  DN layout views:     %s ids=%s' % (len(dn_layout), dn_layout_ids))
lines.append('  DN reports:          %s ids=%s' % (len(dn_reports), dn_report_ids))
lines.append('  DN papers:           %s ids=%s' % (len(dn_papers), dn_paper_ids))
lines.append('  SO bridge views:     %s ids=%s' % (len(so_view), so_view_ids))
lines.append('  SO bridge reports:   %s ids=%s' % (len(so_reports), so_report_ids))
lines.append('  PickOps body views:  %s ids=%s' % (len(pick_body), pick_body_ids))
lines.append('  PickOps layout views:%s ids=%s' % (len(pick_layout), pick_layout_ids))
lines.append('  PickOps reports:     %s ids=%s' % (len(pick_reports), pick_report_ids))
lines.append('  PickOps papers:      %s ids=%s' % (len(pick_papers), pick_paper_ids))
lines.append('')

blocked = False
if len(dn_body) > 1:
    blocked = True
    lines.append('BLOCKER: duplicate DN body views with key=%s.' % DN_BODY_KEY)
if len(dn_layout) > 1:
    blocked = True
    lines.append('BLOCKER: duplicate DN layout views with key=%s.' % DN_LAYOUT_KEY)
if len(dn_reports) > 1:
    # This can be normal if union includes same record once; Odoo union de-dupes.
    blocked = True
    lines.append('BLOCKER: duplicate DN stock.picking report actions for %s.' % DN_BODY_KEY)
if len(so_view) > 1:
    blocked = True
    lines.append('BLOCKER: duplicate SO bridge views with key=%s.' % SO_WRAPPER_KEY)
if len(so_reports) > 1:
    blocked = True
    lines.append('BLOCKER: duplicate SO bridge report actions for %s.' % SO_WRAPPER_KEY)
if len(pick_body) > 1:
    blocked = True
    lines.append('BLOCKER: duplicate Picking Operations body views with key=%s.' % PICK_BODY_KEY)
if len(pick_layout) > 1:
    blocked = True
    lines.append('BLOCKER: duplicate Picking Operations layout views with key=%s.' % PICK_LAYOUT_KEY)
if len(pick_reports) > 1:
    blocked = True
    lines.append('BLOCKER: duplicate Picking Operations report actions for %s.' % PICK_BODY_KEY)

if blocked:
    lines.append('STOP: duplicate/collision state detected. Export continues below where singleton-safe, but canonical installer should not be generated until resolved.')
lines.append('')

# ---------------------------------------------------------------------------
# Metadata details.
# ---------------------------------------------------------------------------
lines.append('REPORT / PAPER METADATA')
for rep in dn_reports:
    lines.append("  DN REPORT id=%s name=%r model=%s report_name=%s binding=%s/%s paper=%s/%s groups=%s" % (
        rep.id, rep.name, rep.model, rep.report_name,
        rep.binding_model_id.id if rep.binding_model_id else '',
        rep.binding_model_id.model if rep.binding_model_id else '',
        rep.paperformat_id.id if rep.paperformat_id else '',
        rep.paperformat_id.name if rep.paperformat_id else '',
        ','.join(rep.groups_id.mapped('name')) if rep.groups_id else 'none'
    ))
for rep in so_reports:
    lines.append("  SO REPORT id=%s name=%r model=%s report_name=%s binding=%s/%s paper=%s/%s groups=%s" % (
        rep.id, rep.name, rep.model, rep.report_name,
        rep.binding_model_id.id if rep.binding_model_id else '',
        rep.binding_model_id.model if rep.binding_model_id else '',
        rep.paperformat_id.id if rep.paperformat_id else '',
        rep.paperformat_id.name if rep.paperformat_id else '',
        ','.join(rep.groups_id.mapped('name')) if rep.groups_id else 'none'
    ))
for rep in pick_reports:
    lines.append("  PICKOPS REPORT id=%s name=%r model=%s report_name=%s binding=%s/%s paper=%s/%s groups=%s" % (
        rep.id, rep.name, rep.model, rep.report_name,
        rep.binding_model_id.id if rep.binding_model_id else '',
        rep.binding_model_id.model if rep.binding_model_id else '',
        rep.paperformat_id.id if rep.paperformat_id else '',
        rep.paperformat_id.name if rep.paperformat_id else '',
        ','.join(rep.groups_id.mapped('name')) if rep.groups_id else 'none'
    ))
for paper in dn_papers | pick_papers:
    lines.append("  PAPER id=%s name=%r margins T/B/L/R=%s/%s/%s/%s header_spacing=%s dpi=%s" % (
        paper.id, paper.name, paper.margin_top, paper.margin_bottom, paper.margin_left, paper.margin_right, paper.header_spacing, paper.dpi
    ))
lines.append('')

# ---------------------------------------------------------------------------
# Lightweight lint against known regressions.
# ---------------------------------------------------------------------------
lines.append('LIGHTWEIGHT TEMPLATE LINT')
for item in [('DN_BODY', dn_body), ('DN_LAYOUT', dn_layout), ('SO_BRIDGE', so_view), ('PICKOPS_BODY', pick_body), ('PICKOPS_LAYOUT', pick_layout)]:
    label = item[0]
    recs = item[1]
    if len(recs) == 1:
        arch = recs.arch_db or ''
        dotless_count = 0
        pos = arch.find('t-field="')
        while pos >= 0:
            start = pos + len('t-field="')
            end = arch.find('"', start)
            expr = arch[start:end] if end >= 0 else ''
            if expr and '.' not in expr:
                dotless_count = dotless_count + 1
            pos = arch.find('t-field="', start + 1)
        lines.append('  %s id=%s arch_chars=%s dotless_t_field=%s dds=%s brn=%s invoice_money_tokens=%s' % (
            label, recs.id, len(arch), dotless_count,
            'YES' if 'dds_' in arch else 'NO',
            'YES' if 'brn_' in arch else 'NO',
            'YES' if ('payment_reference' in arch or 'amount_total' in arch or 'partner_bank_id' in arch) else 'NO'
        ))
    else:
        lines.append('  %s count=%s: not linted as singleton' % (label, len(recs)))
lines.append('')

# ---------------------------------------------------------------------------
# Export XML payloads.
# ---------------------------------------------------------------------------
want_dn = False
want_so = False
want_pick = False
if WHICH == 'all' or WHICH == 'dn':
    want_dn = True
if WHICH == 'all' or WHICH == 'so_bridge':
    want_so = True
if WHICH == 'all' or WHICH == 'pickops':
    want_pick = True

if want_dn:
    lines.append('============================================================')
    lines.append('BEGIN DN_BODY_ARCH key=%s' % DN_BODY_KEY)
    lines.append('============================================================')
    if len(dn_body) == 1:
        lines.append('view_id=%s write_date=%s length=%s chars' % (dn_body.id, dn_body.write_date, len(dn_body.arch_db or '')))
        lines.append(dn_body.arch_db or '')
    else:
        lines.append('(DN body view not found as exactly one singleton)')
    lines.append('============================================================')
    lines.append('END DN_BODY_ARCH')
    lines.append('')

    lines.append('============================================================')
    lines.append('BEGIN DN_LAYOUT_ARCH key=%s' % DN_LAYOUT_KEY)
    lines.append('============================================================')
    if len(dn_layout) == 1:
        lines.append('view_id=%s write_date=%s length=%s chars' % (dn_layout.id, dn_layout.write_date, len(dn_layout.arch_db or '')))
        lines.append(dn_layout.arch_db or '')
    else:
        lines.append('(DN layout view not found as exactly one singleton)')
    lines.append('============================================================')
    lines.append('END DN_LAYOUT_ARCH')
    lines.append('')

if want_so:
    lines.append('============================================================')
    lines.append('BEGIN SO_BRIDGE_ARCH key=%s' % SO_WRAPPER_KEY)
    lines.append('============================================================')
    if len(so_view) == 1:
        lines.append('view_id=%s write_date=%s length=%s chars' % (so_view.id, so_view.write_date, len(so_view.arch_db or '')))
        lines.append(so_view.arch_db or '')
    else:
        lines.append('(SO bridge view not found as exactly one singleton)')
    lines.append('============================================================')
    lines.append('END SO_BRIDGE_ARCH')
    lines.append('')

if want_pick:
    lines.append('============================================================')
    lines.append('BEGIN PICKOPS_BODY_ARCH key=%s' % PICK_BODY_KEY)
    lines.append('============================================================')
    if len(pick_body) == 1:
        lines.append('view_id=%s write_date=%s length=%s chars' % (pick_body.id, pick_body.write_date, len(pick_body.arch_db or '')))
        lines.append(pick_body.arch_db or '')
    else:
        lines.append('(Picking Operations body view not found as exactly one singleton)')
    lines.append('============================================================')
    lines.append('END PICKOPS_BODY_ARCH')
    lines.append('')

    lines.append('============================================================')
    lines.append('BEGIN PICKOPS_LAYOUT_ARCH key=%s' % PICK_LAYOUT_KEY)
    lines.append('============================================================')
    if len(pick_layout) == 1:
        lines.append('view_id=%s write_date=%s length=%s chars' % (pick_layout.id, pick_layout.write_date, len(pick_layout.arch_db or '')))
        lines.append(pick_layout.arch_db or '')
    else:
        lines.append('(Picking Operations layout view not found as exactly one singleton)')
    lines.append('============================================================')
    lines.append('END PICKOPS_LAYOUT_ARCH')
    lines.append('')

lines.append('READ-ONLY EXPORT COMPLETE. No writes were performed.')
lines.append('Next: paste all pages here; then canonical repo scripts can be reconciled to these live DB templates before DN L2 work.')

full = '\n'.join(lines)
full_len = len(full)
pages = int(full_len / PAGE_SIZE)
if pages * PAGE_SIZE < full_len:
    pages = pages + 1
if pages < 1:
    pages = 1
start_idx = (PAGE - 1) * PAGE_SIZE
if start_idx < 0:
    start_idx = 0
end_idx = start_idx + PAGE_SIZE
more = 'NO'
if start_idx >= full_len:
    body = '(PAGE %s past end; full length %s chars.)' % (PAGE, full_len)
else:
    body = full[start_idx:end_idx]
    if end_idx < full_len:
        more = 'YES'
head = []
head.append('============ PAGED OUTPUT ============')
head.append('FULL = %s chars | PAGE %s of %s | SHOWING %s-%s | MORE REMAINS: %s' % (full_len, PAGE, pages, start_idx, end_idx, more))
head.append('======================================')
head.append('')
raise UserError(('\n'.join(head) + body)[:60000])
