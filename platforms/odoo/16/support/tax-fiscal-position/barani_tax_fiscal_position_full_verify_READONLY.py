# ============================================================================
# ACTION NAME : READ-ONLY: BARANI tax + fiscal-position full verification dump
# MODEL       : Module (ir.module.module) or any model; selected records ignored.
# ACTION TO DO: Execute Python Code
# PURPOSE     : Print a complete, paged, read-only audit of taxes, down-payment
#               product/account 324000 setup, and every fiscal-position tax
#               mapping after the Option-B gross-paid down-payment configuration.
#
# READ-ONLY   : YES. Performs no create/write/unlink/set_param/commit/SQL.
#               Reads account.tax, account.fiscal.position, product templates,
#               company/bank/account metadata, then raises UserError as output.
#
# RUN         : Settings > Technical > Server Actions > Run.
#               Set PAGE=1, run; if footer says MORE REMAINS:YES, increment PAGE.
#
# EXPECTED OPTION-B PRINCIPLE
#   - Down-payment product keeps account 324000.
#   - Domestic gross-paid DPI uses "SK 23% VAT Included — Down Payments".
#   - Intra-EU maps that included advance tax to 0% EU B2B.
#   - Non-EU maps that included advance tax to 0% non-EU export.
#   - OSS B2C maps that included advance tax to destination-country included
#     OSS down-payment taxes.
#
# SAFE_EVAL   : no import/def/lambda/comprehension/with/getattr/hasattr/setattr/
#               eval/exec/open/dir/isinstance in executable code.
# ============================================================================

PAGE = 1
PAGE_SIZE = 32000

ACTION_NAME = 'READ-ONLY: BARANI tax + fiscal-position full verification dump'
SOURCE_ADV_TAX_NAME = 'SK 23% VAT Included — Down Payments'
NORMAL_SK_TAX_NAME = '23 % SK VAT'
DP_TEMPLATE_NAME = 'Down payment'
RECEIVING_IBAN_COMPACT = 'XX0000000000000000000000'
RECEIVING_BIC = 'YOURBICXXX'

Tax = env['account.tax'].sudo()
FP = env['account.fiscal.position'].sudo()
Account = env['account.account'].sudo()
Template = env['product.template'].sudo()
Product = env['product.product'].sudo()
Company = env.company.sudo()

lines = []
warns = []
fails = []

lines.append(ACTION_NAME)
lines.append('READ-ONLY:YES — no writes. PAGE=%s PAGE_SIZE=%s' % (PAGE, PAGE_SIZE))
lines.append('Purpose: verify Option-B gross-paid down-payment taxes + all fiscal-position mappings.')
lines.append('')

# ---------------------------------------------------------------------------
# 1) Company / bank / rounding context.
# ---------------------------------------------------------------------------
lines.append('============================================================')
lines.append('1) COMPANY / ROUNDING / BANK CONTEXT')
lines.append('============================================================')
lines.append('company id=%s name=%r currency=%s VAT=%s registry=%s fiscal_country=%s' % (
    Company.id,
    Company.name,
    Company.currency_id.name if Company.currency_id else '',
    Company.vat or '',
    Company.company_registry or '',
    Company.account_fiscal_country_id.name if Company.account_fiscal_country_id else '',
))
lines.append('tax_calculation_rounding_method=%s' % (Company.tax_calculation_rounding_method or ''))
bank_match_count = 0
if Company.partner_id:
    for bank in Company.partner_id.bank_ids:
        bic = ''
        bname = ''
        baddr = ''
        if bank.bank_id:
            bic = bank.bank_id.bic or ''
            bname = bank.bank_id.name or ''
            if bank.bank_id.street:
                baddr = bank.bank_id.street
            if bank.bank_id.zip or bank.bank_id.city:
                if baddr:
                    baddr = baddr + ', '
                if bank.bank_id.zip:
                    baddr = baddr + bank.bank_id.zip
                if bank.bank_id.zip and bank.bank_id.city:
                    baddr = baddr + ' '
                if bank.bank_id.city:
                    baddr = baddr + bank.bank_id.city
            if bank.bank_id.country:
                if baddr:
                    baddr = baddr + ', '
                baddr = baddr + bank.bank_id.country.name
        compact = (bank.acc_number or '').replace(' ', '')
        bic_compact = (bic or '').replace(' ', '')
        match = compact == RECEIVING_IBAN_COMPACT and bic_compact == RECEIVING_BIC
        if match:
            bank_match_count = bank_match_count + 1
        lines.append('  bank id=%s acc=%s bic=%s name=%r addr=%r MATCH=%s' % (
            bank.id, bank.acc_number or '', bic, bname, baddr, 'YES' if match else 'no'))
