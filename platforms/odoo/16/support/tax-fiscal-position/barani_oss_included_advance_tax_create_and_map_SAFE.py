# ============================================================================
# ACTION NAME : BARANI OSS included down-payment tax create/map SAFE
# MODEL       : Module (ir.module.module) or any model; selected records ignored.
# ACTION TO DO: Execute Python Code
# RUN BY      : Run APPLY=False first; then APPLY=True + CONFIRM='CREATE_MAP_OSS_INCLUDED_ADVANCE_TAXES'.
# PURPOSE     : For each OSS B2C fiscal position, ensure gross-paid down-payment
#               advances use price-included destination-country VAT taxes.
#
#               It reads the current OSS mapping, duplicates the current OSS
#               destination VAT tax when necessary, renames the duplicate by
#               appending ' Included — Down Payments', sets Included in Price,
#               and maps ONLY the source tax
#                 'SK 23% VAT Included — Down Payments'
#               to that included destination tax.
#
#               Existing normal product mappings are not changed. Intra-EU and
#               Non-EU mappings are not changed. The Down payment product/account
#               and account 324000 are not changed.
#
# DEFAULT     : APPLY=False. Dry-run performs no writes.
# WRITES      : account.tax create/copy; account.fiscal.position.tax create/write
#               only when APPLY=True + CONFIRM matches.
# SAFE_EVAL   : no import/def/lambda/comprehension/with/getattr/hasattr/setattr/
#               eval/exec/open/dir/isinstance in executable code.
# ============================================================================

APPLY = False
CONFIRM = ''

ACTION_NAME = 'BARANI OSS included down-payment tax create/map SAFE'
SOURCE_ADVANCE_TAX_NAME = 'SK 23% VAT Included — Down Payments'
BASE_DOMESTIC_TAX_NAME = '23 % SK VAT'
INCLUDED_SUFFIX = ' Included — Down Payments'
CONFIRM_TOKEN = 'CREATE_MAP_OSS_INCLUDED_ADVANCE_TAXES'
OUTPUT_PARAMETER_KEY = 'barani.oss_included_advance_tax.last_run'

Tax = env['account.tax'].sudo()
FP = env['account.fiscal.position'].sudo()
FPTax = env['account.fiscal.position.tax'].sudo()
Product = env['product.template'].sudo()
Param = env['ir.config_parameter'].sudo()

lines = []
lines.append(ACTION_NAME)
lines.append('APPLY=%s CONFIRM=%s' % (APPLY, CONFIRM))
lines.append('Scope: OSS B2C fiscal-position tax mappings for gross-paid down payments only.')
lines.append('')

# Savepoint/cache probe.
manual_sp_ok = False
cache_inv_method = ''
lines.append('TEST 0 - manual SQL savepoint recovery + ORM cache invalidation')
try:
    env.cr.execute('SAVEPOINT t0_ok')
    env.cr.execute('SELECT 1')
    env.cr.execute('RELEASE SAVEPOINT t0_ok')
    env.cr.execute('SAVEPOINT t0_fail')
    try:
        env.cr.execute('SELECT * FROM __barani_missing_table_for_rollback_probe__')
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
    lines.append('STOP: savepoint/cache mechanism unusable.')
    raise UserError('\n'.join(lines)[:90000])
lines.append('')

# Resolve source taxes.
source_taxes = Tax.search([('name', '=', SOURCE_ADVANCE_TAX_NAME), ('type_tax_use', '=', 'sale')])
base_taxes = Tax.search([('name', '=', BASE_DOMESTIC_TAX_NAME), ('type_tax_use', '=', 'sale')])
lines.append('SOURCE TAX RESOLUTION')
lines.append('  %r found=%s' % (SOURCE_ADVANCE_TAX_NAME, len(source_taxes)))
if len(source_taxes) != 1:
    lines.append('ERROR: expected exactly one source advance tax. Refusing.')
    raise UserError('\n'.join(lines)[:90000])
