# ============================================================================
# ACTION NAME : READ-ONLY: BARANI Option-B included down-payment tax audit
# MODEL       : Module (ir.module.module) or any model; selected records ignored.
# ACTION TO DO: Execute Python Code
# PURPOSE     : Verify the newly created "SK 23% VAT Included — Down Payments"
#               tax, the Down payment product tax assignment, and fiscal-position
#               mappings for domestic / Intra-EU / Non-EU / OSS advance flows.
#
# READ-ONLY   : search/read only. No create/write/unlink/set_param/commit.
# OUTPUT      : raises UserError with the report text.
# SAFE_EVAL   : no import/def/lambda/comprehension/with/getattr/hasattr/setattr/
#               eval/exec/open/dir/isinstance in executable code.
# ============================================================================

ACTION_NAME = 'READ-ONLY: BARANI Option-B included down-payment tax audit'

Tax = env['account.tax'].sudo()
Product = env['product.product'].sudo()
Template = env['product.template'].sudo()
FP = env['account.fiscal.position'].sudo()

NEW_TAX_NAME = 'SK 23% VAT Included — Down Payments'
SOURCE_TAX_NAME = '23 % SK VAT'
DP_PRODUCT_NAME = 'Down payment'

lines = []
lines.append(ACTION_NAME)
lines.append('READ-ONLY:YES — no writes. Selected records ignored.')
lines.append('')

new_taxes = Tax.with_context(active_test=False).search([('name', '=', NEW_TAX_NAME), ('type_tax_use', '=', 'sale')])
src_taxes = Tax.with_context(active_test=False).search([('name', '=', SOURCE_TAX_NAME), ('type_tax_use', '=', 'sale')])

lines.append('1) TARGET TAX')
lines.append('  target name=%r found=%s' % (NEW_TAX_NAME, len(new_taxes)))
if len(new_taxes) != 1:
    lines.append('  ERROR: expected exactly one sale tax with this name.')
else:
    t = new_taxes[0]
    lines.append('  id=%s name=%r active=%s amount=%s type=%s price_include=%s include_base_amount=%s' % (t.id, t.name, t.active, t.amount, t.amount_type, t.price_include, t.include_base_amount))
    lines.append('  description(Label on Invoices)=%r tax_group=%r country=%r company=%r' % (t.description, t.tax_group_id.name, t.country_id.name, t.company_id.name))
    ok = True
    if not t.active:
        ok = False
        lines.append('  FAIL: tax is inactive.')
    if t.amount_type != 'percent':
        ok = False
        lines.append('  FAIL: tax computation should be Percentage of Price / percent.')
    if abs((t.amount or 0.0) - 23.0) > 0.0001:
        ok = False
        lines.append('  FAIL: amount is not 23%.')
    if not t.price_include:
        ok = False
        lines.append('  FAIL: Included in Price is not checked. Gross-paid advances will not split correctly.')
    if not t.description:
        ok = False
        lines.append('  FAIL: Label on Invoices is empty.')
    if ok:
        lines.append('  PASS: core target-tax settings look correct for gross-paid domestic advances.')
lines.append('')

lines.append('2) SOURCE REGULAR 23% TAX COMPARISON')
lines.append('  source name=%r found=%s' % (SOURCE_TAX_NAME, len(src_taxes)))
if len(src_taxes) != 1:
    lines.append('  WARNING: expected exactly one regular source sale tax. Manual comparison needed.')
else:
    s = src_taxes[0]
    lines.append('  id=%s name=%r active=%s amount=%s type=%s price_include=%s include_base_amount=%s' % (s.id, s.name, s.active, s.amount, s.amount_type, s.price_include, s.include_base_amount))
    lines.append('  description=%r tax_group=%r country=%r company=%r' % (s.description, s.tax_group_id.name, s.country_id.name, s.company_id.name))
    if len(new_taxes) == 1:
        t = new_taxes[0]
        if t.tax_group_id.id != s.tax_group_id.id:
            lines.append('  WARNING: target tax group differs from regular 23%% tax.')
        if t.country_id.id != s.country_id.id:
            lines.append('  WARNING: target country differs from regular 23%% tax.')
        if t.company_id.id != s.company_id.id:
            lines.append('  WARNING: target company differs from regular 23%% tax.')
        if t.include_base_amount != s.include_base_amount:
            lines.append('  NOTE: Affect Base of Subsequent Taxes differs from regular 23%% tax. Usually harmless for a single tax, but best practice is to mirror the regular VAT tax except price_include.')
lines.append('')

def_dump_block = False
# no def allowed in BARANI safe-eval convention, so the blocks below are duplicated.

lines.append('3) TARGET TAX REPARTITION / TAX GRIDS')
if len(new_taxes) == 1:
    t = new_taxes[0]
    lines.append('  INVOICES:')
    for rl in t.invoice_repartition_line_ids:
        tag_names = ''
        first = True
        for tag in rl.tag_ids:
            if first:
                tag_names = tag.name
                first = False
            else:
                tag_names = tag_names + ', ' + tag.name
        lines.append('    type=%s factor=%s account=%s %s tags=%r' % (rl.repartition_type, rl.factor_percent, rl.account_id.code or '', rl.account_id.name or '', tag_names))
    lines.append('  REFUNDS:')
    for rl in t.refund_repartition_line_ids:
        tag_names = ''
        first = True
        for tag in rl.tag_ids:
            if first:
                tag_names = tag.name
                first = False
            else:
                tag_names = tag_names + ', ' + tag.name
        lines.append('    type=%s factor=%s account=%s %s tags=%r' % (rl.repartition_type, rl.factor_percent, rl.account_id.code or '', rl.account_id.name or '', tag_names))
    missing_tags = False
    for rl in t.invoice_repartition_line_ids:
        if not rl.tag_ids:
            missing_tags = True
    for rl in t.refund_repartition_line_ids:
        if not rl.tag_ids:
            missing_tags = True
    if missing_tags:
        lines.append('  WARNING: one or more repartition lines have no Tax Grid/tags. Compare with regular 23% SK VAT; VAT return/POHODA may require tags.')
    else:
        lines.append('  PASS: all target repartition lines have at least one tax grid/tag.')
