# ============================================================================
# ACTION NAME : READ-ONLY: BARANI new-DB Option-B down-payment accounting readiness probe v2
# MODEL       : Module (ir.module.module) or any model; selected records ignored.
# ACTION TO DO: Execute Python Code
# PURPOSE     : Read-only readiness check for the non-template configuration needed
#               by BARANI VAT-inclusive down-payment invoices and final RI deduction:
#                 - modules/fields/company/bank
#                 - account 324000 and down-payment product/category/account/taxes
#                 - sale taxes, price-included advance-tax candidates
#                 - fiscal positions and mappings for Domestic / OSS / Intra-EU / Non-EU
#                 - POHODA module presence and export-risk reminders
# READ-ONLY   : search/read only. No create/write/unlink/set_param/commit/SQL.
# SAFE_EVAL   : no import/def/lambda/comprehension/with/getattr/hasattr/setattr/
#               eval/exec/open/dir/isinstance in executable code.
# ============================================================================

PAGE = 1
PAGE_SIZE = 32000

RECEIVING_IBAN_COMPACT = 'XX0000000000000000000000'
RECEIVING_BIC = 'YOURBICXXX'
ACCOUNT_324 = '324000'
TARGET_DOMESTIC_VAT = 23.0
TARGET_OSS_FI_VAT = 25.5

Company = env['res.company'].sudo()
Module = env['ir.module.module'].sudo()
Tax = env['account.tax'].sudo()
Account = env['account.account'].sudo()
ProductTemplate = env['product.template'].sudo()
FiscalPosition = env['account.fiscal.position'].sudo()
Fields = env['ir.model.fields'].sudo()

lines = []
lines.append('READ-ONLY: BARANI new-DB Option-B down-payment accounting readiness probe v2')
lines.append('Selected records ignored. No writes. PAGE=%s PAGE_SIZE=%s' % (PAGE, PAGE_SIZE))
lines.append('Target principle: customer-paid advances are gross; Odoo should split gross into base + VAT using fiscal-position-specific tax treatment.')
lines.append('')

company = env.company.sudo()
lines.append('1) COMPANY / MODULES / REPORT FIELD PREREQUISITES')
lines.append('  company=%s id=%s currency=%s VAT=%s registry=%s fiscal_country=%s' % (company.name, company.id, company.currency_id.name if company.currency_id else '', company.vat or '', company.company_registry or '', company.account_fiscal_country_id.name if company.account_fiscal_country_id else ''))
if 'tax_calculation_rounding_method' in company._fields:
    lines.append('  tax_calculation_rounding_method=%s' % company.tax_calculation_rounding_method)
for modname in ['sale', 'account', 'account_intrastat', 'l10n_sk', 'account_qr_code_sepa', 'dds_export_pohoda']:
    mods = Module.search([('name', '=', modname)], limit=1)
    if mods:
        lines.append('  module %-28s state=%s' % (modname, mods.state))
    else:
        lines.append('  module %-28s NOT FOUND' % modname)
for fname in ['invoice_incoterm_id', 'reversed_entry_id', 'intrastat_transport_mode_id']:
    fld = Fields.search([('model', '=', 'account.move'), ('name', '=', fname)], limit=1)
    lines.append('  account.move.%-32s %s' % (fname, 'FOUND' if fld else 'MISSING'))
lines.append('')

lines.append('2) COMPANY RECEIVING BANK')
match_count = 0
for b in company.partner_id.bank_ids:
    bic = ''
    if b.bank_id:
        bic = (b.bank_id.bic or '').replace(' ', '')
    acc = (b.acc_number or '').replace(' ', '')
    is_match = acc == RECEIVING_IBAN_COMPACT and bic == RECEIVING_BIC
    if is_match:
        match_count = match_count + 1
    addr = ''
    if b.bank_id:
        if b.bank_id.street:
            addr = b.bank_id.street
        if b.bank_id.zip or b.bank_id.city:
            if addr:
                addr = addr + ', '
            if b.bank_id.zip:
                addr = addr + b.bank_id.zip
            if b.bank_id.zip and b.bank_id.city:
                addr = addr + ' '
            if b.bank_id.city:
                addr = addr + b.bank_id.city
        if b.bank_id.country:
            if addr:
                addr = addr + ', '
            addr = addr + b.bank_id.country.name
    lines.append('  bank id=%s acc=%s bic=%s name=%s addr=%s MATCH=%s' % (b.id, b.acc_number or '', bic, b.bank_id.name if b.bank_id else '', addr, 'YES' if is_match else 'no'))
lines.append('  matching BARANI receiving bank count=%s' % match_count)
if match_count != 1:
    lines.append('  WARNING: report installers expect exactly one confirmed company receiving bank for the BARANI company.')
