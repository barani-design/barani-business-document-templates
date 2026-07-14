# ============================================================================
# ACTION NAME : P02 OPEN — BARANI Preview 2026+ verification invoices READ-ONLY
# MODEL       : Journal Entry (account.move)
# ACTION TO DO: Execute Python Code
# PURPOSE     : Open the exact RI/DPI/Credit Note records used to verify the
#               existing Accounting "Preview" button after a routing fix.
# SAFETY      : READ-ONLY:YES. Returns a filtered list action only.
# ============================================================================

MOVE_NAMES = ['2026232', '2026198', '2026200']

Move = env['account.move'].sudo().with_context(active_test=False)
found = Move.search([('name', 'in', MOVE_NAMES)], order='name desc')
found_names = []
for rec in found:
    found_names.append(rec.name or '/')
missing = []
for wanted in MOVE_NAMES:
    if wanted not in found_names:
        missing.append(wanted)

if not found:
    raise UserError('No requested preview verification invoices were found: %s' % ', '.join(MOVE_NAMES))

message = 'Opened %s verification records: %s' % (len(found), ', '.join(found_names))
if missing:
    message = message + '. Missing: ' + ', '.join(missing)

# Display notification first, then open the list using a chained client action
# is not portable in all Odoo 16 builds. The list title therefore carries the
# result summary.
action = {
    'type': 'ir.actions.act_window',
    'name': 'BARANI Preview 2026+ verification — ' + message,
    'res_model': 'account.move',
    'view_mode': 'tree,form',
    'views': [(False, 'tree'), (False, 'form')],
    'domain': [('id', 'in', found.ids)],
    'context': {
        'create': False,
        'delete': False,
    },
    'target': 'current',
}
