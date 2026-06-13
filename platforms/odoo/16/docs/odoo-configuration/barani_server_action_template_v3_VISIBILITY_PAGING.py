# ============================================================================
# ACTION NAME : TEMPLATE v3: BARANI Server Action - visibility + dry-run + savepoint + paging
# MODEL       : Choose the business model you are working on.
#               For generic probes, Model = Module (ir.module.module) is fine.
# ACTION TO DO: Execute Python Code
# CREATE AT   : Settings -> Technical -> Actions -> Server Actions -> New
# RUN BY      : Save, then either run directly from the Server Action form or
#               bind it with "Create Contextual Action" if contextual menu access
#               is useful and safe for this action.
# VISIBILITY  : Contextual Action-menu visibility depends on the Server Action
#               model and whether you create/bind a contextual action. Replace
#               this block in each real script with the exact user path. Examples:
#                 - Model=account.move + contextual action:
#                   Accounting -> Customers -> Invoices -> select invoice(s) ->
#                   Action menu.
#                 - Model=sale.order + contextual action:
#                   Sales -> Orders / Quotations -> select order(s) -> Action menu.
#                 - ir.actions.report print entries:
#                   appear in the model's Print menu, not the Action menu.
#                 - Module/unbound diagnostics:
#                   run from Settings -> Technical -> Actions -> Server Actions.
#               Do not bind installers/migrations into customer-facing menus.
# PAGINATION  : Keep PAGE/PAGE_SIZE on every probe. In paged mode, the footer
#               tells you whether more text remains. Change PAGE = 2, 3, ... and
#               rerun until MORE REMAINS: NO. UserError paging is zero-write.
#
# DEFAULT     : DRY_RUN = True. In dry-run mode the template only builds a plan
#               and reports it; it creates/writes/unlinks NO business records.
#               Set DRY_RUN = False only after reviewing the dry-run plan.
#
# *** MANDATORY RULE - WRITE-CAPABLE SCRIPTS MUST HAVE A WORKING DRY-RUN ***
#   Any script cloned from this template that performs ANY write (rec.write,
#   create, unlink, set_param on business data, posting, etc.) MUST:
#     (1) keep a real DRY_RUN flag defaulting to True;
#     (2) in DRY_RUN=True, build and report the FULL plan of intended writes
#         (record id, target field/value, reason) and execute NONE of them;
#     (3) gate every actual write behind `if not DRY_RUN:` so a dry-run pass
#         is guaranteed side-effect-free and can be tested safely first.
#   Pure read-only probes may state READ-ONLY:YES and omit fake dry-run branches.
#
# OUTPUT MODES (OUTPUT_MODE):
#   'paged' (DEFAULT) : zero-write. The full report is built in memory and
#                       delivered via UserError, sliced into PAGE_SIZE pages.
#   'param'           : writes the full report to ir.config_parameter under
#                       OUTPUT_PARAMETER_KEY and opens that form. This is a
#                       one-row WRITE, so it is not zero-write.
#
# SAFE_EVAL   : Avoids imports, def, lambda, comprehensions, getattr/hasattr/
#               setattr, eval/exec/open, and Python `with`. This template uses
#               explicit PostgreSQL SAVEPOINT / ROLLBACK / RELEASE and try/except
#               around test/apply blocks. For strict no-try read-only probes,
#               copy the no-try pattern from the VAT export probe.
#
# HOW TO ADAPT
# ------------
# 1) Set ACTION_NAME, TARGET_MODEL_NAME, TARGET_DOMAIN, OUTPUT_PARAMETER_KEY.
# 2) Replace VISIBILITY with the exact Odoo path for the model/action type.
# 3) Add detection logic in the BUILD PLAN section.
# 4) Add planned writes as tuples: (record, values, reason).
# 5) Run once with DRY_RUN=True; read all pages; copy into the ticket notes.
# 6) Only then set DRY_RUN=False and run on a tiny controlled selection.
# ============================================================================

ACTION_NAME = 'TEMPLATE v3: BARANI Server Action - visibility + dry-run + savepoint + paging'
DRY_RUN = True

# ---- output configuration ---------------------------------------------------
OUTPUT_MODE = 'paged'          # 'paged' (zero-write, default) or 'param' (writes log)
PAGE = 1                       # bump to 2,3,... when footer says MORE REMAINS: YES
PAGE_SIZE = 80000              # chars per page; public-repo standard page size
OUTPUT_PARAMETER_KEY = 'barani.server_action_template.last_run'  # used by 'param' mode

