# ============================================================================
# ACTION NAME : READ-ONLY: BARANI review-fields usage + standard alternatives v1
# MODEL       : Module (ir.module.module). Selected records are ignored.
# ACTION TO DO: Execute Python Code
# PURPOSE     : Axis-2 follow-up for BARANI commercial Q/SO/PF reports.
#
#               The field-provenance probe marked a small set of core fields as
#               REVIEW because DDS modules have extended the field metadata:
#                 - partner_id.vat
#                 - company_id.vat
#                 - company_id.name
#                 - company_id.company_registry
#                 - company_id.email
#                 - company_id.phone
#                 - company_id.logo
#
#               This probe checks whether those fields are actually used in QWeb
#               / view XML, whether their field definitions are core or custom,
#               whether Slovak/DDS-looking translations exist, and what standard
#               Odoo alternatives exist (for example company.partner_id.vat or
#               partner.commercial_partner_id.vat).
#
# READ-ONLY   : Performs NO create/write/unlink/set_param/commit. It reads only
#               metadata, views, translations if available, and a few sample
#               company/sale values. Output is raised via UserError.
#
# PRIVACY     : May display your own company VAT/email/phone and sample customer
#               VATs. Use only as an internal diagnostic.
#
# SAFE_EVAL   : no import / def / lambda / comprehension / with / getattr /
#               hasattr / setattr / eval / exec / open. No writes.
# ============================================================================

PAGE = 1
PAGE_SIZE = 30000
MAX_VIEW_HITS_PER_TOKEN = 12
MAX_TRANSLATION_HITS = 12
MAX_SAMPLE_SALE_ORDERS = 8

if PAGE < 1:
    raise UserError('ERROR: PAGE must be >= 1')
if PAGE_SIZE < 5000:
    raise UserError('ERROR: PAGE_SIZE must be >= 5000')

Field = env['ir.model.fields'].sudo()
Data = env['ir.model.data'].sudo()
Model = env['ir.model'].sudo()
View = env['ir.ui.view'].sudo()
Module = env['ir.module.module'].sudo()

has_modules_field = Field.search_count([('model', '=', 'ir.model.fields'), ('name', '=', 'modules')])
trans_model_count = Model.search_count([('model', '=', 'ir.translation')])

TARGET_FIELDS = [
    ('CUSTOMER_VAT', 'res.partner', 'vat', 'Customer VAT ID; printed as doc.partner_id.vat or commercial partner VAT'),
    ('COMPANY_VAT', 'res.company', 'vat', 'Seller VAT ID / IC DPH'),
    ('COMPANY_NAME', 'res.company', 'name', 'Seller company legal/display name'),
    ('COMPANY_REGISTRY', 'res.company', 'company_registry', 'Seller company registry / ICO'),
    ('COMPANY_EMAIL', 'res.company', 'email', 'Seller email'),
    ('COMPANY_PHONE', 'res.company', 'phone', 'Seller phone'),
    ('COMPANY_LOGO', 'res.company', 'logo', 'Seller logo binary used by report header'),
]

ALT_PATHS = [
    ('CUSTOMER_VAT', 'res.partner', 'vat', 'Canonical Odoo customer VAT field'),
    ('CUSTOMER_VAT', 'res.partner', 'commercial_partner_id.vat', 'Standard alternative when contact belongs to a parent company'),
    ('CUSTOMER_VAT', 'res.partner', 'parent_id.vat', 'Parent company VAT fallback candidate'),
    ('COMPANY_VAT', 'res.company', 'vat', 'Canonical Odoo company VAT field'),
    ('COMPANY_VAT', 'res.company', 'partner_id.vat', 'Standard partner-backed company VAT alternative'),
    ('COMPANY_NAME', 'res.company', 'name', 'Canonical company name'),
    ('COMPANY_NAME', 'res.company', 'partner_id.name', 'Partner-backed company name alternative'),
    ('COMPANY_REGISTRY', 'res.company', 'company_registry', 'Canonical company registry / ICO field'),
    ('COMPANY_REGISTRY', 'res.company', 'partner_id.company_registry', 'Partner-backed company registry alternative, if present'),
    ('COMPANY_EMAIL', 'res.company', 'email', 'Canonical company email'),
    ('COMPANY_EMAIL', 'res.company', 'partner_id.email', 'Partner-backed company email alternative'),
    ('COMPANY_PHONE', 'res.company', 'phone', 'Canonical company phone'),
    ('COMPANY_PHONE', 'res.company', 'partner_id.phone', 'Partner-backed company phone alternative'),
    ('COMPANY_LOGO', 'res.company', 'logo', 'Canonical company logo for PDF reports'),
    ('COMPANY_LOGO', 'res.company', 'logo_web', 'Standard web-optimized company logo, if installed'),
    ('COMPANY_LOGO', 'res.company', 'partner_id.image_1920', 'Partner image alternative; not preferred for company report header'),
]

