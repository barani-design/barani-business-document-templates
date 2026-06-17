# ============================================================================
# ACTION NAME : BARANI DELIVERY DOCS DEV STEP 30 — DB identity + template ids probe v5.0 READ-ONLY
# MODEL       : Module (ir.module.module) or any model; selected records ignored.
# ACTION TO DO: Execute Python Code
# RUN BY      : Settings -> Technical -> Actions -> Server Actions -> New/Run
# PURPOSE     : Verify which Odoo database/environment you are currently in and
#               list the BARANI Delivery Note / Picking Operations 2026+ template
#               artifact IDs present in THAT database. Helps avoid confusing
#               test/staging/prod because numeric record IDs differ by database.
#
# READ-ONLY   : Performs no create/write/unlink/set_param/commit. It only reads
#               metadata and raises UserError for paged output.
# SAFE_EVAL   : no import/def/lambda/comprehensions/with/getattr/hasattr/
#               setattr/eval/exec/open/dir/isinstance.
# ============================================================================

ACTION_NAME = 'BARANI DELIVERY DOCS DEV STEP 30 — DB identity + template ids probe v5.0 READ-ONLY'
READ_ONLY = True
PAGE = 1
PAGE_SIZE = 15000

DN_BODY_KEY = 'barani_delivery.report_delivery_note_2026'
DN_LAYOUT_KEY = 'barani_delivery.external_layout_delivery_2026'
SO_BRIDGE_KEY = 'barani_delivery.report_sale_order_delivery_note_2026'
PICKOPS_BODY_KEY = 'barani_delivery.report_picking_operations_2026'
PICKOPS_LAYOUT_KEY = 'barani_delivery.external_layout_picking_operations_2026'
DN_REPORT_NAME = 'barani_delivery.report_delivery_note_2026'
SO_REPORT_NAME = 'barani_delivery.report_sale_order_delivery_note_2026'
PICKOPS_REPORT_NAME = 'barani_delivery.report_picking_operations_2026'

lines = []
lines.append(ACTION_NAME)
lines.append('READ_ONLY=%s | OUTPUT_MODE=paged | PAGE=%s PAGE_SIZE=%s' % (READ_ONLY, PAGE, PAGE_SIZE))
lines.append('Purpose: identify current DB/environment and BARANI 2026+ report artifact IDs. No writes.')
lines.append('')

Param = env['ir.config_parameter'].sudo()
View = env['ir.ui.view'].sudo()
Report = env['ir.actions.report'].sudo()
Paper = env['report.paperformat'].sudo()

# ---------------------------------------------------------------------------
# 1) Environment identity.
# ---------------------------------------------------------------------------
lines.append('1) DATABASE / ENVIRONMENT IDENTITY')
dbname = ''
try:
    dbname = env.cr.dbname or ''
except Exception as e_db:
    dbname = 'UNAVAILABLE: %s' % e_db
lines.append('  env.cr.dbname: %s' % dbname)
lines.append('  web.base.url: %s' % (Param.get_param('web.base.url') or ''))
lines.append('  database.uuid: %s' % (Param.get_param('database.uuid') or ''))
lines.append('  database.create_date: %s' % (Param.get_param('database.create_date') or ''))
lines.append('  odoo.sh.project_id: %s' % (Param.get_param('odoo.sh.project_id') or ''))
lines.append('  odoo.sh.branch: %s' % (Param.get_param('odoo.sh.branch') or ''))
lines.append('')

# ---------------------------------------------------------------------------
# 2) User/company context.
# ---------------------------------------------------------------------------
lines.append('2) CURRENT USER / COMPANY')
lines.append("  user: id=%s name='%s' login='%s'" % (env.user.id, env.user.name or '', env.user.login or ''))
lines.append("  company: id=%s name='%s' vat='%s'" % (env.company.id, env.company.name or '', env.company.vat or ''))
lines.append('')

# ---------------------------------------------------------------------------
# 3) Stored IDs.
# ---------------------------------------------------------------------------
lines.append('3) BARANI STORED ID PARAMETERS')
dn_ids = Param.get_param('barani.delivery_note_2026.ids') or ''
so_ids = Param.get_param('barani.delivery_note_2026.sale_order_menu.ids') or ''
pick_ids = Param.get_param('barani.picking_operations_2026.ids') or ''
restore_current = Param.get_param('barani.delivery_docs_2026.restore_point.current') or ''
lines.append("  barani.delivery_note_2026.ids = '%s'" % dn_ids)
lines.append("  barani.delivery_note_2026.sale_order_menu.ids = '%s'" % so_ids)
lines.append("  barani.picking_operations_2026.ids = '%s'" % pick_ids)
lines.append("  barani.delivery_docs_2026.restore_point.current = '%s'" % restore_current)
lines.append('')