lines.append('')

lines.append('4) REGULAR 23% TAX REPARTITION / TAX GRIDS (reference)')
if len(src_taxes) == 1:
    s = src_taxes[0]
    lines.append('  INVOICES:')
    for rl in s.invoice_repartition_line_ids:
        tag_names = ''
        first = True
        for tag in rl.tag_ids:
            if first:
                tag_names = tag.name
                first = False
            else:
                tag_names = tag_names + ', ' + tag.name
        lines.append('    type=%s factor=%s account=%s %s tags=%r' % (rl.repartition_type, rl.factor_percent, rl.account_id.code or '', rl.account_id.name or '', tag_names))
    lines.append('  REFUNDS:')
    for rl in s.refund_repartition_line_ids:
        tag_names = ''
        first = True
        for tag in rl.tag_ids:
            if first:
                tag_names = tag.name
                first = False
            else:
                tag_names = tag_names + ', ' + tag.name
        lines.append('    type=%s factor=%s account=%s %s tags=%r' % (rl.repartition_type, rl.factor_percent, rl.account_id.code or '', rl.account_id.name or '', tag_names))
lines.append('')

lines.append('5) DOWN PAYMENT PRODUCT TAX ASSIGNMENT')
templates = Template.with_context(active_test=False).search([('name', '=', DP_PRODUCT_NAME)])
products = Product.with_context(active_test=False).search([('product_tmpl_id', 'in', templates.ids)])
lines.append('  templates found=%s products found=%s' % (len(templates), len(products)))
for tmpl in templates:
    tax_text = ''
    first = True
    for tx in tmpl.taxes_id:
        part = 'id=%s %s included=%s active=%s' % (tx.id, tx.name, tx.price_include, tx.active)
        if first:
            tax_text = part
            first = False
        else:
            tax_text = tax_text + '; ' + part
    income = tmpl.property_account_income_id
    categ_income = tmpl.categ_id.property_account_income_categ_id
    lines.append('  tmpl id=%s name=%r category=%r income=%s %s categ_income=%s %s taxes=[%s]' % (tmpl.id, tmpl.name, tmpl.categ_id.complete_name, income.code or '', income.name or '', categ_income.code or '', categ_income.name or '', tax_text))
    if len(new_taxes) == 1:
        found_new = False
        for tx in tmpl.taxes_id:
            if tx.id == new_taxes[0].id:
                found_new = True
        if found_new:
            lines.append('    PASS: Down payment product uses the included advance tax.')
        else:
            lines.append('    FAIL: Down payment product does not use the included advance tax.')
    if (income and income.code == '324000') or ((not income) and categ_income and categ_income.code == '324000'):
        lines.append('    PASS: income/category path resolves to 324000.')
    else:
        lines.append('    WARNING: income/category path does not clearly resolve to 324000.')
lines.append('')

lines.append('6) FISCAL POSITION MAPPINGS FROM INCLUDED ADVANCE TAX')
if len(new_taxes) == 1:
    t = new_taxes[0]
    fps = FP.with_context(active_test=False).search([])
    for fp in fps:
        has_map = False
        for m in fp.tax_ids:
            if m.tax_src_id.id == t.id:
                if not has_map:
                    lines.append('  FP id=%s name=%r auto=%s vat_required=%s country=%r country_group=%r' % (fp.id, fp.name, fp.auto_apply, fp.vat_required, fp.country_id.name, fp.country_group_id.name))
                    has_map = True
                dst = m.tax_dest_id
                lines.append('    %s -> %s | dest amount=%s price_include=%s description=%r active=%s' % (m.tax_src_id.name, dst.name, dst.amount, dst.price_include, dst.description, dst.active))
                if fp.name and fp.name.startswith('OSS B2C') and not dst.price_include:
                    lines.append('    WARNING: OSS target tax is not price-included. Gross-paid OSS DPI may be wrong unless this is intentional.')
                if fp.name and fp.name == 'Domestic (Slovakia)':
                    lines.append('    NOTE: Domestic normally does not need a mapping if the DP product default tax is already SK included.')
    lines.append('  NOTE: no output for fiscal positions without an explicit mapping from the included advance tax.')
lines.append('')

lines.append('7) EXPECTED DRAFT TEST RESULTS')
lines.append('  Domestic gross 44.00 advance should produce: base approx 35.77, VAT approx 8.23, total 44.00.')
lines.append('  If it produces base 44.00 + VAT 10.12 = total 54.12, then Odoo is still using a tax-excluded path.')
lines.append('  OSS B2C gross advance should keep the gross amount fixed and split using destination-country VAT; this requires a price-included destination tax or an equivalent tested configuration.')
lines.append('')
raise UserError('\n'.join(lines)[:90000])