lines.append('')

lines.append('3) ACCOUNT 324000 AND DOWN-PAYMENT PRODUCT')
accs = Account.search([('code', '=', ACCOUNT_324)], limit=10)
if accs:
    for a in accs:
        lines.append('  account id=%s code=%s name=%s deprecated=%s type=%s' % (a.id, a.code, a.name, a.deprecated, a.account_type))
else:
    lines.append('  ERROR: account 324000 not found.')

pts = ProductTemplate.search(['|', '|', ('name', 'ilike', 'Down Payment'), ('name', 'ilike', 'Deposit'), ('categ_id.complete_name', 'ilike', 'Received Down Payments')], limit=30)
if not pts:
    lines.append('  Down Payment/Deposit product template not found yet. This can be normal before the first Odoo down-payment invoice; configure it when created.')
for pt in pts:
    income = ''
    if 'property_account_income_id' in pt._fields and pt.property_account_income_id:
        income = pt.property_account_income_id.code + ' ' + pt.property_account_income_id.name
    categ_income = ''
    if pt.categ_id and 'property_account_income_categ_id' in pt.categ_id._fields and pt.categ_id.property_account_income_categ_id:
        categ_income = pt.categ_id.property_account_income_categ_id.code + ' ' + pt.categ_id.property_account_income_categ_id.name
    tax_names = ''
    for t in pt.taxes_id:
        if tax_names:
            tax_names = tax_names + ' | '
        tax_names = tax_names + ('id=%s %s amount=%s desc=%s included=%s active=%s' % (t.id, t.name, t.amount, t.description or '', t.price_include, t.active))
    lines.append('  template id=%s name=%r categ=%r income=%r categ_income=%r taxes=[%s]' % (pt.id, pt.name, pt.categ_id.complete_name, income, categ_income, tax_names))
    if ACCOUNT_324 in income or ACCOUNT_324 in categ_income:
        lines.append('    PASS: product/category income path appears to resolve to 324000.')
    else:
        lines.append('    WARNING: product/category income path does not visibly resolve to 324000.')
lines.append('')

lines.append('4) SALE TAXES — LABELS, PRICE-INCLUDED ADVANCE CANDIDATES')
empty_tax = 0
advance_source_candidates = 0
vat23_included = 0
vat23_excluded = 0
fi255_included = 0
zero_sales = 0
for t in Tax.with_context(active_test=False).search([('type_tax_use', '=', 'sale')], order='amount,name'):
    if not t.description:
        empty_tax = empty_tax + 1
    if abs((t.amount or 0.0) - TARGET_DOMESTIC_VAT) < 0.0001 and t.price_include:
        vat23_included = vat23_included + 1
    if abs((t.amount or 0.0) - TARGET_DOMESTIC_VAT) < 0.0001 and not t.price_include:
        vat23_excluded = vat23_excluded + 1
    if abs((t.amount or 0.0) - TARGET_OSS_FI_VAT) < 0.0001 and t.price_include:
        fi255_included = fi255_included + 1
    if abs((t.amount or 0.0)) < 0.0001:
        zero_sales = zero_sales + 1
    tname_low = (t.name or '').lower()
    if t.price_include and (('advance' in tname_low) or ('down' in tname_low) or ('deposit' in tname_low) or ('preddav' in tname_low) or ('zalo' in tname_low) or ('zálo' in tname_low)):
        advance_source_candidates = advance_source_candidates + 1
        lines.append('  ADVANCE INCLUDED CANDIDATE tax id=%s active=%s name=%s amount=%s desc=%s included=%s' % (t.id, t.active, t.name, t.amount, t.description or '', t.price_include))
lines.append('  empty sale tax descriptions=%s' % empty_tax)
lines.append('  23%% sale tax price-included candidates=%s; price-excluded candidates=%s' % (vat23_included, vat23_excluded))
lines.append('  25.5%% FI/OSS price-included candidates=%s' % fi255_included)
lines.append('  zero sale taxes=%s' % zero_sales)
lines.append('  named price-included advance/deposit tax candidates=%s' % advance_source_candidates)
if vat23_included == 0:
    lines.append('  WARNING: no 23%% price-included sale tax found. Gross-paid domestic advances require either included tax or manual net entry.')
lines.append('')

