# ============================================================================
# ACTION NAME : BARANI DELIVERY DOCS DEV STEP 22 — create live 2026+ restore point v5.0 APPLY-SAFE
# MODEL       : Any model is acceptable; selected records are ignored.
# ACTION TO DO: Execute Python Code
# RUN BY      : Settings -> Technical -> Actions -> Server Actions -> Run
# PURPOSE     : Create an exact restore point for the installed BARANI 2026+
#               Delivery Note, Sales Order bridge, and Picking Operations QWeb
#               templates before applying DN L2/customs changes.
#
# SAFETY      : Write-capable but dry-run by default. In DRY_RUN=True it reads
#               and reports only. In apply mode it writes only ir.config_parameter
#               backup payloads and never writes business records.
# APPLY-SAFE  : In successful apply mode it stores full output in a parameter and
#               opens that parameter, avoiding rollback-causing UserError.
# ============================================================================

ACTION_NAME = 'BARANI DELIVERY DOCS DEV STEP 22 — create live 2026+ restore point v5.0 APPLY-SAFE'
DRY_RUN = True
CONFIRM = ''
PAGE = 1
PAGE_SIZE = 15000
OUTPUT_MODE = 'paged'
CONFIRM_TOKEN = 'CREATE_DN_PICKOPS_2026_RESTORE_POINT'
LAST_RUN_KEY = 'barani.delivery_docs_2026.restore_point.last_run'
BASE_KEY = 'barani.delivery_docs_2026.restore_point.'

DN_BODY_KEY = 'barani_delivery.report_delivery_note_2026'
DN_LAYOUT_KEY = 'barani_delivery.external_layout_delivery_2026'
SO_BRIDGE_KEY = 'barani_delivery.report_sale_order_delivery_note_2026'
PICKOPS_BODY_KEY = 'barani_delivery.report_picking_operations_2026'
PICKOPS_LAYOUT_KEY = 'barani_delivery.external_layout_picking_operations_2026'

DN_IDS_PARAM = 'barani.delivery_note_2026.ids'
SO_IDS_PARAM = 'barani.delivery_note_2026.sale_order_menu.ids'
PICKOPS_IDS_PARAM = 'barani.picking_operations_2026.ids'

lines = []
lines.append(ACTION_NAME)
lines.append("DRY_RUN=%s | CONFIRM=%r | OUTPUT_MODE=%s | PAGE=%s PAGE_SIZE=%s" % (DRY_RUN, CONFIRM, OUTPUT_MODE, PAGE, PAGE_SIZE))
lines.append('Scope: restore-point backup for BARANI-owned 2026+ report templates only. No business data writes.')
lines.append('')

View = env['ir.ui.view'].sudo()
Report = env['ir.actions.report'].sudo()
Paper = env['report.paperformat'].sudo()
Param = env['ir.config_parameter'].sudo()

# ---------------------------------------------------------------------------
# TEST 0 — savepoint/cache mechanism
# ---------------------------------------------------------------------------
manual_sp_ok = False
cache_inv_method = ''
lines.append('TEST 0 - manual SQL savepoint recovery + ORM cache invalidation')
try:
    env.cr.execute('SAVEPOINT t0_ok')
    env.cr.execute('SELECT 1')
    env.cr.execute('RELEASE SAVEPOINT t0_ok')
    env.cr.execute('SAVEPOINT t0_fail')
    try:
        env.cr.execute('SELECT * FROM __barani_missing_table_for_restore_probe__')
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
            env.cr.execute('SELECT 1')
            manual_sp_ok = True
            lines.append('PASS: SAVEPOINT recovery works; cache method=%s' % cache_inv_method)
except Exception as e0:
    lines.append('FATAL TEST 0: %s' % str(e0)[:500])
if not manual_sp_ok:
    lines.append('STOP: savepoint/cache mechanism unusable. No writes performed.')
    text = '\n'.join(lines)
    raise UserError(text[:60000])
lines.append('')

# ---------------------------------------------------------------------------
# Helpers inline: resolve by stored id first, key fallback, refuse duplicates.
# ---------------------------------------------------------------------------
blocked = False

dn_ids = Param.get_param(DN_IDS_PARAM, '') or ''
so_ids = Param.get_param(SO_IDS_PARAM, '') or ''
pickops_ids = Param.get_param(PICKOPS_IDS_PARAM, '') or ''
lines.append('1) STORED IDS')
lines.append("  %s = %r" % (DN_IDS_PARAM, dn_ids))
lines.append("  %s = %r" % (SO_IDS_PARAM, so_ids))
lines.append("  %s = %r" % (PICKOPS_IDS_PARAM, pickops_ids))
lines.append('')