TOKEN_PLAN = [
    ('CUSTOMER_VAT', 'partner_id.vat'),
    ('CUSTOMER_VAT', 'commercial_partner_id.vat'),
    ('CUSTOMER_VAT', 'parent_id.vat'),
    ('CUSTOMER_VAT', 'partner.vat'),
    ('CUSTOMER_VAT', 'field name="vat"'),
    ('COMPANY_VAT', 'company.vat'),
    ('COMPANY_VAT', 'company_id.vat'),
    ('COMPANY_VAT', 'res_company.vat'),
    ('COMPANY_VAT', 'o.company_id.vat'),
    ('COMPANY_VAT', 'doc.company_id.vat'),
    ('COMPANY_NAME', 'company.name'),
    ('COMPANY_NAME', 'company_id.name'),
    ('COMPANY_NAME', 'res_company.name'),
    ('COMPANY_NAME', 'o.company_id.name'),
    ('COMPANY_NAME', 'doc.company_id.name'),
    ('COMPANY_REGISTRY', 'company.company_registry'),
    ('COMPANY_REGISTRY', 'company_id.company_registry'),
    ('COMPANY_REGISTRY', 'res_company.company_registry'),
    ('COMPANY_REGISTRY', 'o.company_id.company_registry'),
    ('COMPANY_REGISTRY', 'doc.company_id.company_registry'),
    ('COMPANY_EMAIL', 'company.email'),
    ('COMPANY_EMAIL', 'company_id.email'),
    ('COMPANY_EMAIL', 'res_company.email'),
    ('COMPANY_EMAIL', 'o.company_id.email'),
    ('COMPANY_EMAIL', 'doc.company_id.email'),
    ('COMPANY_PHONE', 'company.phone'),
    ('COMPANY_PHONE', 'company_id.phone'),
    ('COMPANY_PHONE', 'res_company.phone'),
    ('COMPANY_PHONE', 'o.company_id.phone'),
    ('COMPANY_PHONE', 'doc.company_id.phone'),
    ('COMPANY_LOGO', 'company.logo'),
    ('COMPANY_LOGO', 'company_id.logo'),
    ('COMPANY_LOGO', 'res_company.logo'),
    ('COMPANY_LOGO', 'image_data_uri(company.logo)'),
    ('COMPANY_LOGO', 'company.logo_web'),
]

lines = []
lines.append('BARANI REVIEW-FIELDS USAGE + STANDARD ALTERNATIVES PROBE v1 READ-ONLY')
lines.append('READ-ONLY:YES - metadata/views/translations/sample reads only; output via UserError')
lines.append('PAGE=%s PAGE_SIZE=%s' % (PAGE, PAGE_SIZE))
lines.append('Scope: check REVIEW fields from the Q/SO/PF field-provenance audit before using them in standalone BARANI commercial templates.')
lines.append('')

lines.append('=' * 60)
lines.append('A. INSTALLED MODULES RELEVANT TO THIS CHECK')
lines.append('=' * 60)
mods = Module.search([('name', 'in', ['base', 'web', 'sale', 'sale_management', 'sale_stock', 'account', 'delivery', 'dds_localization_sk', 'dds_setupbase', 'dds_barani', 'studio_customization', 'web_studio'])], order='name')
for m in mods:
    lines.append('  %-28s state=%s' % (m.name, m.state))
lines.append('')

lines.append('=' * 60)
lines.append('B. FIELD METADATA FOR REVIEW FIELDS')
lines.append('=' * 60)
for item in TARGET_FIELDS:
    group = item[0]
    model_name = item[1]
    field_name = item[2]
    note = item[3]
    f = Field.search([('model', '=', model_name), ('name', '=', field_name)], limit=1)
    lines.append('%s  %s.%s' % (group, model_name, field_name))
    lines.append('  note: %s' % note)
    if not f:
        lines.append('  status: MISSING')
    else:
        xmls = Data.search([('model', '=', 'ir.model.fields'), ('res_id', '=', f.id)], order='module,name')
        owners = []
        for x in xmls:
            owners.append('%s.%s' % (x.module, x.name))
        mod_text = ''
        if has_modules_field:
            mod_text = f.modules or ''
        lines.append('  field id=%s type=%s relation=%s state=%s store=%s readonly=%s required=%s' % (f.id, f.ttype, f.relation or '', f.state or '', f.store, f.readonly, f.required))
        lines.append('  related=%s compute=%s translate=%s' % (f.related or '', f.compute or '', f.translate))
        lines.append('  modules=%s' % (mod_text or '(blank/not available)'))
        lines.append('  xmlid owners=%s' % (', '.join(owners) if owners else '(none)'))
        if ('dds' in (mod_text or '').lower()) or ('dodo' in (mod_text or '').lower()):
            lines.append('  interpretation: REVIEW - DDS appears in modules metadata, but this can mean the core field was extended/translated, not that the field itself is DDS-only.')
        else:
            lines.append('  interpretation: OK/CORE unless another section finds a custom-only dependency.')
    lines.append('')