# ---- target configuration ---------------------------------------------------
TARGET_MODEL_NAME = 'account.move'
# Optional explicit domain. Leave empty to use selected records only.
# Example: [('name', 'in', ['INV-EXAMPLE', 'INV-EXAMPLE'])]
TARGET_DOMAIN = []

lines = []
lines.append(ACTION_NAME)
lines.append('DRY_RUN=%s | OUTPUT_MODE=%s | PAGE=%s' % (DRY_RUN, OUTPUT_MODE, PAGE))
lines.append('Target model: %s' % TARGET_MODEL_NAME)
lines.append('')

Param = env['ir.config_parameter'].sudo()

# ---------------------------------------------------------------------------
# TEST 0 - savepoint recovery + ORM cache invalidation (proves the mechanism
#          this build needs before any real work; sets cache_inv_method).
# ---------------------------------------------------------------------------
manual_sp_ok = False
cache_inv_method = ''
lines.append('TEST 0 - manual SQL savepoint recovery + ORM cache invalidation')
try:
    env.cr.execute('SAVEPOINT t0_ok')
    env.cr.execute('SELECT 1')
    env.cr.execute('RELEASE SAVEPOINT t0_ok')
    lines.append('PASS: SAVEPOINT + RELEASE works.')
    env.cr.execute('SAVEPOINT t0_fail')
    try:
        env.cr.execute('SELECT * FROM __barani_probe_missing_table__')
        env.cr.execute('RELEASE SAVEPOINT t0_fail')
    except Exception as e0_inner:
        env.cr.execute('ROLLBACK TO SAVEPOINT t0_fail')
        env.cr.execute('RELEASE SAVEPOINT t0_fail')
        try:
            env.invalidate_all()
            cache_inv_method = 'env.invalidate_all'
            lines.append('PASS: cache invalidation via env.invalidate_all().')
        except Exception as inv_a:
            try:
                env.cache.invalidate()
                cache_inv_method = 'env.cache.invalidate'
                lines.append('PASS: cache invalidation via env.cache.invalidate().')
            except Exception as inv_b:
                lines.append('FAIL: no cache invalidation method worked.')
        if cache_inv_method:
            env.cr.execute('SELECT 1')
            env['res.company'].sudo().search([], limit=1)
            manual_sp_ok = True
            lines.append('PASS: rolled back cleanly; SQL+ORM healthy.')
except Exception as e0:
    lines.append('FAIL: savepoint mechanism unusable. %s' % str(e0)[:400])

if not manual_sp_ok:
    lines.append('STOP: savepoint/cache mechanism unusable on this build.')
    raise UserError('\n'.join(lines)[:60000])
lines.append('')

# ---------------------------------------------------------------------------
# RECORD COLLECTION
# ---------------------------------------------------------------------------
lines.append('RECORD COLLECTION')
if TARGET_MODEL_NAME not in env:
    lines.append('ERROR: model is not registered: %s' % TARGET_MODEL_NAME)
    raise UserError('\n'.join(lines)[:60000])

Target = env[TARGET_MODEL_NAME].sudo()
candidate_records = Target.browse()

try:
    if records:
        if records._name == TARGET_MODEL_NAME:
            candidate_records = candidate_records | records.sudo()
            lines.append('Selected records included: %s' % len(records))
        else:
            lines.append('Selected records ignored: selected model=%s, target model=%s' % (records._name, TARGET_MODEL_NAME))
except Exception as e_records:
    lines.append('Selected-record inspection skipped/error: %s' % str(e_records))

if TARGET_DOMAIN:
    try:
        env.cr.execute('SAVEPOINT sp_domain')
        domain_records = Target.search(TARGET_DOMAIN, limit=500)
        candidate_records = candidate_records | domain_records
        lines.append('Domain records included: %s' % len(domain_records))
        env.cr.execute('RELEASE SAVEPOINT sp_domain')
    except Exception as e_domain:
        try:
            env.cr.execute('ROLLBACK TO SAVEPOINT sp_domain')
            env.cr.execute('RELEASE SAVEPOINT sp_domain')
            if cache_inv_method == 'env.invalidate_all':
                env.invalidate_all()
            else:
                env.cache.invalidate()
        except Exception as e_domain_rb:
            lines.append('Domain rollback/release problem: %s' % str(e_domain_rb))
        lines.append('Domain search failed: %s' % str(e_domain))