lines.append('5) FISCAL POSITION MAPPING MATRIX')
lines.append('  Desired target for gross advances:')
lines.append('    Domestic Slovakia -> SK 23%% price-included advance tax OR no mapping if product default is already SK 23%% included.')
lines.append('    OSS B2C Finland -> FI OSS 25.5%% price-included advance tax.')
lines.append('    Intra-EU reverse charge -> 0%% reverse-charge advance tax.')
lines.append('    Non-EU export -> 0%% export advance tax.')
lines.append('')
for fp in FiscalPosition.with_context(active_test=False).search([], order='sequence,name'):
    low = (fp.name or '').lower()
    interesting = False
    if 'domestic' in low or 'slovak' in low or 'slovakia' in low:
        interesting = True
    if 'oss' in low or 'finland' in low or 'fíns' in low or 'finn' in low:
        interesting = True
    if 'intra' in low or 'reverse' in low or 'eu' in low:
        interesting = True
    if 'non-eu' in low or 'export' in low or 'mimo' in low:
        interesting = True
    if interesting:
        note = ''
        if 'note' in fp._fields:
            note = fp.note or ''
        if len(note) > 150:
            note = note[:150] + '...'
        lines.append('  FP id=%s active=%s seq=%s name=%r auto=%s vat_required=%s country=%s group=%s note=%r' % (fp.id, fp.active, fp.sequence, fp.name, fp.auto_apply, fp.vat_required, fp.country_id.name if fp.country_id else '', fp.country_group_id.name if fp.country_group_id else '', note))
        has_included_src = False
        has_23_dst = False
        has_fi_dst = False
        has_zero_dst = False
        for tm in fp.tax_ids:
            src = tm.tax_src_id
            dst = tm.tax_dest_id
            if src and src.price_include:
                has_included_src = True
            if dst and abs((dst.amount or 0.0) - TARGET_DOMESTIC_VAT) < 0.0001:
                has_23_dst = True
            if dst and abs((dst.amount or 0.0) - TARGET_OSS_FI_VAT) < 0.0001:
                has_fi_dst = True
            if dst and abs((dst.amount or 0.0)) < 0.0001:
                has_zero_dst = True
            lines.append('      map tax %s[%s incl=%s] -> %s[%s incl=%s]' % (src.name if src else '', src.amount if src else '', src.price_include if src else '', dst.name if dst else '', dst.amount if dst else '', dst.price_include if dst else ''))
        if 'oss' in low and 'finland' in low:
            if has_fi_dst:
                lines.append('      PASS/LIKELY: OSS Finland maps at least one source tax to 25.5%%.')
            else:
                lines.append('      WARNING: OSS Finland does not visibly map an advance/source tax to 25.5%%.')
        if 'intra' in low or 'reverse' in low:
            if has_zero_dst:
                lines.append('      PASS/LIKELY: Intra-EU/reverse maps at least one source tax to 0%%.')
            else:
                lines.append('      WARNING: Intra-EU/reverse does not visibly map source tax to 0%%.')
        if 'non-eu' in low or 'export' in low or 'mimo' in low:
            if has_zero_dst:
                lines.append('      PASS/LIKELY: Non-EU/export maps at least one source tax to 0%%.')
            else:
                lines.append('      WARNING: Non-EU/export does not visibly map source tax to 0%%.')
        if 'domestic' in low or 'slovak' in low or 'slovakia' in low:
            if has_23_dst or vat23_included:
                lines.append('      PASS/LIKELY: Domestic can use 23%% treatment; confirm down-payment product uses included tax if gross-paid advances are required.')
            else:
                lines.append('      WARNING: Domestic FP/product path does not show a 23%% candidate for gross-paid advances.')
lines.append('')

lines.append('6) POHODA / EXPORT REMINDER')
pohoda_mods = Module.search(['|', ('name', 'ilike', 'pohoda'), ('summary', 'ilike', 'Pohoda')], limit=20)
if pohoda_mods:
    for m in pohoda_mods:
        lines.append('  module %s state=%s summary=%s' % (m.name, m.state, m.summary or ''))
else:
    lines.append('  no Pohoda-named modules found by name/summary search')
lines.append('  Reminder: valid VAT-bearing domestic/OSS DPIs and matching VAT-bearing RI deductions must be allowed; fiscal-position/tax mismatches should still be blocked.')
lines.append('')

lines.append('7) RECOMMENDED NEXT ACTION')
lines.append('  Do NOT create/modify fiscal positions automatically from this probe output. Use it to identify missing taxes/mappings, then apply changes manually or with a separate, accountant-approved dry-run migration.')
lines.append('  If gross customer-paid advances are required, prefer a dedicated price-included advance tax path mapped by fiscal positions. Keep account/category 324000 unchanged.')

text = '\n'.join(lines)
start = (PAGE - 1) * PAGE_SIZE
end = start + PAGE_SIZE
chunk = text[start:end]
more = 'YES' if end < len(text) else 'NO'
raise UserError('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s\n%s' % (PAGE, start, min(end, len(text)), len(text), more, chunk))