lines.append('confirmed receiving bank matches=%s' % bank_match_count)
if bank_match_count != 1:
    fails.append('Expected exactly one company bank matching confirmed IBAN/BIC; found %s.' % bank_match_count)
lines.append('')

# ---------------------------------------------------------------------------
# 2) Source taxes.
# ---------------------------------------------------------------------------
lines.append('============================================================')
lines.append('2) KEY TAXES / DOWN-PAYMENT PRODUCT')
lines.append('============================================================')
src_taxes = Tax.with_context(active_test=False).search([('name', '=', SOURCE_ADV_TAX_NAME)])
normal_taxes = Tax.with_context(active_test=False).search([('name', '=', NORMAL_SK_TAX_NAME)])
lines.append("source advance tax %r found=%s" % (SOURCE_ADV_TAX_NAME, len(src_taxes)))
source_tax = Tax.browse()
if len(src_taxes) == 1:
    source_tax = src_taxes[0]
    lines.append("  id=%s type=%s amount=%s included=%s active=%s desc=%r group=%r country=%r" % (
        source_tax.id, source_tax.type_tax_use, source_tax.amount, source_tax.price_include,
        source_tax.active, source_tax.description or '', source_tax.tax_group_id.name if source_tax.tax_group_id else '',
        source_tax.country_id.name if source_tax.country_id else ''))
    if source_tax.type_tax_use != 'sale':
        fails.append('Source advance tax is not a Sales tax.')
    if not source_tax.price_include:
        fails.append('Source advance tax is not Included in Price.')
    if abs((source_tax.amount or 0.0) - 23.0) > 0.0001:
        fails.append('Source advance tax is not 23%.')
    if not source_tax.description:
        fails.append('Source advance tax Label on Invoices is empty.')
else:
    fails.append('Expected exactly one source advance tax named %r.' % SOURCE_ADV_TAX_NAME)

lines.append("normal domestic source tax %r found=%s" % (NORMAL_SK_TAX_NAME, len(normal_taxes)))
normal_tax = Tax.browse()
if len(normal_taxes) == 1:
    normal_tax = normal_taxes[0]
    lines.append("  id=%s type=%s amount=%s included=%s active=%s desc=%r group=%r country=%r" % (
        normal_tax.id, normal_tax.type_tax_use, normal_tax.amount, normal_tax.price_include,
        normal_tax.active, normal_tax.description or '', normal_tax.tax_group_id.name if normal_tax.tax_group_id else '',
        normal_tax.country_id.name if normal_tax.country_id else ''))
else:
    fails.append('Expected exactly one normal domestic source tax named %r.' % NORMAL_SK_TAX_NAME)

# 2b) Tax repartition of key taxes.
for tx in src_taxes + normal_taxes:
    lines.append('')
    lines.append('  TAX DETAIL id=%s name=%r' % (tx.id, tx.name))
    lines.append('    invoice repartition:')
    for rl in tx.invoice_repartition_line_ids:
        tag_names = ''
        for tag in rl.tag_ids:
            if tag_names:
                tag_names = tag_names + ', '
            tag_names = tag_names + tag.name
        lines.append('      factor=%s repartition_type=%s account=%s %s tags=[%s]' % (
            rl.factor_percent, rl.repartition_type,
            rl.account_id.code if rl.account_id else '',
            rl.account_id.name if rl.account_id else '',
            tag_names))
    lines.append('    refund repartition:')
    for rl in tx.refund_repartition_line_ids:
        tag_names = ''
        for tag in rl.tag_ids:
            if tag_names:
                tag_names = tag_names + ', '
            tag_names = tag_names + tag.name
        lines.append('      factor=%s repartition_type=%s account=%s %s tags=[%s]' % (
            rl.factor_percent, rl.repartition_type,
            rl.account_id.code if rl.account_id else '',
            rl.account_id.name if rl.account_id else '',
            tag_names))