source_tax = source_taxes[0]
lines.append('  source id=%s amount=%s included=%s active=%s description=%r' % (source_tax.id, source_tax.amount, source_tax.price_include, source_tax.active, source_tax.description))
if not source_tax.active or not source_tax.price_include or source_tax.amount < 22.99 or source_tax.amount > 23.01:
    lines.append('ERROR: source advance tax must be active, 23%%, and Included in Price=True. Refusing.')
    raise UserError('\n'.join(lines)[:90000])
lines.append('  %r found=%s' % (BASE_DOMESTIC_TAX_NAME, len(base_taxes)))
if len(base_taxes) != 1:
    lines.append('ERROR: expected exactly one normal 23%% SK VAT source tax for regular OSS mapping discovery. Refusing.')
    raise UserError('\n'.join(lines)[:90000])
base_tax = base_taxes[0]
lines.append('  base id=%s amount=%s included=%s active=%s' % (base_tax.id, base_tax.amount, base_tax.price_include, base_tax.active))
lines.append('')

# Down-payment product sanity: product should use source tax and remain 324-category/account path.
lines.append('DOWN PAYMENT PRODUCT SANITY')
dp_templates = Product.search([('name', '=', 'Down payment')])
found_dp_source_tax = False
found_dp_324 = False
for pt in dp_templates:
    tax_names = ''
    has_source = False
    for tx in pt.taxes_id:
        if tax_names:
            tax_names = tax_names + ', '
        tax_names = tax_names + tx.name
        if tx.id == source_tax.id:
            has_source = True
            found_dp_source_tax = True
    income = pt.property_account_income_id
    categ_income = pt.categ_id.property_account_income_categ_id if pt.categ_id else False
    code = ''
    if income:
        code = income.code or ''
    elif categ_income:
        code = categ_income.code or ''
    if code == '324000':
        found_dp_324 = True
    lines.append('  template id=%s name=%r categ=%r income_path=%r taxes=[%s]' % (pt.id, pt.name, pt.categ_id.complete_name if pt.categ_id else '', code, tax_names))
if not found_dp_source_tax:
    lines.append('ERROR: no Down payment template uses the source included advance tax. Refusing; set product customer tax first.')
    raise UserError('\n'.join(lines)[:90000])
if not found_dp_324:
    lines.append('ERROR: no Down payment template resolves to account 324000. Refusing; do not proceed until accounting path is fixed.')
    raise UserError('\n'.join(lines)[:90000])
lines.append('PASS: Down payment product uses included source tax and still resolves to 324000.')
lines.append('')

fps = FP.search([('name', 'ilike', 'OSS B2C')], order='name')
if not fps:
    lines.append('ERROR: no OSS B2C fiscal positions found. Refusing.')
    raise UserError('\n'.join(lines)[:90000])

lines.append('PLAN BY OSS FISCAL POSITION')
create_count = 0
reuse_count = 0
update_count = 0
create_map_count = 0
already_ok_count = 0
skip_count = 0
fatal = False