lines.append('Candidate count: %s' % len(candidate_records))
for rec in candidate_records:
    lines.append('  Candidate id=%s display=%s' % (rec.id, rec.display_name))
lines.append('')

# ---------------------------------------------------------------------------
# BUILD PLAN
# ---------------------------------------------------------------------------
# Add project-specific detection here. The default template makes no business
# changes. To adapt:
#   values = {'field_name': new_value}
#   planned_updates.append((rec, values, 'why this record needs changing'))
# For long reports, just keep appending to `lines`; paging handles length.
# ---------------------------------------------------------------------------
lines.append('BUILD PLAN')
planned_updates = []

for rec in candidate_records:
    lines.append('  INSPECT id=%s display=%s' % (rec.id, rec.display_name))
    # TODO: replace this placeholder with real detection logic.
    # values = {'some_field': 'some_value'}
    # planned_updates.append((rec, values, 'reason / ticket reference'))

lines.append('Planned business writes: %s' % len(planned_updates))
for plan in planned_updates:
    rec = plan[0]
    values = plan[1]
    reason = plan[2]
    lines.append('  PLAN id=%s display=%s values=%s reason=%s' % (rec.id, rec.display_name, values, reason))
lines.append('')

# ---------------------------------------------------------------------------
# APPLY PLAN  (each write isolated; rollback also invalidates the ORM cache)
# RULE: every real write lives under `if not DRY_RUN:` below. Do NOT move any
# write above this gate. If you add writes, they go here, never in BUILD PLAN.
# A write-capable clone must keep this DRY_RUN gate working (see header rule).
# ---------------------------------------------------------------------------
if DRY_RUN:
    lines.append('DRY RUN: no business records were modified.')
else:
    lines.append('APPLY MODE: applying planned writes.')
    for plan in planned_updates:
        rec = plan[0]
        values = plan[1]
        reason = plan[2]
        try:
            env.cr.execute('SAVEPOINT sp_apply')
            rec.write(values)
            env.cr.execute('RELEASE SAVEPOINT sp_apply')
            lines.append('  APPLIED id=%s display=%s values=%s reason=%s' % (rec.id, rec.display_name, values, reason))
        except Exception as e_apply:
            try:
                env.cr.execute('ROLLBACK TO SAVEPOINT sp_apply')
                env.cr.execute('RELEASE SAVEPOINT sp_apply')
                if cache_inv_method == 'env.invalidate_all':
                    env.invalidate_all()
                else:
                    env.cache.invalidate()
            except Exception as e_apply_rb:
                lines.append('  APPLY rollback/release problem id=%s: %s' % (rec.id, str(e_apply_rb)))
            lines.append('  APPLY FAILED id=%s display=%s error=%s' % (rec.id, rec.display_name, str(e_apply)))

lines.append('')
lines.append('SUMMARY')
lines.append('  candidates=%s | planned_writes=%s | dry_run=%s' % (len(candidate_records), len(planned_updates), DRY_RUN))
lines.append('  cache method: %s' % cache_inv_method)
lines.append('')
lines.append('END OF SERVER ACTION')

text = '\n'.join(lines)

# ---------------------------------------------------------------------------
# OUTPUT  ('paged' = zero-write UserError; 'param' = write log + open form)
# ---------------------------------------------------------------------------
if OUTPUT_MODE == 'param':
    Param.set_param(OUTPUT_PARAMETER_KEY, text)
    param = Param.search([('key', '=', OUTPUT_PARAMETER_KEY)], limit=1)
    action = {
        'type': 'ir.actions.act_window',
        'name': ACTION_NAME,
        'res_model': 'ir.config_parameter',
        'view_mode': 'form',
        'res_id': param.id,
        'target': 'current',
    }
else:
    # 'paged' (default) - zero-write paged delivery
    full = text
    full_len = len(full)
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
        body = full[start_idx:end_idx]
        if end_idx < full_len:
            more = 'YES'
    head = []
    head.append('============ PAGED OUTPUT ============')
    head.append('FULL = %s chars | PAGE %s of %s | SHOWING %s-%s | MORE REMAINS: %s' % (full_len, PAGE, pages_int, start_idx, end_idx, more))
    head.append('======================================')
    head.append('')
    raise UserError(('\n'.join(head) + body)[:60000])