# Stored ids are comma strings: DN body,report,paper,layout; SO view,report; PickOps body,report,paper,layout.
dn_body_id = 0
dn_report_id = 0
dn_paper_id = 0
dn_layout_id = 0
so_view_id = 0
so_report_id = 0
pick_body_id = 0
pick_report_id = 0
pick_paper_id = 0
pick_layout_id = 0
parts = dn_ids.split(',') if dn_ids else []
if len(parts) >= 4:
    try:
        dn_body_id = int(parts[0] or '0')
        dn_report_id = int(parts[1] or '0')
        dn_paper_id = int(parts[2] or '0')
        dn_layout_id = int(parts[3] or '0')
    except Exception:
        lines.append('  ERROR: failed parsing DN stored ids')
        blocked = True
parts = so_ids.split(',') if so_ids else []
if len(parts) >= 2:
    try:
        so_view_id = int(parts[0] or '0')
        so_report_id = int(parts[1] or '0')
    except Exception:
        lines.append('  ERROR: failed parsing SO stored ids')
        blocked = True
parts = pickops_ids.split(',') if pickops_ids else []
if len(parts) >= 4:
    try:
        pick_body_id = int(parts[0] or '0')
        pick_report_id = int(parts[1] or '0')
        pick_paper_id = int(parts[2] or '0')
        pick_layout_id = int(parts[3] or '0')
    except Exception:
        lines.append('  ERROR: failed parsing PickOps stored ids')
        blocked = True

# Resolve views. Stored id is preferred; if missing, fallback by key.
dn_body = View.browse(dn_body_id).exists() if dn_body_id else View.browse()
dn_layout = View.browse(dn_layout_id).exists() if dn_layout_id else View.browse()
so_view = View.browse(so_view_id).exists() if so_view_id else View.browse()
pick_body = View.browse(pick_body_id).exists() if pick_body_id else View.browse()
pick_layout = View.browse(pick_layout_id).exists() if pick_layout_id else View.browse()

if not dn_body:
    recs = View.search([('key', '=', DN_BODY_KEY)])
    if len(recs) == 1:
        dn_body = recs
    elif len(recs) > 1:
        lines.append('  ERROR: duplicate DN body views by key=%s ids=%s' % (DN_BODY_KEY, recs.ids))
        blocked = True
if not dn_layout:
    recs = View.search([('key', '=', DN_LAYOUT_KEY)])
    if len(recs) == 1:
        dn_layout = recs
    elif len(recs) > 1:
        lines.append('  ERROR: duplicate DN layout views by key=%s ids=%s' % (DN_LAYOUT_KEY, recs.ids))
        blocked = True
if not so_view:
    recs = View.search([('key', '=', SO_BRIDGE_KEY)])
    if len(recs) == 1:
        so_view = recs
    elif len(recs) > 1:
        lines.append('  ERROR: duplicate SO bridge views by key=%s ids=%s' % (SO_BRIDGE_KEY, recs.ids))
        blocked = True
if not pick_body:
    recs = View.search([('key', '=', PICKOPS_BODY_KEY)])
    if len(recs) == 1:
        pick_body = recs
    elif len(recs) > 1:
        lines.append('  ERROR: duplicate PickOps body views by key=%s ids=%s' % (PICKOPS_BODY_KEY, recs.ids))
        blocked = True
if not pick_layout:
    recs = View.search([('key', '=', PICKOPS_LAYOUT_KEY)])
    if len(recs) == 1:
        pick_layout = recs
    elif len(recs) > 1:
        lines.append('  ERROR: duplicate PickOps layout views by key=%s ids=%s' % (PICKOPS_LAYOUT_KEY, recs.ids))
        blocked = True

# Resolve reports/paperformats for metadata only.
dn_report = Report.browse(dn_report_id).exists() if dn_report_id else Report.search([('report_name', '=', DN_BODY_KEY)], limit=1)
so_report = Report.browse(so_report_id).exists() if so_report_id else Report.search([('report_name', '=', SO_BRIDGE_KEY)], limit=1)
pick_report = Report.browse(pick_report_id).exists() if pick_report_id else Report.search([('report_name', '=', PICKOPS_BODY_KEY)], limit=1)
dn_paper = Paper.browse(dn_paper_id).exists() if dn_paper_id else Paper.search([('name', '=', 'BARANI Delivery A4 7mm')], limit=1)
pick_paper = Paper.browse(pick_paper_id).exists() if pick_paper_id else Paper.search([('name', '=', 'BARANI Picking Operations A4 7mm')], limit=1)