# Store plan lines as text only; the actual work recomputes under savepoint.
for fp in fps:
    regular_map = False
    advance_map = False
    for mp in fp.tax_ids:
        if mp.tax_src_id and mp.tax_src_id.id == base_tax.id:
            regular_map = mp
        if mp.tax_src_id and mp.tax_src_id.id == source_tax.id:
            advance_map = mp

    lines.append('')
    lines.append('FP id=%s name=%r' % (fp.id, fp.name))
    base_dest = False
    if advance_map and advance_map.tax_dest_id:
        base_dest = advance_map.tax_dest_id
        lines.append('  current advance dest: id=%s name=%r amount=%s included=%s' % (base_dest.id, base_dest.name, base_dest.amount, base_dest.price_include))
    elif regular_map and regular_map.tax_dest_id:
        base_dest = regular_map.tax_dest_id
        lines.append('  no advance mapping yet; using regular 23%% mapping dest as base: id=%s name=%r amount=%s included=%s' % (base_dest.id, base_dest.name, base_dest.amount, base_dest.price_include))
    else:
        lines.append('  ERROR: no usable 23%% regular mapping or current advance mapping found.')
        fatal = True

    if base_dest:
        if base_dest.amount <= 0.0001:
            lines.append('  SKIP: target is 0%%. OSS B2C should normally be VAT-bearing; review manually.')
            skip_count = skip_count + 1
        elif base_dest.price_include:
            lines.append('  OK: destination tax is already price-included; map/reuse it.')
            if advance_map and advance_map.tax_dest_id and advance_map.tax_dest_id.id == base_dest.id:
                already_ok_count = already_ok_count + 1
            else:
                update_count = update_count + 1
        else:
            new_name = base_dest.name + INCLUDED_SUFFIX
            existing = Tax.search([('name', '=', new_name), ('type_tax_use', '=', 'sale'), ('company_id', '=', base_dest.company_id.id)])
            if len(existing) > 1:
                lines.append('  ERROR: multiple existing included candidate taxes named %r. Refusing.' % new_name)
                fatal = True
            elif len(existing) == 1:
                cand = existing[0]
                if not cand.price_include:
                    lines.append('  ERROR: existing candidate %r is not price-included. Refusing.' % cand.name)
                    fatal = True
                elif cand.amount != base_dest.amount:
                    lines.append('  ERROR: existing candidate %r amount differs from source destination. Refusing.' % cand.name)
                    fatal = True
                else:
                    lines.append('  REUSE: existing included tax id=%s name=%r amount=%s' % (cand.id, cand.name, cand.amount))
                    reuse_count = reuse_count + 1
                    if advance_map and advance_map.tax_dest_id and advance_map.tax_dest_id.id == cand.id:
                        already_ok_count = already_ok_count + 1
                    else:
                        update_count = update_count + 1
            else:
                lines.append('  CREATE: copy tax id=%s %r -> new price-included tax %r' % (base_dest.id, base_dest.name, new_name))
                create_count = create_count + 1
                if advance_map:
                    update_count = update_count + 1
                else:
                    create_map_count = create_map_count + 1

if fatal:
    lines.append('')
    lines.append('ABORT: fatal planning errors. No writes will be performed.')
    raise UserError('\n'.join(lines)[:90000])

lines.append('')
lines.append('PLAN SUMMARY')
lines.append('  included taxes to create: %s' % create_count)
lines.append('  existing included taxes to reuse: %s' % reuse_count)
lines.append('  fiscal-position mapping updates: %s' % update_count)
lines.append('  fiscal-position mappings to create: %s' % create_map_count)
lines.append('  already OK mappings: %s' % already_ok_count)
lines.append('  skipped/review manually: %s' % skip_count)
lines.append('  unchanged: normal product mappings, Intra-EU/Non-EU mappings, down-payment account/category, invoices/accounting entries')
lines.append('')

if not APPLY:
    lines.append('DRY RUN COMPLETE: no writes performed.')
    lines.append('Set APPLY=True and CONFIRM=%r to apply.' % CONFIRM_TOKEN)
    raise UserError('\n'.join(lines)[:90000])
if CONFIRM != CONFIRM_TOKEN:
    lines.append('ERROR: APPLY=True but CONFIRM does not match %r. Refusing.' % CONFIRM_TOKEN)
    raise UserError('\n'.join(lines)[:90000])