# 2c) account 324 and product.
acct_324 = Account.search([('code', '=', '324000')], limit=1)
if acct_324:
    lines.append('')
    lines.append('account 324000: id=%s name=%r deprecated=%s type=%s' % (
        acct_324.id, acct_324.name, acct_324.deprecated, acct_324.account_type))
else:
    fails.append('Account 324000 not found.')
    lines.append('account 324000: NOT FOUND')

dp_templates = Template.with_context(active_test=False).search([('name', '=', DP_TEMPLATE_NAME)])
lines.append('')
lines.append("down-payment product templates named %r found=%s" % (DP_TEMPLATE_NAME, len(dp_templates)))
dp_ok_count = 0
for tmpl in dp_templates:
    cat_path = ''
    cat = tmpl.categ_id
    depth = 0
    while cat and depth < 20:
        if cat_path:
            cat_path = cat.name + ' / ' + cat_path
        else:
            cat_path = cat.name
        cat = cat.parent_id
        depth = depth + 1
    income = tmpl.property_account_income_id or tmpl.categ_id.property_account_income_categ_id
    tax_names = ''
    source_tax_on_product = False
    for t in tmpl.taxes_id:
        if tax_names:
            tax_names = tax_names + ', '
        tax_names = tax_names + '%s(id=%s included=%s amount=%s)' % (t.name, t.id, t.price_include, t.amount)
        if source_tax and t.id == source_tax.id:
            source_tax_on_product = True
    lines.append("  template id=%s active=%s name=%r categ=%r income_path=%r taxes=[%s]" % (
        tmpl.id, tmpl.active, tmpl.name, cat_path, (income.code + ' ' + income.name) if income else '', tax_names))
    if income and income.code == '324000' and source_tax_on_product:
        dp_ok_count = dp_ok_count + 1
if dp_ok_count < 1:
    fails.append('No Down payment product template both resolves to account 324000 and uses the included source advance tax.')
lines.append('')

# ---------------------------------------------------------------------------
# 3) All taxes.
# ---------------------------------------------------------------------------
lines.append('============================================================')
lines.append('3) ALL SALE/PURCHASE TAXES')
lines.append('============================================================')
all_taxes = Tax.with_context(active_test=False).search([('type_tax_use', 'in', ['sale', 'purchase'])], order='type_tax_use,name,id')
empty_desc = 0
for tx in all_taxes:
    if not tx.description:
        empty_desc = empty_desc + 1
    inv_tax_accounts = ''
    inv_tags = ''
    for rl in tx.invoice_repartition_line_ids:
        if rl.repartition_type == 'tax':
            if rl.account_id:
                if inv_tax_accounts:
                    inv_tax_accounts = inv_tax_accounts + '; '
                inv_tax_accounts = inv_tax_accounts + rl.account_id.code + ' ' + rl.account_id.name
            for tag in rl.tag_ids:
                if inv_tags:
                    inv_tags = inv_tags + ', '
                inv_tags = inv_tags + tag.name
    ref_tax_accounts = ''
    ref_tags = ''
    for rl in tx.refund_repartition_line_ids:
        if rl.repartition_type == 'tax':
            if rl.account_id:
                if ref_tax_accounts:
                    ref_tax_accounts = ref_tax_accounts + '; '
                ref_tax_accounts = ref_tax_accounts + rl.account_id.code + ' ' + rl.account_id.name
            for tag in rl.tag_ids:
                if ref_tags:
                    ref_tags = ref_tags + ', '
                ref_tags = ref_tags + tag.name
    lines.append("TAX id=%s name=%r type=%s amount=%s included=%s active=%s desc=%r group=%r country=%r inv_accts=[%s] inv_tags=[%s] ref_accts=[%s] ref_tags=[%s]" % (
        tx.id, tx.name, tx.type_tax_use, tx.amount, tx.price_include, tx.active, tx.description or '',
        tx.tax_group_id.name if tx.tax_group_id else '', tx.country_id.name if tx.country_id else '',
        inv_tax_accounts, inv_tags, ref_tax_accounts, ref_tags))
lines.append('sale/purchase taxes total=%s; empty Label on Invoices=%s' % (len(all_taxes), empty_desc))
if empty_desc:
    fails.append('Some sale/purchase taxes have empty Label on Invoices.')
lines.append('')

