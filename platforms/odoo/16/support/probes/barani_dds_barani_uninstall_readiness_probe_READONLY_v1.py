# ============================================================================
# ACTION NAME : READ-ONLY: BARANI dds_barani uninstall-readiness probe v1
# MODEL       : Module (ir.module.module) is convenient; selected records ignored.
# ACTION TO DO: Execute Python Code
# CREATE AT   : Settings -> Technical -> Actions -> Server Actions -> New
# RUN BY      : Save, then run directly from the Server Action form.
# VISIBILITY  : Usually run from Settings -> Technical -> Actions -> Server Actions.
#               Do NOT bind this diagnostic into customer-facing menus.
# PAGINATION  : PAGE/PAGE_SIZE control the UserError output. If MORE REMAINS is
#               YES, set PAGE = 2, 3, ... and rerun until MORE REMAINS is NO.
# PURPOSE     : Read-only uninstall-readiness map for module dds_barani:
#                 - module state and installed reverse dependencies;
#                 - XML artifacts owned by dds_barani;
#                 - dds_barani-owned fields and stored-value usage counts;
#                 - views/reports/server actions/menu/actions owned or referencing it;
#                 - live BARANI report families checked for dds_barani/brn_ references.
# READ-ONLY   : search/read only. No create/write/unlink/set_param/commit/SQL.
# SAFE_EVAL   : no import/def/lambda/comprehension/with/getattr/hasattr/setattr/
#               eval/exec/open/dir/isinstance/try-except in executable body.
# ============================================================================

PAGE = 1
PAGE_SIZE = 30000
MODULE = 'dds_barani'

if PAGE < 1:
    raise UserError('PAGE must be >= 1')
if PAGE_SIZE < 1000:
    raise UserError('PAGE_SIZE must be >= 1000')

Module = env['ir.module.module'].sudo()
Dep = env['ir.module.module.dependency'].sudo()
IMD = env['ir.model.data'].sudo()
IMF = env['ir.model.fields'].sudo()
View = env['ir.ui.view'].sudo()
Report = env['ir.actions.report'].sudo()
ServerAction = env['ir.actions.server'].sudo()
Menu = env['ir.ui.menu'].sudo()
WindowAction = env['ir.actions.act_window'].sudo()
Param = env['ir.config_parameter'].sudo()

lines = []
lines.append('BARANI dds_barani UNINSTALL-READINESS PROBE v1 READ-ONLY')
lines.append('READ-ONLY:YES - metadata/business reads only; no create/write/unlink/set_param/commit/SQL.')
lines.append('MODULE=%s PAGE=%s PAGE_SIZE=%s' % (MODULE, PAGE, PAGE_SIZE))
lines.append('')

# A. Module state and reverse dependencies.
lines.append('=' * 60)
lines.append('A. MODULE STATE + INSTALLED REVERSE DEPENDENCIES')
lines.append('=' * 60)
mod = Module.search([('name', '=', MODULE)], limit=1)
if mod:
    lines.append('module id=%s name=%s state=%s shortdesc=%r' % (mod.id, mod.name, mod.state, mod.shortdesc or ''))
else:
    lines.append('module %s not found in ir.module.module' % MODULE)

deps = Dep.search([('name', '=', MODULE)], order='module_id')
installed_dep_count = 0
lines.append('reverse dependency rows where dependency.name = %s: %s' % (MODULE, len(deps)))
for d in deps:
    m = d.module_id
    line = '  module_id=%s module=%s state=%s shortdesc=%r' % (m.id, m.name or '', m.state or '', m.shortdesc or '')
    if m.state == 'installed':
        installed_dep_count = installed_dep_count + 1
        line = line + '  <-- INSTALLED DEPENDENT'
    lines.append(line)
if installed_dep_count:
    lines.append('BLOCKER/REVIEW: installed modules depend on %s. Do not uninstall until dependency/cascade impact is understood.' % MODULE)
else:
    lines.append('PASS: no installed reverse dependency row found for %s.' % MODULE)
lines.append('')

# B. Owned XML artifacts.
lines.append('=' * 60)
lines.append('B. XML ARTIFACTS OWNED BY dds_barani')
lines.append('=' * 60)
owned = IMD.search([('module', '=', MODULE)], order='model, name')
lines.append('owned ir.model.data rows: %s' % len(owned))
counts = {}
models_order = []
for x in owned:
    if x.model not in counts:
        counts[x.model] = 0
        models_order.append(x.model)
    counts[x.model] = counts[x.model] + 1
