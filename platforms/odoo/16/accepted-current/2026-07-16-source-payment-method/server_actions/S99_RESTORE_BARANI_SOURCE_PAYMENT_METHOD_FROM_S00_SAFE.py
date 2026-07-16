# ============================================================================
# ACTION NAME : S99 RESTORE — BARANI Source / Payment Method from S00 SAFE
# MODEL       : Module (ir.module.module) recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
#
# PURPOSE
#   Restore the exact pre-S01/S02 commercial and VAT QWeb bytes captured by S00.
#
# NO TOUCH
#   Business records, report actions, Print menus, Preview, paperformats,
#   Delivery Note, stored Payment References, taxes, totals, or DDS fields.
# ============================================================================

APPLY = False
CONFIRM = ''
CONFIRM_TOKEN = 'RESTORE_BARANI_SOURCE_PAYMENT_METHOD_FROM_S00_S99'

S00_MARKER = 'barani.source_method.s00.restore.marker'
S01_MARKER = 'barani.source_method.s01.commercial.marker'
S02_MARKER = 'barani.source_method.s02.vat.marker'
RESTORE_MARKER = 'barani.source_method.s99.restored.marker'
OUTPUT_KEY = 'barani.source_method.s99.output'
PREFIX = 'barani.source_method.s00.restore.'

NL = chr(10)

Param = env['ir.config_parameter'].sudo()
View = env['ir.ui.view'].sudo().with_context(lang=None, active_test=False)

lines = []
lines.append('S99 RESTORE — BARANI Source / Payment Method from S00 SAFE')
lines.append('APPLY=%s CONFIRM_OK=%s' % (APPLY, CONFIRM == CONFIRM_TOKEN))
lines.append('Restores exact commercial and VAT QWeb bytes only.')
lines.append('')

problems = 0
rows = []

if Param.get_param(S00_MARKER) != '1':
    lines.append('FAIL: S00 restore marker missing.')
    problems = problems + 1

for token in ['commercial', 'vat']:
    rid = int(Param.get_param(PREFIX + 'view.' + token + '.id') or '0')
    key = Param.get_param(PREFIX + 'view.' + token + '.key') or ''
    name = Param.get_param(PREFIX + 'view.' + token + '.name') or ''
    arch = Param.get_param(PREFIX + 'view.' + token + '.arch') or ''
    active = Param.get_param(PREFIX + 'view.' + token + '.active') == '1'
    rec = View.browse(rid).exists() if rid else View.browse([])
    ok = bool(rec) and rec.key == key and bool(rec.active) == active and bool(arch)
    lines.append(
        '  token=%s id=%s key=%r exists=%s identity_ok=%s backup_len=%s'
        % (token, rid, key, bool(rec), ok, len(arch))
    )
    if not ok:
        problems = problems + 1
    else:
        rows.append((token, rec, name, arch))

if problems:
    lines.append('')
    lines.append('ERROR: %s preflight problem(s); no writes performed.' % problems)
    raise UserError(NL.join(lines)[:90000])

already_original = True
for token, rec, name, arch in rows:
    if (rec.arch_db or '') != arch or (rec.name or '') != name:
        already_original = False

if already_original:
    lines.append('')
    lines.append('NO-OP: both QWeb bodies already match the S00 restore baseline.')
    raise UserError(NL.join(lines)[:90000])

lines.append('')
lines.append('PLAN')
for token, rec, name, arch in rows:
    lines.append('  restore %s view id=%s current_len=%s backup_len=%s' % (
        token, rec.id, len(rec.arch_db or ''), len(arch)
    ))
lines.append('  preserve report routing, HTML Preview, paperformats, and business records')

if not APPLY or CONFIRM != CONFIRM_TOKEN:
    lines.append('')
    lines.append('DRY RUN — no writes performed.')
    lines.append('Apply with APPLY=True and CONFIRM=%s.' % CONFIRM_TOKEN)
    raise UserError(NL.join(lines)[:90000])

for token, rec, name, arch in rows:
    rec.with_context(lang=None).write({'name': name, 'arch_db': arch})
View.clear_caches()

readback_fail = 0
for token, rec, name, arch in rows:
    fresh = View.browse(rec.id)
    if (fresh.name or '') != name or (fresh.arch_db or '') != arch:
        lines.append('READ-BACK FAIL token=%s id=%s' % (token, rec.id))
        readback_fail = readback_fail + 1

if readback_fail:
    raise UserError((NL.join(lines) + NL + 'READ-BACK FAILED; transaction rolled back.')[:90000])

Param.set_param(S01_MARKER, '0')
Param.set_param(S02_MARKER, '0')
Param.set_param(RESTORE_MARKER, '1')

lines.append('')
lines.append('S99 COMPLETE: exact pre-S01/S02 commercial and VAT QWeb bytes restored; read-back PASS.')
text = NL.join(lines)[:90000]
Param.set_param(OUTPUT_KEY, text)
out = Param.search([('key', '=', OUTPUT_KEY)], limit=1)
action = {
    'type': 'ir.actions.act_window',
    'name': 'S99 BARANI Source / Payment Method restore result',
    'res_model': 'ir.config_parameter',
    'view_mode': 'form',
    'res_id': out.id,
    'target': 'current',
}