lines.append('=' * 60)
lines.append('C. STANDARD ALTERNATIVE FIELD PATHS')
lines.append('=' * 60)
for alt in ALT_PATHS:
    group = alt[0]
    root_model = alt[1]
    path = alt[2]
    note = alt[3]
    model_name = root_model
    resolved = True
    chain_parts = []
    missing_at = ''
    parts = path.split('.')
    for part in parts:
        fld = Field.search([('model', '=', model_name), ('name', '=', part)], limit=1)
        if not fld:
            resolved = False
            missing_at = model_name + '.' + part
            chain_parts.append('%s.%s -> MISSING' % (model_name, part))
            break
        xmls = Data.search([('model', '=', 'ir.model.fields'), ('res_id', '=', fld.id)], order='module,name')
        owner_text = ''
        for x in xmls:
            if owner_text:
                owner_text = owner_text + ','
            owner_text = owner_text + x.module
        chain_parts.append('%s.%s[%s] owner=%s modules=%s' % (model_name, part, fld.ttype, owner_text or '(none)', (fld.modules or '') if has_modules_field else '(n/a)'))
        if fld.ttype in ['many2one', 'one2many', 'many2many'] and fld.relation:
            model_name = fld.relation
    status = 'OK'
    if not resolved:
        status = 'MISSING'
    else:
        chain_lower = ' '.join(chain_parts).lower()
        if 'dds' in chain_lower or 'dodo' in chain_lower or 'studio_customization' in chain_lower or 'web_studio' in chain_lower or '.x_' in path or '.x_studio_' in path:
            status = 'REVIEW'
    lines.append('[%s] %s %s.%s' % (status, group, root_model, path))
    lines.append('  note: %s' % note)
    lines.append('  chain: %s' % (' | '.join(chain_parts)))
    if missing_at:
        lines.append('  missing: %s' % missing_at)
lines.append('')

lines.append('=' * 60)
lines.append('D. VIEW / QWEB USAGE SCAN')
lines.append('=' * 60)
lines.append('Searches ir.ui.view.arch_db for exact tokens. Broad form tokens are only evidence, not proof of report dependency.')
for tp in TOKEN_PLAN:
    group = tp[0]
    token = tp[1]
    hits_total = View.search_count([('arch_db', 'ilike', token)])
    hits_qweb = View.search_count([('arch_db', 'ilike', token), ('type', '=', 'qweb')])
    lines.append('%s token=%r total_views=%s qweb_views=%s' % (group, token, hits_total, hits_qweb))
    hits = View.search([('arch_db', 'ilike', token)], order='type,id', limit=MAX_VIEW_HITS_PER_TOKEN)
    for v in hits:
        xmls = Data.search([('model', '=', 'ir.ui.view'), ('res_id', '=', v.id)], order='module,name')
        owner = ''
        for x in xmls:
            if owner:
                owner = owner + ','
            owner = owner + '%s.%s' % (x.module, x.name)
        inherit_txt = ''
        if v.inherit_id:
            inherit_txt = ' inherit_id=%s key=%s' % (v.inherit_id.id, v.inherit_id.key or '')
        lines.append('  - view id=%s type=%s key=%s name=%r owner=%s%s' % (v.id, v.type, v.key or '', v.name or '', owner or '(no xmlid)', inherit_txt))
    if hits_total > MAX_VIEW_HITS_PER_TOKEN:
        lines.append('  ... truncated view hits at %s' % MAX_VIEW_HITS_PER_TOKEN)
lines.append('')

lines.append('=' * 60)
lines.append('E. FIELD LABEL / TRANSLATION EVIDENCE')
lines.append('=' * 60)
if not trans_model_count:
    lines.append('ir.translation model not present in registry; skipping translation scan.')