# ---------------------------------------------------------------------------
# 4) All fiscal positions and mappings.
# ---------------------------------------------------------------------------
lines.append('============================================================')
lines.append('4) ALL FISCAL POSITIONS + TAX MAPPINGS')
lines.append('============================================================')
all_fps = FP.with_context(active_test=False).search([], order='sequence,name,id')
for fp in all_fps:
    note_text = ''
    if fp.note:
        note_text = str(fp.note).replace('\n', ' ')
        if len(note_text) > 220:
            note_text = note_text[:220] + '...'
    lines.append('')
    lines.append("FP id=%s name=%r active=%s sequence=%s auto=%s vat_required=%s country=%r group=%r zip=%r-%r foreign_vat=%r" % (
        fp.id, fp.name, fp.active, fp.sequence, fp.auto_apply, fp.vat_required,
        fp.country_id.name if fp.country_id else '',
        fp.country_group_id.name if fp.country_group_id else '',
        fp.zip_from or '', fp.zip_to or '', fp.foreign_vat or ''))
    lines.append('  note=%r' % note_text)
    if not fp.tax_ids:
        lines.append('  tax mappings: (none)')
    for mp in fp.tax_ids:
        src = mp.tax_src_id
        dst = mp.tax_dest_id
        lines.append("  map id=%s: SRC id=%s %r amount=%s incl=%s active=%s -> DST id=%s %r amount=%s incl=%s active=%s desc=%r group=%r" % (
            mp.id,
            src.id if src else 0, src.name if src else '', src.amount if src else '', src.price_include if src else '', src.active if src else '',
            dst.id if dst else 0, dst.name if dst else '', dst.amount if dst else '', dst.price_include if dst else '', dst.active if dst else '',
            dst.description if dst else '', dst.tax_group_id.name if dst and dst.tax_group_id else ''))
lines.append('')

# ---------------------------------------------------------------------------
# 5) Expected mapping verification matrix.
# ---------------------------------------------------------------------------
lines.append('============================================================')
lines.append('5) EXPECTED OPTION-B CONFIG VERIFICATION')
lines.append('============================================================')

# Domestic check
dom_fps = FP.with_context(active_test=False).search([('name', '=', 'Domestic (Slovakia)')])
lines.append("Domestic (Slovakia) fiscal positions found=%s" % len(dom_fps))
if len(dom_fps) != 1:
    fails.append('Expected exactly one Domestic (Slovakia) fiscal position.')
else:
    dom = dom_fps[0]
    source_mapped_dom = False
    for mp in dom.tax_ids:
        if source_tax and mp.tax_src_id and mp.tax_src_id.id == source_tax.id:
            source_mapped_dom = True
            lines.append("  Domestic maps source advance tax to %r included=%s amount=%s" % (
                mp.tax_dest_id.name if mp.tax_dest_id else '', mp.tax_dest_id.price_include if mp.tax_dest_id else '', mp.tax_dest_id.amount if mp.tax_dest_id else ''))
    if source_mapped_dom:
        warns.append('Domestic fiscal position maps the included advance tax; usually no mapping is needed if source tax is the domestic included tax.')
    else:
        lines.append('  OK: Domestic has no mapping for included source advance tax; product tax remains SK 23% included.')

# Intra-EU/Non-EU
for fname in ['Intra-EU', 'Non-EU']:
    fps = FP.with_context(active_test=False).search([('name', '=', fname)])
    lines.append('')
    lines.append("%s fiscal positions found=%s" % (fname, len(fps)))
    if len(fps) != 1:
        fails.append('Expected exactly one %s fiscal position.' % fname)
    else:
        fp = fps[0]
        src_adv_seen = False
        src_norm_seen = False
        for mp in fp.tax_ids:
            if source_tax and mp.tax_src_id and mp.tax_src_id.id == source_tax.id:
                src_adv_seen = True
                ok_zero = mp.tax_dest_id and abs(mp.tax_dest_id.amount or 0.0) < 0.0001
                lines.append("  advance mapping: %r -> %r amount=%s included=%s OK_ZERO=%s" % (
                    mp.tax_src_id.name, mp.tax_dest_id.name if mp.tax_dest_id else '',
                    mp.tax_dest_id.amount if mp.tax_dest_id else '', mp.tax_dest_id.price_include if mp.tax_dest_id else '', ok_zero))
                if not ok_zero:
                    fails.append('%s advance mapping destination is not 0%%.' % fname)
            if normal_tax and mp.tax_src_id and mp.tax_src_id.id == normal_tax.id:
                src_norm_seen = True
                ok_zero2 = mp.tax_dest_id and abs(mp.tax_dest_id.amount or 0.0) < 0.0001
                lines.append("  normal 23%% mapping: %r -> %r amount=%s included=%s OK_ZERO=%s" % (
                    mp.tax_src_id.name, mp.tax_dest_id.name if mp.tax_dest_id else '',
                    mp.tax_dest_id.amount if mp.tax_dest_id else '', mp.tax_dest_id.price_include if mp.tax_dest_id else '', ok_zero2))
        if not src_adv_seen:
            fails.append('%s does not map included advance source tax.' % fname)
        if not src_norm_seen:
            warns.append('%s does not map normal 23%% SK VAT source tax.' % fname)

