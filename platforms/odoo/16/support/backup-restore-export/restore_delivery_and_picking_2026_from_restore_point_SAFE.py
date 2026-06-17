# ============================================================================
# ACTION NAME : BARANI DELIVERY DOCS DEV STEP 23 — restore live 2026+ templates from restore point v5.0 APPLY-SAFE
# MODEL       : Any model is acceptable; selected records are ignored.
# ACTION TO DO: Execute Python Code
# RUN BY      : Settings -> Technical -> Actions -> Server Actions -> Run
# PURPOSE     : Restore BARANI-owned 2026+ Delivery Note, Sales Order bridge,
#               and Picking Operations QWeb templates from the current restore
#               point created by Step 22.
#
# SAFETY      : Write-capable but dry-run by default. In dry-run it reads and
#               reports only. In apply mode it writes only ir.ui.view.arch_db on
#               the five BARANI-owned QWeb views. No business data writes.
# APPLY-SAFE  : In successful apply mode it stores full output in a parameter and
#               opens that parameter, avoiding rollback-causing UserError.
# ============================================================================

ACTION_NAME = 'BARANI DELIVERY DOCS DEV STEP 23 — restore live 2026+ templates from restore point v5.0 APPLY-SAFE'
DRY_RUN = True
CONFIRM = ''
PAGE = 1
PAGE_SIZE = 15000
OUTPUT_MODE = 'paged'
CONFIRM_TOKEN = 'RESTORE_DN_PICKOPS_2026_FROM_RESTORE_POINT'
LAST_RUN_KEY = 'barani.delivery_docs_2026.restore_from_point.last_run'
BASE_KEY = 'barani.delivery_docs_2026.restore_point.'

DN_BODY_KEY = 'barani_delivery.report_delivery_note_2026'
DN_LAYOUT_KEY = 'barani_delivery.external_layout_delivery_2026'
SO_BRIDGE_KEY = 'barani_delivery.report_sale_order_delivery_note_2026'
PICKOPS_BODY_KEY = 'barani_delivery.report_picking_operations_2026'
PICKOPS_LAYOUT_KEY = 'barani_delivery.external_layout_picking_operations_2026'

lines = []
lines.append(ACTION_NAME)
lines.append("DRY_RUN=%s | CONFIRM=%r | OUTPUT_MODE=%s | PAGE=%s PAGE_SIZE=%s" % (DRY_RUN, CONFIRM, OUTPUT_MODE, PAGE, PAGE_SIZE))
lines.append('Scope: restore BARANI-owned 2026+ QWeb templates only. No business data writes.')
lines.append('')

View = env['ir.ui.view'].sudo()
Param = env['ir.config_parameter'].sudo()

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
    raise UserError('\n'.join(lines)[:60000])
lines.append('')

blocked = False

current_tag = Param.get_param(BASE_KEY + 'current', '') or ''
lines.append('1) RESTORE POINT DISCOVERY')
lines.append("  current tag=%r" % current_tag)
if not current_tag:
    lines.append('  ERROR: no current restore-point tag found. Run Step 22 first and apply it.')
    blocked = True

meta = Param.get_param(BASE_KEY + current_tag + '.meta', '') or '' if current_tag else ''
dn_body_arch = Param.get_param(BASE_KEY + current_tag + '.dn_body_arch', '') or '' if current_tag else ''
dn_layout_arch = Param.get_param(BASE_KEY + current_tag + '.dn_layout_arch', '') or '' if current_tag else ''
so_bridge_arch = Param.get_param(BASE_KEY + current_tag + '.so_bridge_arch', '') or '' if current_tag else ''
pick_body_arch = Param.get_param(BASE_KEY + current_tag + '.pickops_body_arch', '') or '' if current_tag else ''
pick_layout_arch = Param.get_param(BASE_KEY + current_tag + '.pickops_layout_arch', '') or '' if current_tag else ''

lines.append('  meta chars=%s' % len(meta or ''))
lines.append('  payload chars: dn_body=%s dn_layout=%s so_bridge=%s pick_body=%s pick_layout=%s' % (len(dn_body_arch or ''), len(dn_layout_arch or ''), len(so_bridge_arch or ''), len(pick_body_arch or ''), len(pick_layout_arch or '')))
if current_tag and meta:
    first_line = meta.split('\n')[0]
    lines.append('  meta first line: %s' % first_line)
for label, arch in [('dn_body_arch', dn_body_arch), ('dn_layout_arch', dn_layout_arch), ('so_bridge_arch', so_bridge_arch), ('pickops_body_arch', pick_body_arch), ('pickops_layout_arch', pick_layout_arch)]:
    if not arch:
        lines.append('  ERROR: missing restore payload %s' % label)
        blocked = True
lines.append('')