lines.append('2) ARTIFACT DISCOVERY / IDENTITY CHECK')
expected = [
    ('DN body', dn_body, DN_BODY_KEY),
    ('DN layout', dn_layout, DN_LAYOUT_KEY),
    ('SO bridge', so_view, SO_BRIDGE_KEY),
    ('PickOps body', pick_body, PICKOPS_BODY_KEY),
    ('PickOps layout', pick_layout, PICKOPS_LAYOUT_KEY),
]
for row in expected:
    label = row[0]
    rec = row[1]
    key = row[2]
    if not rec:
        lines.append('  %s: MISSING expected_key=%s' % (label, key))
        blocked = True
    else:
        ok = rec.key == key and rec.type == 'qweb' and not rec.inherit_id
        lines.append('  %s: id=%s key=%s type=%s inherit_id=%s arch_chars=%s identity=%s' % (label, rec.id, rec.key, rec.type, rec.inherit_id.id if rec.inherit_id else '', len(rec.arch_db or ''), 'PASS' if ok else 'FAIL'))
        if not ok:
            blocked = True
if dn_report:
    lines.append("  DN report: id=%s name=%r model=%s report_name=%s" % (dn_report.id, dn_report.name, dn_report.model, dn_report.report_name))
else:
    lines.append('  DN report: MISSING')
    blocked = True
if so_report:
    lines.append("  SO bridge report: id=%s name=%r model=%s report_name=%s" % (so_report.id, so_report.name, so_report.model, so_report.report_name))
else:
    lines.append('  SO bridge report: MISSING')
if pick_report:
    lines.append("  PickOps report: id=%s name=%r model=%s report_name=%s" % (pick_report.id, pick_report.name, pick_report.model, pick_report.report_name))
else:
    lines.append('  PickOps report: MISSING')
    blocked = True
lines.append('')

# Lint exact current arches before backup.
lines.append('3) LIGHTWEIGHT BACKUP LINT')
all_arch = ''
for row in expected:
    label = row[0]
    rec = row[1]
    if rec:
        arch = rec.arch_db or ''
        all_arch = all_arch + '\n' + arch
        dotless_count = 0
        pos = arch.find('t-field="')
        while pos >= 0:
            start = pos + 9
            end = arch.find('"', start)
            if end >= 0:
                expr = arch[start:end]
                if '.' not in expr:
                    dotless_count = dotless_count + 1
            pos = arch.find('t-field="', pos + 1)
        lines.append('  %s: chars=%s dotless_t_field=%s dds=%s brn=%s invoice_money_tokens=%s' % (
            label,
            len(arch),
            dotless_count,
            'YES' if 'dds_' in arch else 'NO',
            'YES' if 'brn_' in arch else 'NO',
            'YES' if ('partner_bank_id' in arch or 'payment_reference' in arch or 'amount_total' in arch or 'price_unit' in arch) else 'NO'
        ))
        if dotless_count or 'dds_' in arch or 'brn_' in arch:
            blocked = True
lines.append('')

# Make a DB timestamp tag. Fallback is manual constant if SQL fails.
tag = ''
try:
    env.cr.execute("SELECT to_char(now(), 'YYYYMMDD_HH24MISS')")
    tag = env.cr.fetchone()[0]
except Exception:
    tag = 'manual_restore_point'
tag = 'delivery_docs_2026_' + tag

# Build restore payload.
metadata = []
metadata.append('BARANI Delivery Docs 2026+ restore point')
metadata.append('tag=%s' % tag)
metadata.append('created_by_user=%s/%s' % (env.user.id, env.user.name))
metadata.append('dn_ids=%s' % dn_ids)
metadata.append('so_ids=%s' % so_ids)
metadata.append('pickops_ids=%s' % pickops_ids)
if dn_report:
    metadata.append("dn_report id=%s name=%r model=%s report_name=%s" % (dn_report.id, dn_report.name, dn_report.model, dn_report.report_name))
if so_report:
    metadata.append("so_report id=%s name=%r model=%s report_name=%s" % (so_report.id, so_report.name, so_report.model, so_report.report_name))
if pick_report:
    metadata.append("pick_report id=%s name=%r model=%s report_name=%s" % (pick_report.id, pick_report.name, pick_report.model, pick_report.report_name))