for mname in models_order:
    lines.append('  %s: %s' % (mname, counts[mname]))
lines.append('')
lines.append('owned artifact detail:')
for x in owned:
    lines.append('  %s.%s model=%s res_id=%s complete_name=%s' % (x.module, x.name, x.model, x.res_id, x.complete_name or ''))
lines.append('')

# C. Fields owned by dds_barani and usage counts.
lines.append('=' * 60)
lines.append('C. FIELDS OWNED BY dds_barani + STORED USAGE COUNTS')
lines.append('=' * 60)
field_count = 0
stored_with_usage = 0
for x in owned:
    if x.model == 'ir.model.fields':
        f = IMF.browse(x.res_id)
        if f and f.exists():
            field_count = field_count + 1
            fmodel = f.model or ''
            fname = f.name or ''
            ttype = f.ttype or ''
            store = False
            if 'store' in IMF._fields:
                store = bool(f.store)
            usage = 'not counted'
            if store and fmodel and fname:
                Target = env[fmodel].sudo()
                if fname in Target._fields:
                    usage_n = Target.search_count([(fname, '!=', False)])
                    usage = '%s records with non-empty value' % usage_n
                    if usage_n:
                        stored_with_usage = stored_with_usage + 1
            lines.append('  %s.%s type=%s store=%s field_id=%s -> %s' % (fmodel, fname, ttype, store, f.id, usage))
if not field_count:
    lines.append('  no ir.model.fields rows owned by %s' % MODULE)
if stored_with_usage:
    lines.append('REVIEW: at least %s stored dds_barani field(s) have values. Export before uninstall if historical reference may matter.' % stored_with_usage)
else:
    lines.append('PASS/INFO: no stored dds_barani-owned field with non-empty values was counted, or no owned fields found.')
lines.append('')

# D. Views owned by dds_barani.
lines.append('=' * 60)
lines.append('D. VIEWS OWNED BY dds_barani')
lines.append('=' * 60)
view_count = 0
for x in owned:
    if x.model == 'ir.ui.view':
        v = View.browse(x.res_id)
        if v and v.exists():
            view_count = view_count + 1
            inh = 'EMPTY/STANDALONE'
            if v.inherit_id:
                inh = '%s[%s]' % (v.inherit_id.id, v.inherit_id.key or '')
            arch = v.arch_db or ''
            low = arch.lower()
            flags = []
            if 'sale.report_saleorder_document' in low:
                flags.append('SALE_REPORT_PATCH')
            if 'purchase.report' in low:
                flags.append('PURCHASE_REPORT_PATCH')
            if 'stock.report' in low or 'report_picking' in low:
                flags.append('STOCK/PICKING_PATCH')
            if 'barcode' in low or 'qr' in low:
                flags.append('BARCODE/QR_TERM')
            if 'button' in low:
                flags.append('BUTTON_TERM')
            lines.append('  view id=%s key=%s name=%r type=%s mode=%s active=%s inherit_id=%s flags=%s arch_len=%s' % (
                v.id, v.key or '', v.name or '', v.type or '', v.mode or '', v.active, inh, ','.join(flags) or '-', len(arch)))
            if flags:
                pos = -1
                token = ''
                for tok in ['barcode', 'qr', 'button', 'sale.report_saleorder_document', 'picking', 'stock']:
                    if pos == -1:
                        pos = low.find(tok)
                        token = tok
                if pos != -1:
                    s = pos - 180
                    if s < 0:
                        s = 0
                    e = pos + 360
                    lines.append('    snippet[%s]: %s' % (token, arch[s:e].replace('\n', ' ')))
if not view_count:
    lines.append('  no ir.ui.view rows owned by %s' % MODULE)
lines.append('')

# E. Owned report/server/window/menu artifacts.
lines.append('=' * 60)
lines.append('E. OWNED ACTIONS / MENUS / REPORTS')
lines.append('=' * 60)
for x in owned:
    if x.model == 'ir.actions.report':
        r = Report.browse(x.res_id)
        if r and r.exists():
            lines.append('  report id=%s name=%r model=%s report_name=%s binding_model=%s' % (r.id, r.name or '', r.model or '', r.report_name or '', r.binding_model_id.model or ''))
    if x.model == 'ir.actions.server':
        a = ServerAction.browse(x.res_id)
        if a and a.exists():
            lines.append('  server_action id=%s name=%r model=%s state=%s' % (a.id, a.name or '', a.model_id.model or '', a.state or ''))
    if x.model == 'ir.actions.act_window':
        a2 = WindowAction.browse(x.res_id)
        if a2 and a2.exists():
            lines.append('  window_action id=%s name=%r res_model=%s' % (a2.id, a2.name or '', a2.res_model or ''))
    if x.model == 'ir.ui.menu':
        mn = Menu.browse(x.res_id)
        if mn and mn.exists():
            lines.append('  menu id=%s name=%r parent=%r action=%r' % (mn.id, mn.name or '', mn.parent_id.name or '', mn.action or ''))