# OSS B2C checks.
oss_total = 0
oss_ok = 0
oss_missing = 0
oss_bad = 0
oss_regular_missing = 0
oss_dup_names = 0
lines.append('')
lines.append('OSS B2C mapping verification:')
for fp in all_fps:
    if fp.name and fp.name.startswith('OSS B2C '):
        oss_total = oss_total + 1
        regular_dest = Tax.browse()
        advance_dest = Tax.browse()
        for mp in fp.tax_ids:
            if normal_tax and mp.tax_src_id and mp.tax_src_id.id == normal_tax.id:
                regular_dest = mp.tax_dest_id
            if source_tax and mp.tax_src_id and mp.tax_src_id.id == source_tax.id:
                advance_dest = mp.tax_dest_id
        if not regular_dest:
            oss_regular_missing = oss_regular_missing + 1
        if not advance_dest:
            oss_missing = oss_missing + 1
            lines.append("  FP %s %r: FAIL missing advance mapping; regular_dest=%r" % (fp.id, fp.name, regular_dest.name if regular_dest else ''))
        else:
            included_name_expected = ''
            if regular_dest:
                included_name_expected = regular_dest.name + ' Included — Down Payments'
            duplicate_count = 0
            if included_name_expected:
                duplicate_count = len(Tax.with_context(active_test=False).search([('name', '=', included_name_expected)]))
            if duplicate_count > 1:
                oss_dup_names = oss_dup_names + 1
            ok = True
            reasons = ''
            if not advance_dest.price_include:
                ok = False
                reasons = reasons + 'dest_not_included; '
            if not advance_dest.active:
                ok = False
                reasons = reasons + 'dest_inactive; '
            if regular_dest and abs((advance_dest.amount or 0.0) - (regular_dest.amount or 0.0)) > 0.0001:
                ok = False
                reasons = reasons + 'amount_mismatch; '
            if regular_dest and advance_dest.tax_group_id.id != regular_dest.tax_group_id.id:
                ok = False
                reasons = reasons + 'tax_group_mismatch; '
            if regular_dest and advance_dest.country_id.id != regular_dest.country_id.id:
                ok = False
                reasons = reasons + 'country_mismatch; '
            if regular_dest and advance_dest.type_tax_use != regular_dest.type_tax_use:
                ok = False
                reasons = reasons + 'type_mismatch; '
            # compare tax repartition tax accounts/tags as compact strings
            reg_inv = ''
            adv_inv = ''
            reg_ref = ''
            adv_ref = ''
            if regular_dest:
                for rl in regular_dest.invoice_repartition_line_ids:
                    if rl.repartition_type == 'tax':
                        piece = ''
                        if rl.account_id:
                            piece = piece + rl.account_id.code
                        piece = piece + '|'
                        for tg in rl.tag_ids:
                            piece = piece + tg.name + ','
                        if reg_inv:
                            reg_inv = reg_inv + ';'
                        reg_inv = reg_inv + piece
                for rl in advance_dest.invoice_repartition_line_ids:
                    if rl.repartition_type == 'tax':
                        piece = ''
                        if rl.account_id:
                            piece = piece + rl.account_id.code
                        piece = piece + '|'
                        for tg in rl.tag_ids:
                            piece = piece + tg.name + ','
                        if adv_inv:
                            adv_inv = adv_inv + ';'
                        adv_inv = adv_inv + piece
                for rl in regular_dest.refund_repartition_line_ids:
                    if rl.repartition_type == 'tax':
                        piece = ''
                        if rl.account_id:
                            piece = piece + rl.account_id.code
                        piece = piece + '|'
                        for tg in rl.tag_ids:
                            piece = piece + tg.name + ','
                        if reg_ref:
                            reg_ref = reg_ref + ';'
                        reg_ref = reg_ref + piece
                for rl in advance_dest.refund_repartition_line_ids:
                    if rl.repartition_type == 'tax':
                        piece = ''
                        if rl.account_id:
                            piece = piece + rl.account_id.code
                        piece = piece + '|'
                        for tg in rl.tag_ids:
                            piece = piece + tg.name + ','
                        if adv_ref:
                            adv_ref = adv_ref + ';'
                        adv_ref = adv_ref + piece
                if reg_inv != adv_inv:
                    ok = False
                    reasons = reasons + 'invoice_repartition_mismatch; '
                if reg_ref != adv_ref:
                    ok = False
                    reasons = reasons + 'refund_repartition_mismatch; '
            if ok:
                oss_ok = oss_ok + 1
            else:
                oss_bad = oss_bad + 1
            lines.append("  FP %s %r: regular=%r amount=%s incl=%s -> advance=%r amount=%s incl=%s STATUS=%s reasons=%s expected_name=%r name_candidates=%s" % (
                fp.id, fp.name,
                regular_dest.name if regular_dest else '', regular_dest.amount if regular_dest else '', regular_dest.price_include if regular_dest else '',
                advance_dest.name if advance_dest else '', advance_dest.amount if advance_dest else '', advance_dest.price_include if advance_dest else '',
                'OK' if ok else 'FAIL', reasons, included_name_expected, duplicate_count))