lines.append('APPLY OSS INCLUDED ADVANCE TAXES / MAPPINGS')
try:
    env.cr.execute('SAVEPOINT sp_oss_included_advance_tax')
    create_done = 0
    reuse_done = 0
    map_write_done = 0
    map_create_done = 0

    for fp2 in fps:
        regular_map2 = False
        advance_map2 = False
        for mp2 in fp2.tax_ids:
            if mp2.tax_src_id and mp2.tax_src_id.id == base_tax.id:
                regular_map2 = mp2
            if mp2.tax_src_id and mp2.tax_src_id.id == source_tax.id:
                advance_map2 = mp2

        base_dest2 = False
        if advance_map2 and advance_map2.tax_dest_id:
            base_dest2 = advance_map2.tax_dest_id
        elif regular_map2 and regular_map2.tax_dest_id:
            base_dest2 = regular_map2.tax_dest_id

        if base_dest2 and base_dest2.amount > 0.0001:
            included_dest = False
            if base_dest2.price_include:
                included_dest = base_dest2
                reuse_done = reuse_done + 1
            else:
                new_name2 = base_dest2.name + INCLUDED_SUFFIX
                existing2 = Tax.search([('name', '=', new_name2), ('type_tax_use', '=', 'sale'), ('company_id', '=', base_dest2.company_id.id)])
                if len(existing2) == 1:
                    included_dest = existing2[0]
                    reuse_done = reuse_done + 1
                elif len(existing2) == 0:
                    included_dest = base_dest2.copy({
                        'name': new_name2,
                        'price_include': True,
                        'description': base_dest2.description or '',
                    })
                    create_done = create_done + 1
                    lines.append('  CREATED tax id=%s from base id=%s name=%r' % (included_dest.id, base_dest2.id, included_dest.name))
                else:
                    raise Exception('multiple included candidate taxes for ' + new_name2)

            if not included_dest or not included_dest.price_include:
                raise Exception('included destination tax resolution failed for FP ' + fp2.name)

            if advance_map2:
                if advance_map2.tax_dest_id.id != included_dest.id:
                    advance_map2.write({'tax_dest_id': included_dest.id})
                    map_write_done = map_write_done + 1
                    lines.append('  UPDATED FP %r mapping source=%r dest=%r' % (fp2.name, source_tax.name, included_dest.name))
            else:
                FPTax.create({'position_id': fp2.id, 'tax_src_id': source_tax.id, 'tax_dest_id': included_dest.id})
                map_create_done = map_create_done + 1
                lines.append('  CREATED FP %r mapping source=%r dest=%r' % (fp2.name, source_tax.name, included_dest.name))

    if cache_inv_method == 'env.invalidate_all':
        env.invalidate_all()
    else:
        env.cache.invalidate()
    lines.append('PASS: ORM cache invalidated via %s.' % cache_inv_method)

    # Read-back verification: every OSS B2C advance mapping destination must be price-included.
    bad_after = 0
    missing_after = 0
    for fp3 in fps:
        found = False
        for mp3 in fp3.tax_ids:
            if mp3.tax_src_id and mp3.tax_src_id.id == source_tax.id:
                found = True
                if not mp3.tax_dest_id or not mp3.tax_dest_id.price_include:
                    bad_after = bad_after + 1
                    lines.append('  BAD AFTER: FP %r dest=%r included=%s' % (fp3.name, mp3.tax_dest_id.name if mp3.tax_dest_id else '', mp3.tax_dest_id.price_include if mp3.tax_dest_id else ''))
        if not found:
            missing_after = missing_after + 1
            lines.append('  MISSING AFTER: FP %r has no advance mapping.' % fp3.name)
    if bad_after or missing_after:
        raise Exception('read-back verification failed: bad=%s missing=%s' % (bad_after, missing_after))

    env.cr.execute('RELEASE SAVEPOINT sp_oss_included_advance_tax')
    lines.append('PASS: apply complete. created_taxes=%s reused_taxes=%s mapping_updates=%s mapping_creates=%s' % (create_done, reuse_done, map_write_done, map_create_done))
    lines.append('NEXT TEST: create OSS B2C draft DPI for 100 EUR gross. Expected total stays 100 EUR and Odoo splits base/VAT by destination-country VAT rate.')
except Exception as e_apply:
    try:
        env.cr.execute('ROLLBACK TO SAVEPOINT sp_oss_included_advance_tax')
        env.cr.execute('RELEASE SAVEPOINT sp_oss_included_advance_tax')
        if cache_inv_method == 'env.invalidate_all':
            env.invalidate_all()
        else:
            env.cache.invalidate()
        lines.append('PASS: rolled back savepoint after failure.')
    except Exception as e_rb:
        lines.append('ROLLBACK PROBLEM: %s' % str(e_rb)[:500])
    lines.append('INSTALL FAILED: %s' % str(e_apply)[:1500])
    raise UserError('\n'.join(lines)[:90000])

text = '\n'.join(lines)
Param.set_param(OUTPUT_PARAMETER_KEY, text)
param = Param.search([('key', '=', OUTPUT_PARAMETER_KEY)], limit=1)
action = {'type': 'ir.actions.act_window', 'name': ACTION_NAME, 'res_model': 'ir.config_parameter', 'view_mode': 'form', 'res_id': param.id, 'target': 'current'}