if dn_paper:
    metadata.append("dn_paper id=%s name=%r margins=%s/%s/%s/%s header_spacing=%s dpi=%s" % (dn_paper.id, dn_paper.name, dn_paper.margin_top, dn_paper.margin_bottom, dn_paper.margin_left, dn_paper.margin_right, dn_paper.header_spacing, dn_paper.dpi))
if pick_paper:
    metadata.append("pick_paper id=%s name=%r margins=%s/%s/%s/%s header_spacing=%s dpi=%s" % (pick_paper.id, pick_paper.name, pick_paper.margin_top, pick_paper.margin_bottom, pick_paper.margin_left, pick_paper.margin_right, pick_paper.header_spacing, pick_paper.dpi))
metadata_text = '\n'.join(metadata)

planned = []
if not blocked:
    planned.append((BASE_KEY + 'current', tag, 'Set current restore point tag'))
    planned.append((BASE_KEY + tag + '.meta', metadata_text, 'Restore point metadata'))
    planned.append((BASE_KEY + tag + '.dn_body_arch', dn_body.arch_db or '', 'DN body QWeb arch'))
    planned.append((BASE_KEY + tag + '.dn_layout_arch', dn_layout.arch_db or '', 'DN layout QWeb arch'))
    planned.append((BASE_KEY + tag + '.so_bridge_arch', so_view.arch_db or '', 'SO bridge QWeb arch'))
    planned.append((BASE_KEY + tag + '.pickops_body_arch', pick_body.arch_db or '', 'PickOps body QWeb arch'))
    planned.append((BASE_KEY + tag + '.pickops_layout_arch', pick_layout.arch_db or '', 'PickOps layout QWeb arch'))

lines.append('4) RESTORE POINT WRITE PLAN')
lines.append('  restore tag: %s' % tag)
for p in planned:
    lines.append('  PLAN param=%s chars=%s reason=%s' % (p[0], len(p[1] or ''), p[2]))
if blocked:
    lines.append('  BLOCKED: discovery/lint errors above. No restore point will be created.')
lines.append('')

lines.append('5) APPLY PLAN')
if blocked:
    lines.append('  BLOCKED: no writes performed.')
elif DRY_RUN:
    lines.append('  DRY RUN: no writes performed.')
    lines.append("  To create the restore point, set DRY_RUN=False and CONFIRM='%s'." % CONFIRM_TOKEN)
else:
    if CONFIRM != CONFIRM_TOKEN:
        lines.append("  BLOCKED: CONFIRM must be %r. No writes performed." % CONFIRM_TOKEN)
        blocked = True
    else:
        for p in planned:
            try:
                env.cr.execute('SAVEPOINT sp_param')
                Param.set_param(p[0], p[1])
                env.cr.execute('RELEASE SAVEPOINT sp_param')
                lines.append('  APPLIED param=%s chars=%s reason=%s' % (p[0], len(p[1] or ''), p[2]))
            except Exception as e_apply:
                try:
                    env.cr.execute('ROLLBACK TO SAVEPOINT sp_param')
                    env.cr.execute('RELEASE SAVEPOINT sp_param')
                    if cache_inv_method == 'env.invalidate_all':
                        env.invalidate_all()
                    else:
                        env.cache.invalidate()
                except Exception as e_rb:
                    lines.append('  ROLLBACK PROBLEM param=%s error=%s' % (p[0], str(e_rb)[:300]))
                lines.append('  APPLY FAILED param=%s error=%s' % (p[0], str(e_apply)[:500]))
                blocked = True
        if not blocked:
            lines.append('  PASS: restore point created. Current tag=%s' % tag)
            lines.append('  NEXT: run the restore script in DRY_RUN=True to verify it can see this tag before applying DN L2.')
lines.append('')
lines.append('SUMMARY')
lines.append('  planned_param_writes=%s | dry_run=%s | blocked=%s | cache_method=%s' % (len(planned), DRY_RUN, blocked, cache_inv_method))
lines.append('END OF RESTORE POINT CREATION')

text = '\n'.join(lines)

if (not DRY_RUN) and (not blocked) and CONFIRM == CONFIRM_TOKEN:
    Param.set_param(LAST_RUN_KEY, text)
    param = Param.search([('key', '=', LAST_RUN_KEY)], limit=1)
    action = {
        'type': 'ir.actions.act_window',
        'name': ACTION_NAME,
        'res_model': 'ir.config_parameter',
        'view_mode': 'form',
        'res_id': param.id,
        'target': 'current',
    }
else:
    full = text
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
    raise UserError(('\n'.join(head) + '\n' + body)[:60000])