# ---------------------------------------------------------------------------
# 4) Artifact discovery by stable keys/report names.
# ---------------------------------------------------------------------------
lines.append('4) ARTIFACT DISCOVERY BY STABLE KEYS')
keys = [DN_BODY_KEY, DN_LAYOUT_KEY, SO_BRIDGE_KEY, PICKOPS_BODY_KEY, PICKOPS_LAYOUT_KEY]
for key in keys:
    recs = View.search([('key', '=', key)], order='id')
    ids_text = ''
    for rec in recs:
        if ids_text:
            ids_text += ','
        ids_text += str(rec.id)
    lines.append("  VIEW key=%s count=%s ids=%s" % (key, len(recs), ids_text))
    for rec in recs:
        lines.append("    id=%s name='%s' type=%s inherit_id=%s arch_chars=%s write_date=%s" % (rec.id, rec.name or '', rec.type or '', rec.inherit_id.id if rec.inherit_id else '', len(rec.arch_db or ''), rec.write_date))

report_names = [DN_REPORT_NAME, SO_REPORT_NAME, PICKOPS_REPORT_NAME]
for rname in report_names:
    reps = Report.search([('report_name', '=', rname)], order='id')
    ids_text = ''
    for rep in reps:
        if ids_text:
            ids_text += ','
        ids_text += str(rep.id)
    lines.append("  REPORT report_name=%s count=%s ids=%s" % (rname, len(reps), ids_text))
    for rep in reps:
        bind_model = ''
        if rep.binding_model_id:
            bind_model = rep.binding_model_id.model or ''
        lines.append("    id=%s name='%s' model=%s binding_model=%s paperformat=%s/%s" % (rep.id, rep.name or '', rep.model or '', bind_model, rep.paperformat_id.id if rep.paperformat_id else '', rep.paperformat_id.name if rep.paperformat_id else ''))

papers = Paper.search([('name', 'in', ['BARANI Delivery A4 7mm', 'BARANI Picking Operations A4 7mm'])], order='id')
ids_text = ''
for paper in papers:
    if ids_text:
        ids_text += ','
    ids_text += str(paper.id)
lines.append('  PAPERFORMAT count=%s ids=%s' % (len(papers), ids_text))
for paper in papers:
    lines.append("    id=%s name='%s' margins T/B/L/R=%s/%s/%s/%s header_spacing=%s dpi=%s" % (paper.id, paper.name or '', paper.margin_top, paper.margin_bottom, paper.margin_left, paper.margin_right, paper.header_spacing, paper.dpi))
lines.append('')

# ---------------------------------------------------------------------------
# 5) Interpretation help.
# ---------------------------------------------------------------------------
lines.append('5) INTERPRETATION')
lines.append('  Numeric IDs are database-local. They are not portable between test, staging, and production.')
lines.append('  Compare database identity using env.cr.dbname, web.base.url, and database.uuid, not only IDs.')
lines.append('  Compare templates by stable key/report_name and arch_chars/hash/export, not by assuming body id 2862 or 2929.')
lines.append('  If this DB shows DN body id=2929, it matches the repaired/test DB state used during recent staging work.')
lines.append('  If another DB shows DN body id=2862, that may be the earlier live/prod export state. That is not wrong by itself.')
lines.append('  Production apply scripts should discover by key/report_name and update the single matching view in that DB.')
lines.append('  Restore points are per database. A restore point created in test does not protect production.')
lines.append('')

# ---------------------------------------------------------------------------
# 6) Quick health summary.
# ---------------------------------------------------------------------------
lines.append('6) QUICK HEALTH SUMMARY')
blocked = False
for key in keys:
    recs = View.search([('key', '=', key)])
    if len(recs) != 1:
        blocked = True
        lines.append('  BLOCKER: expected exactly one view for key %s, found %s.' % (key, len(recs)))
for rname in report_names:
    reps = Report.search([('report_name', '=', rname)])
    if len(reps) != 1:
        blocked = True
        lines.append('  BLOCKER: expected exactly one report for report_name %s, found %s.' % (rname, len(reps)))
if not blocked:
    lines.append('  PASS: one view/report found for each BARANI 2026+ delivery/picking artifact key.')
lines.append('  read_only=True | blocked=%s' % blocked)
lines.append('')
lines.append('END OF READ-ONLY DB/TEMPLATE IDENTITY PROBE')

full = '\n'.join(lines)
start = (PAGE - 1) * PAGE_SIZE
end = PAGE * PAGE_SIZE
shown = full[start:end]
more = 'YES' if end < len(full) else 'NO'
header = []
header.append('============ PAGED OUTPUT ============')
header.append('FULL = %s chars | PAGE %s | SHOWING %s-%s | MORE REMAINS: %s' % (len(full), PAGE, start, min(end, len(full)), more))
header.append('======================================')
raise UserError('\n'.join(header) + '\n' + shown)
