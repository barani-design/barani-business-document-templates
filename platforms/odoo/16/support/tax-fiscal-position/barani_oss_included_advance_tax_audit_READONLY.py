# ============================================================================
# ACTION NAME : READ-ONLY: BARANI OSS included down-payment tax mapping audit
# MODEL       : Module (ir.module.module) or any model; selected records ignored.
# ACTION TO DO: Execute Python Code
# PURPOSE     : Verify whether OSS B2C fiscal positions map the gross-paid
#               down-payment source tax to PRICE-INCLUDED OSS destination taxes.
#
# READ-ONLY   : No create/write/unlink/set_param/commit. Raises UserError as output.
# SAFE_EVAL   : no import/def/lambda/comprehension/with/getattr/hasattr/setattr/
#               eval/exec/open/dir/isinstance in executable code.
# ============================================================================

PAGE = 1
PAGE_SIZE = 80000

ACTION_NAME = 'READ-ONLY: BARANI OSS included down-payment tax mapping audit'
SOURCE_ADVANCE_TAX_NAME = 'SK 23% VAT Included — Down Payments'
BASE_DOMESTIC_TAX_NAME = '23 % SK VAT'
INCLUDED_SUFFIX = ' Included — Down Payments'

Tax = env['account.tax'].sudo()
FP = env['account.fiscal.position'].sudo()

lines = []
lines.append(ACTION_NAME)
lines.append('READ-ONLY:YES — no writes. PAGE=%s PAGE_SIZE=%s' % (PAGE, PAGE_SIZE))
lines.append('Target: OSS B2C advance mappings should use destination-country VAT taxes with Included in Price=True.')
lines.append('')

# Resolve source advance tax.
source_taxes = Tax.search([('name', '=', SOURCE_ADVANCE_TAX_NAME), ('type_tax_use', '=', 'sale')])
lines.append('SOURCE ADVANCE TAX')
lines.append('  name=%r found=%s' % (SOURCE_ADVANCE_TAX_NAME, len(source_taxes)))
source_tax = False
if len(source_taxes) == 1:
    source_tax = source_taxes[0]
    lines.append('  id=%s amount=%s price_include=%s active=%s description=%r group=%r country=%r' % (
        source_tax.id, source_tax.amount, source_tax.price_include, source_tax.active,
        source_tax.description, source_tax.tax_group_id.name if source_tax.tax_group_id else '',
        source_tax.country_id.name if source_tax.country_id else ''
    ))
else:
    lines.append('  ERROR: expected exactly one source advance tax.')

base_taxes = Tax.search([('name', '=', BASE_DOMESTIC_TAX_NAME), ('type_tax_use', '=', 'sale')])
lines.append('')
lines.append('NORMAL DOMESTIC SOURCE TAX')
lines.append('  name=%r found=%s' % (BASE_DOMESTIC_TAX_NAME, len(base_taxes)))
base_tax = False
if len(base_taxes) == 1:
    base_tax = base_taxes[0]
    lines.append('  id=%s amount=%s price_include=%s active=%s description=%r' % (
        base_tax.id, base_tax.amount, base_tax.price_include, base_tax.active, base_tax.description
    ))
else:
    lines.append('  WARNING: expected exactly one normal 23 %% SK VAT source tax; regular mapping comparison may be incomplete.')
lines.append('')

fps = FP.search([('name', 'ilike', 'OSS B2C')], order='name')
lines.append('OSS B2C FISCAL POSITIONS FOUND: %s' % len(fps))
missing_adv = 0
bad_dest = 0
ok_dest = 0
candidate_exists = 0
for fp in fps:
    regular_map = False
    advance_map = False
    for mp in fp.tax_ids:
        if base_tax and mp.tax_src_id and mp.tax_src_id.id == base_tax.id:
            regular_map = mp
        if source_tax and mp.tax_src_id and mp.tax_src_id.id == source_tax.id:
            advance_map = mp

    lines.append('')
    lines.append('FP id=%s name=%r auto=%s vat_required=%s country=%r group=%r' % (
        fp.id, fp.name, fp.auto_apply, fp.vat_required,
        fp.country_id.name if fp.country_id else '', fp.country_group_id.name if fp.country_group_id else ''
    ))
    if regular_map:
        rd = regular_map.tax_dest_id
        lines.append('  regular mapping: %r -> %r id=%s amount=%s included=%s active=%s' % (
            regular_map.tax_src_id.name, rd.name if rd else '', rd.id if rd else '', rd.amount if rd else '', rd.price_include if rd else '', rd.active if rd else ''
        ))
    else:
        lines.append('  regular mapping: MISSING for %r' % BASE_DOMESTIC_TAX_NAME)

    if advance_map:
        ad = advance_map.tax_dest_id
        lines.append('  advance mapping: %r -> %r id=%s amount=%s included=%s active=%s' % (
            advance_map.tax_src_id.name, ad.name if ad else '', ad.id if ad else '', ad.amount if ad else '', ad.price_include if ad else '', ad.active if ad else ''
        ))
        if ad and ad.price_include:
            ok_dest = ok_dest + 1
            lines.append('  STATUS: OK — advance destination tax is price-included.')
        else:
            bad_dest = bad_dest + 1
            if ad:
                candidate_name = ad.name + INCLUDED_SUFFIX
                candidates = Tax.search([('name', '=', candidate_name), ('type_tax_use', '=', 'sale'), ('company_id', '=', ad.company_id.id)])
                if candidates:
                    candidate_exists = candidate_exists + len(candidates)
                lines.append('  STATUS: NEEDS FIX — advance destination is not price-included. Suggested included tax name=%r existing_candidates=%s' % (candidate_name, len(candidates)))
            else:
                lines.append('  STATUS: NEEDS FIX — advance mapping has no destination tax.')
    else:
        missing_adv = missing_adv + 1
        lines.append('  advance mapping: MISSING for %r' % SOURCE_ADVANCE_TAX_NAME)
        if regular_map and regular_map.tax_dest_id:
            rd2 = regular_map.tax_dest_id
            if rd2.price_include:
                lines.append('  suggested mapping: %r -> existing price-included tax %r' % (SOURCE_ADVANCE_TAX_NAME, rd2.name))
            else:
                lines.append('  suggested mapping: %r -> duplicate of %r with Included in Price=True' % (SOURCE_ADVANCE_TAX_NAME, rd2.name))

lines.append('')
lines.append('SUMMARY')
lines.append('  OK price-included advance destinations: %s' % ok_dest)
lines.append('  BAD non-included advance destinations: %s' % bad_dest)
lines.append('  Missing advance mappings: %s' % missing_adv)
lines.append('  Existing candidate included taxes found by suggested name: %s' % candidate_exists)
if bad_dest or missing_adv:
    lines.append('  RESULT: OSS advance mappings are NOT fully ready for gross-paid down payments.')
else:
    lines.append('  RESULT: OSS advance mappings appear ready for gross-paid down payments.')

text = '\n'.join(lines)
start = (PAGE - 1) * PAGE_SIZE
end = start + PAGE_SIZE
page_text = text[start:end]
more = 'YES' if end < len(text) else 'NO'
raise UserError('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s\n%s\n--- END PAGE %s | MORE REMAINS: %s ---' % (PAGE, start, min(end, len(text)), len(text), more, page_text, PAGE, more))