lines.append('')

# F. Cross-reference scans.
lines.append('=' * 60)
lines.append('F. REFERENCES TO dds_barani / brn_ / report patches OUTSIDE MODULE OWNER')
lines.append('=' * 60)
scan_terms = ['dds_barani', 'brn_', 'Update Delivered Quantity', 'Lot/Serial', 'Services Only', 'Source Document']
for term in scan_terms:
    lines.append('TERM %r' % term)
    qviews = View.search([('arch_db', 'ilike', term)], order='id', limit=25)
    lines.append('  QWeb/views containing term: %s (showing max 25)' % len(qviews))
    for v in qviews:
        owner = 'unknown'
        xd = IMD.search([('model', '=', 'ir.ui.view'), ('res_id', '=', v.id)], limit=1)
        if xd:
            owner = xd.module
        lines.append('    view id=%s key=%s owner=%s active=%s inherit_id=%s name=%r' % (v.id, v.key or '', owner, v.active, v.inherit_id.id or '', v.name or ''))
    sacts = ServerAction.search(['|', ('name', 'ilike', term), ('code', 'ilike', term)], order='id', limit=20)
    lines.append('  server actions containing term: %s (showing max 20)' % len(sacts))
    for a in sacts:
        lines.append('    server_action id=%s name=%r model=%s state=%s' % (a.id, a.name or '', a.model_id.model or '', a.state or ''))
lines.append('')

# G. BARANI-owned reports checked for references.
lines.append('=' * 60)
lines.append('G. BARANI REPORT FAMILIES - REFERENCE CHECK')
lines.append('=' * 60)
barani_keys = [
    'barani_vat.report_invoice_document_vat',
    'barani_vat.external_layout_standard_titled',
    'barani_commercial.report_saleorder_document',
    'barani_commercial.external_layout_standard_titled',
    'barani_commercial.report_saleorder',
    'barani_commercial.report_saleorder_proforma',
]
for key in barani_keys:
    v = View.search([('key', '=', key)], limit=1)
    if not v:
        lines.append('  key=%s -> MISSING' % key)
    else:
        arch = v.arch_db or ''
        low = arch.lower()
        bad = []
        if MODULE in low:
            bad.append(MODULE)
        if 'brn_' in low:
            bad.append('brn_')
        if 'advanced invoice:' in low:
            bad.append('Advanced Invoice:')
        if 'sale.report_saleorder_document' in low:
            bad.append('stock sale body')
        if 'web.external_layout' in low:
            bad.append('web.external_layout')
        lines.append('  key=%s id=%s inherit_id=%s len=%s flags=%s' % (key, v.id, v.inherit_id.id or 'EMPTY', len(arch), ','.join(bad) or 'OK'))
lines.append('')

# H. Suggested gate.
lines.append('=' * 60)
lines.append('H. INTERPRETATION GATE')
lines.append('=' * 60)
lines.append('GREEN only if:')
lines.append('  1) A shows no installed reverse dependency on dds_barani;')
lines.append('  2) C stored dds_barani field values have been exported or accepted as disposable;')
lines.append('  3) D/F show no must-keep UI/report feature still used by the business;')
lines.append('  4) G shows BARANI VAT and BARANI commercial report families do not reference dds_barani/brn_;')
lines.append('  5) full database backup exists, and uninstall is tested first on staging or a restored copy.')
lines.append('')
lines.append('This probe does not uninstall anything. It only prepares the go/no-go evidence.')

full = '\n'.join(lines)
start = (PAGE - 1) * PAGE_SIZE
end = PAGE * PAGE_SIZE
chunk = full[start:end]
more = 'NO'
if end < len(full):
    more = 'YES'
header = 'PAGE %s | chars %s-%s of %s | MORE REMAINS: %s\n' % (PAGE, start, end, len(full), more)
footer = '\n--- END PAGE %s | MORE REMAINS: %s ---' % (PAGE, more)
if more == 'YES':
    footer = footer + '\nSet PAGE=%s and rerun to continue.' % (PAGE + 1)
raise UserError(header + chunk + footer)