else:
    Trans = env['ir.translation'].sudo()
    trans_has_module = 'module' in Trans._fields
    trans_has_lang = 'lang' in Trans._fields
    trans_has_src = 'src' in Trans._fields
    trans_has_value = 'value' in Trans._fields
    trans_has_name = 'name' in Trans._fields
    for item in TARGET_FIELDS:
        model_name = item[1]
        field_name = item[2]
        f = Field.search([('model', '=', model_name), ('name', '=', field_name)], limit=1)
        lines.append('%s.%s' % (model_name, field_name))
        if not f:
            lines.append('  MISSING FIELD')
        else:
            domain = [('res_id', '=', f.id)]
            if trans_has_name:
                domain = [('res_id', '=', f.id), ('name', 'ilike', 'ir.model.fields')]
            trs = Trans.search(domain, order='lang,name,id', limit=MAX_TRANSLATION_HITS)
            lines.append('  translation hits=%s shown=%s' % (Trans.search_count(domain), len(trs)))
            for tr in trs:
                module_txt = ''
                lang_txt = ''
                name_txt = ''
                src_txt = ''
                val_txt = ''
                if trans_has_module:
                    module_txt = tr.module or ''
                if trans_has_lang:
                    lang_txt = tr.lang or ''
                if trans_has_name:
                    name_txt = tr.name or ''
                if trans_has_src:
                    src_txt = tr.src or ''
                if trans_has_value:
                    val_txt = tr.value or ''
                lines.append('  - lang=%s module=%s name=%s src=%r value=%r' % (lang_txt, module_txt, name_txt, src_txt, val_txt))
lines.append('')

lines.append('=' * 60)
lines.append('F. LIVE COMPANY SAMPLE: CANONICAL vs PARTNER-BACKED VALUES')
lines.append('=' * 60)
comp = env.company.sudo()
cp = comp.partner_id.sudo()
lines.append('Company id=%s name=%r partner_id=%s partner_name=%r' % (comp.id, comp.name or '', cp.id if cp else '', cp.name or ''))
lines.append('  company.name                = %r' % (comp.name or ''))
lines.append('  company.partner_id.name     = %r' % ((cp.name or '') if cp else ''))
lines.append('  company.vat                 = %r' % (comp.vat or ''))
lines.append('  company.partner_id.vat      = %r' % ((cp.vat or '') if cp else ''))
lines.append('  company.company_registry    = %r' % (comp.company_registry or ''))
if cp and 'company_registry' in cp._fields:
    lines.append('  company.partner_id.company_registry = %r' % (cp.company_registry or ''))
else:
    lines.append('  company.partner_id.company_registry = (field missing)')
lines.append('  company.email               = %r' % (comp.email or ''))
lines.append('  company.partner_id.email    = %r' % ((cp.email or '') if cp else ''))
lines.append('  company.phone               = %r' % (comp.phone or ''))
lines.append('  company.partner_id.phone    = %r' % ((cp.phone or '') if cp else ''))
lines.append('  company.logo present        = %s' % bool(comp.logo))
if 'logo_web' in comp._fields:
    lines.append('  company.logo_web present    = %s' % bool(comp.logo_web))
else:
    lines.append('  company.logo_web            = (field missing)')
if cp and 'image_1920' in cp._fields:
    lines.append('  company.partner_id.image_1920 present = %s' % bool(cp.image_1920))
else:
    lines.append('  company.partner_id.image_1920 = (field missing)')
lines.append('')

lines.append('=' * 60)
lines.append('G. SAMPLE SALE ORDERS: PARTNER VAT vs COMMERCIAL PARTNER VAT')
lines.append('=' * 60)
if not Model.search_count([('model', '=', 'sale.order')]):
    lines.append('sale.order model not available; skipping sample sale orders.')
else:
    Sale = env['sale.order'].sudo()
    orders = Sale.search([], order='id desc', limit=MAX_SAMPLE_SALE_ORDERS)
    for o in orders:
        p = o.partner_id
        cp2 = p.commercial_partner_id
        lines.append('SO id=%s name=%s partner=%s partner_vat=%r commercial_partner=%s commercial_vat=%r' % (o.id, o.name or '', p.display_name or '', p.vat or '', cp2.display_name or '', cp2.vat or ''))
lines.append('')

lines.append('=' * 60)
lines.append('H. INTERPRETATION / RECOMMENDATION')
lines.append('=' * 60)
lines.append('1. If the field XML-ID owner is base/sale/account/web and DDS appears only in modules/translation/view-extension metadata, treat the field as REVIEW-OK for printing.')
lines.append('2. For customer VAT, the strongest standard display path is doc.partner_id.commercial_partner_id.vat or doc.partner_id.vat, depending whether child contacts are used.')
lines.append('3. For seller data, company.name/vat/company_registry/email/phone/logo are canonical Odoo report fields. Partner-backed alternatives are useful only if live samples show better data quality.')
lines.append('4. Do not replace these fields with dds_*, x_studio_* or brn_* alternatives. Those would create a real Axis-2 dependency.')
lines.append('5. A Slovak translation of a field label is not contamination by itself; a DDS-owned field or hard dependency in the QWeb arch is the contamination signal.')

text = '\n'.join(lines)
start = (PAGE - 1) * PAGE_SIZE
end = start + PAGE_SIZE
chunk = text[start:end]
footer = '\n\nPAGE %s | chars %s-%s of %s | MORE REMAINS: %s' % (PAGE, start, min(end, len(text)), len(text), 'YES' if end < len(text) else 'NO')
raise UserError(chunk + footer)