if oss_total < 1:
    fails.append('No OSS B2C fiscal positions found.')
if oss_missing:
    fails.append('OSS B2C fiscal positions missing advance mappings: %s.' % oss_missing)
if oss_bad:
    fails.append('OSS B2C fiscal positions with bad advance mappings: %s.' % oss_bad)
if oss_regular_missing:
    warns.append('OSS B2C fiscal positions missing regular 23%% mapping: %s.' % oss_regular_missing)
if oss_dup_names:
    warns.append('Some included OSS tax names are duplicated: %s fiscal positions affected.' % oss_dup_names)
lines.append('')
lines.append('OSS SUMMARY: total=%s OK=%s missing_advance=%s bad=%s regular_missing=%s duplicate_names=%s' % (
    oss_total, oss_ok, oss_missing, oss_bad, oss_regular_missing, oss_dup_names))
lines.append('')

# ---------------------------------------------------------------------------
# 6) Final summary.
# ---------------------------------------------------------------------------
lines.append('============================================================')
lines.append('6) FINAL VERIFICATION SUMMARY')
lines.append('============================================================')
if warns:
    lines.append('WARNINGS (%s):' % len(warns))
    for w in warns:
        lines.append('  WARNING: ' + w)
else:
    lines.append('WARNINGS: none')

if fails:
    lines.append('FAILURES (%s):' % len(fails))
    for f in fails:
        lines.append('  FAIL: ' + f)
    lines.append('')
    lines.append('RESULT: REVIEW/FAIL — configuration is not fully verified.')
else:
    lines.append('FAILURES: none')
    lines.append('')
    lines.append('RESULT: PASS — taxes/fiscal positions appear correctly set for Option-B gross-paid advances.')
lines.append('')
lines.append('EXPECTED DRAFT DPI TESTS AFTER PASS:')
lines.append('  Domestic 100.00 -> untaxed 81.30, VAT 18.70, total 100.00')
lines.append('  OSS France 100.00 -> untaxed 83.33, VAT 16.67, total 100.00')
lines.append('  OSS Finland 100.00 -> untaxed about 79.68, VAT about 20.32, total 100.00')
lines.append('  Intra-EU B2B 100.00 -> 0%% reverse charge, total 100.00')
lines.append('  Non-EU export 100.00 -> 0%% export, total 100.00')
lines.append('')
lines.append('NOTE: This audit checks configuration only. It does not verify POHODA export acceptance.')

full = '\n'.join(lines)
total = len(full)
if PAGE < 1:
    PAGE = 1
start = (PAGE - 1) * PAGE_SIZE
end = start + PAGE_SIZE
slice_text = full[start:end]
more = 'YES' if end < total else 'NO'
header = 'PAGE %s | chars %s-%s of %s | MORE REMAINS: %s\n' % (PAGE, start, min(end, total), total, more)
raise UserError(header + slice_text)