# Resolve exact targets by key. Refuse duplicates.
lines.append('2) TARGET DISCOVERY')
targets = []
for label, key, arch in [
    ('DN body', DN_BODY_KEY, dn_body_arch),
    ('DN layout', DN_LAYOUT_KEY, dn_layout_arch),
    ('SO bridge', SO_BRIDGE_KEY, so_bridge_arch),
    ('PickOps body', PICKOPS_BODY_KEY, pick_body_arch),
    ('PickOps layout', PICKOPS_LAYOUT_KEY, pick_layout_arch),
]:
    recs = View.search([('key', '=', key)])
    if len(recs) == 1:
        rec = recs
        ok = rec.type == 'qweb' and not rec.inherit_id
        lines.append('  %s: id=%s key=%s type=%s inherit_id=%s current_chars=%s identity=%s restore_chars=%s' % (label, rec.id, rec.key, rec.type, rec.inherit_id.id if rec.inherit_id else '', len(rec.arch_db or ''), 'PASS' if ok else 'FAIL', len(arch or '')))
        if not ok:
            blocked = True
        targets.append((label, rec, arch))
    elif len(recs) == 0:
        lines.append('  ERROR: %s target missing key=%s' % (label, key))
        blocked = True
    else:
        lines.append('  ERROR: %s duplicate targets key=%s ids=%s' % (label, key, recs.ids))
        blocked = True
lines.append('')

# Lint restore payload.
lines.append('3) RESTORE PAYLOAD SELF-CHECK')
for t in targets:
    label = t[0]
    arch = t[2] or ''
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
    key_ok = False
    if label == 'DN body' and 't-name="barani_delivery.report_delivery_note_2026"' in arch:
        key_ok = True
    if label == 'DN layout' and 't-name="barani_delivery.external_layout_delivery_2026"' in arch:
        key_ok = True
    if label == 'SO bridge' and 't-name="barani_delivery.report_sale_order_delivery_note_2026"' in arch:
        key_ok = True
    if label == 'PickOps body' and 't-name="barani_delivery.report_picking_operations_2026"' in arch:
        key_ok = True
    if label == 'PickOps layout' and 't-name="barani_delivery.external_layout_picking_operations_2026"' in arch:
        key_ok = True
    no_dds = 'dds_' not in arch
    no_brn = 'brn_' not in arch
    lines.append('  %s: t-name=%s dotless_t_field=%s dds=%s brn=%s' % (label, 'PASS' if key_ok else 'FAIL', dotless_count, 'NO' if no_dds else 'YES', 'NO' if no_brn else 'YES'))
    if not key_ok or dotless_count or not no_dds or not no_brn:
        blocked = True
lines.append('')

lines.append('4) RESTORE WRITE PLAN')
for t in targets:
    lines.append('  PLAN target=%s view_id=%s arch_chars=%s reason=Restore arch_db from current restore point %s' % (t[0], t[1].id, len(t[2] or ''), current_tag))
if blocked:
    lines.append('  BLOCKED: resolve errors above before restore. No writes will be performed.')
lines.append('')

lines.append('5) APPLY PLAN')
if blocked:
    lines.append('  BLOCKED: no writes performed.')
elif DRY_RUN:
    lines.append('  DRY RUN: no writes performed.')
    lines.append("  To restore, set DRY_RUN=False and CONFIRM='%s'." % CONFIRM_TOKEN)
else:
    if CONFIRM != CONFIRM_TOKEN:
        lines.append("  BLOCKED: CONFIRM must be %r. No writes performed." % CONFIRM_TOKEN)
        blocked = True
    else:
        for t in targets:
            label = t[0]
            rec = t[1]
            arch = t[2]
            try:
                env.cr.execute('SAVEPOINT sp_restore')
                rec.write({'arch_db': arch})
                env.cr.execute('RELEASE SAVEPOINT sp_restore')
                lines.append('  APPLIED target=%s view_id=%s arch_chars=%s' % (label, rec.id, len(arch or '')))
            except Exception as e_apply:
                try:
                    env.cr.execute('ROLLBACK TO SAVEPOINT sp_restore')
                    env.cr.execute('RELEASE SAVEPOINT sp_restore')
                    if cache_inv_method == 'env.invalidate_all':
                        env.invalidate_all()
                    else:
                        env.cache.invalidate()
                except Exception as e_rb:
                    lines.append('  ROLLBACK PROBLEM target=%s error=%s' % (label, str(e_rb)[:300]))
                lines.append('  APPLY FAILED target=%s error=%s' % (label, str(e_apply)[:500]))
                blocked = True
        if not blocked:
            # read-back
            lines.append('')
            lines.append('6) POST-WRITE READ-BACK')
            for t in targets:
                rec = t[1]
                expected_len = len(t[2] or '')
                actual_len = len(rec.arch_db or '')
                lines.append('  target=%s view_id=%s expected_chars=%s actual_chars=%s result=%s' % (t[0], rec.id, expected_len, actual_len, 'PASS' if expected_len == actual_len else 'CHECK'))
            lines.append('  PASS: restore completed. Test the stock.picking and sale.order Print menus before continuing.')
lines.append('')
lines.append('SUMMARY')
lines.append('  restore_tag=%s | planned_view_writes=%s | dry_run=%s | blocked=%s | cache_method=%s' % (current_tag, len(targets), DRY_RUN, blocked, cache_inv_method))
lines.append('END OF RESTORE')

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
