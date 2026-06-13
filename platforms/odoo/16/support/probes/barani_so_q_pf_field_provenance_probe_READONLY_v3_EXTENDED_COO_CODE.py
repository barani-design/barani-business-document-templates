# ============================================================================
# ACTION NAME : READ-ONLY: BARANI SO/Q/PF field provenance probe v3 EXTENDED + COO CODE
# MODEL       : Module (ir.module.module). Selected records are ignored.
# ACTION TO DO: Execute Python Code
# PURPOSE     : Axis-2/data-layer audit for the planned standalone BARANI
#               Quotation / Sales Order / Pro-forma report family.
#
#               It enumerates every field path that the BARANI SO/Q/PF PDF is
#               likely to PRINT, including final candidates for HS Code, COO,
#               Incoterm, Payment Method, payment band bank data, tax labels,
#               and known DDS/Studio/BRN traps. It resolves each path through
#               ir.model.fields and ir.model.data and flags fields that would
#               re-couple the clean standalone template to DDS or Studio.
#
# READ-ONLY   : Performs NO create/write/unlink/set_param/commit. It reads only
#               ir.model.fields, ir.model.data, ir.module.module metadata and
#               raises UserError as the output channel.
#
# SAFE_EVAL   : plain server-action Python. No import / def / lambda /
#               comprehension / with / getattr / hasattr / setattr / eval /
#               exec / open. No writes.
# ============================================================================

PAGE = 1
PAGE_SIZE = 30000
MAX_PREFIX_SCAN_ROWS = 250

# Field-owner risk configuration.
DDS_PREFIXES = ['dds', 'dodo']
STUDIO_MODULES = ['studio_customization', 'web_studio']
CUSTOM_PREFIXES = ['x_studio_', 'x_', 'dds_', 'brn_']
CORE_SAFE_PREFIXES = ['base', 'sale', 'sale_management', 'sale_stock', 'stock', 'delivery', 'account', 'account_intrastat', 'product', 'uom', 'web', 'mail', 'l10n_']

# Planned printed / candidate field paths for BARANI SO/Q/PF.
# Group, root model, field path, note.
FIELD_PATHS = [
    # ------------------------------------------------------------------------
    # A. Sale document header / title / references
    # ------------------------------------------------------------------------
    ('DOCUMENT_CORE', 'sale.order', 'name', 'visible quotation/order/pro-forma reference'),
    ('DOCUMENT_CORE', 'sale.order', 'state', 'Quotation vs Order title logic'),
    ('DOCUMENT_CORE', 'sale.order', 'date_order', 'Order Date / Quotation Date'),
    ('DOCUMENT_CORE', 'sale.order', 'validity_date', 'Expiration date on quotations'),
    ('DOCUMENT_CORE', 'sale.order', 'client_order_ref', 'Customer reference'),
    ('DOCUMENT_CORE', 'sale.order', 'user_id.name', 'Salesperson, only if printed'),
    ('DOCUMENT_CORE', 'sale.order', 'payment_term_id.name', 'Payment Terms label'),
    ('DOCUMENT_CORE', 'sale.order', 'payment_term_id.note', 'Payment Terms note, only if printed'),
    ('DOCUMENT_CORE', 'sale.order', 'pricelist_id.name', 'Pricelist label, normally not printed'),
    ('DOCUMENT_CORE', 'sale.order', 'pricelist_id.currency_id.name', 'Currency through pricelist'),
    ('DOCUMENT_CORE', 'sale.order', 'currency_id.name', 'Currency label; related to pricelist'),
    ('DOCUMENT_CORE', 'sale.order', 'fiscal_position_id.name', 'Fiscal position, only if printed/debugged'),
    ('DOCUMENT_CORE', 'sale.order', 'note', 'Commercial note / terms'),

    # ------------------------------------------------------------------------
    # B. Incoterm candidates. Odoo versions/modules vary; missing is useful.
    # ------------------------------------------------------------------------
    ('INCOTERM_CANDIDATE', 'sale.order', 'incoterm.name', 'Likely sale.order incoterm field if installed'),
    ('INCOTERM_CANDIDATE', 'sale.order', 'incoterm.code', 'Incoterm code if incoterm field exists'),
    ('INCOTERM_CANDIDATE', 'sale.order', 'incoterm_location', 'Incoterm location if installed'),
    ('INCOTERM_CANDIDATE', 'sale.order', 'invoice_incoterm_id.name', 'Invoice-style incoterm name; probably missing on sale.order'),
    ('INCOTERM_CANDIDATE', 'sale.order', 'x_studio_incoterm', 'Negative control: Studio incoterm field'),

    # ------------------------------------------------------------------------
    # C. Payment-method candidates. If these are missing, PF can use static text
    #    "Wire transfer" and the bank band from company bank data.
    # ------------------------------------------------------------------------
    ('PAYMENT_METHOD_CANDIDATE', 'sale.order', 'payment_method_id.name', 'Candidate native payment method field; likely missing'),
    ('PAYMENT_METHOD_CANDIDATE', 'sale.order', 'payment_method_line_id.name', 'Candidate payment method line; likely missing'),
    ('PAYMENT_METHOD_CANDIDATE', 'sale.order', 'journal_id.name', 'Candidate payment journal; likely missing on sale.order'),
    ('PAYMENT_METHOD_CANDIDATE', 'sale.order', 'transaction_ids.provider_id.name', 'Online payment provider if website/ecommerce is used'),
    ('PAYMENT_METHOD_CANDIDATE', 'sale.order', 'authorized_transaction_ids.provider_id.name', 'Authorized payment provider if present'),
    ('PAYMENT_METHOD_CANDIDATE', 'sale.order', 'x_studio_payment_method', 'Negative control: Studio payment method field'),

    # ------------------------------------------------------------------------
    # D. Amounts and tax/totals. Do not t-call account.document_tax_totals;
    #    render inline from these core sale.order / sale.order.line values.
    # ------------------------------------------------------------------------
    ('TOTALS_CORE', 'sale.order', 'amount_untaxed', 'Untaxed Amount'),
    ('TOTALS_CORE', 'sale.order', 'amount_tax', 'Total VAT / tax'),
    ('TOTALS_CORE', 'sale.order', 'amount_total', 'Total incl. VAT / tax'),
    ('TOTALS_REVIEW', 'sale.order', 'tax_totals', 'Core computed dict; do not t-call patched template'),

    # ------------------------------------------------------------------------
    # E. Customer / addresses.
    # ------------------------------------------------------------------------
    ('CUSTOMER_CORE', 'sale.order', 'partner_id.name', 'Customer name'),
    ('CUSTOMER_CORE', 'sale.order', 'partner_id.street', 'Customer street'),
    ('CUSTOMER_CORE', 'sale.order', 'partner_id.street2', 'Customer street 2'),
    ('CUSTOMER_CORE', 'sale.order', 'partner_id.zip', 'Customer ZIP'),
    ('CUSTOMER_CORE', 'sale.order', 'partner_id.city', 'Customer city'),
    ('CUSTOMER_CORE', 'sale.order', 'partner_id.country_id.name', 'Customer country'),
    ('CUSTOMER_CORE', 'sale.order', 'partner_id.vat', 'Customer VAT ID; core field but may be DDS-extended'),
    ('CUSTOMER_CORE', 'sale.order', 'partner_id.company_registry', 'Customer Company ID / registry'),
    ('CUSTOMER_CORE', 'sale.order', 'partner_id.email', 'Customer email if printed'),
    ('CUSTOMER_CORE', 'sale.order', 'partner_id.phone', 'Customer phone if printed'),
    ('CUSTOMER_CORE', 'sale.order', 'partner_invoice_id.name', 'Invoice address name if distinct'),
    ('CUSTOMER_CORE', 'sale.order', 'partner_invoice_id.street', 'Invoice address street if distinct'),
    ('CUSTOMER_CORE', 'sale.order', 'partner_invoice_id.city', 'Invoice address city if distinct'),
    ('CUSTOMER_CORE', 'sale.order', 'partner_invoice_id.country_id.name', 'Invoice address country if distinct'),
    ('CUSTOMER_CORE', 'sale.order', 'partner_shipping_id.name', 'Shipping address name if distinct'),
    ('CUSTOMER_CORE', 'sale.order', 'partner_shipping_id.street', 'Shipping address street if distinct'),
    ('CUSTOMER_CORE', 'sale.order', 'partner_shipping_id.city', 'Shipping address city if distinct'),
    ('CUSTOMER_CORE', 'sale.order', 'partner_shipping_id.country_id.name', 'Shipping address country if distinct'),

    # ------------------------------------------------------------------------
    # F. Seller / company header and footer.
    # ------------------------------------------------------------------------
    ('COMPANY_CORE', 'sale.order', 'company_id.name', 'Seller company name'),
    ('COMPANY_CORE', 'sale.order', 'company_id.street', 'Seller street'),
    ('COMPANY_CORE', 'sale.order', 'company_id.street2', 'Seller street 2'),
    ('COMPANY_CORE', 'sale.order', 'company_id.zip', 'Seller ZIP'),
    ('COMPANY_CORE', 'sale.order', 'company_id.city', 'Seller city'),
    ('COMPANY_CORE', 'sale.order', 'company_id.country_id.name', 'Seller country'),
    ('COMPANY_CORE', 'sale.order', 'company_id.company_registry', 'Seller Company ID / ICO'),
    ('COMPANY_CORE', 'sale.order', 'company_id.vat', 'Seller VAT ID / IC DPH; core field but may be DDS-extended'),
    ('COMPANY_CORE', 'sale.order', 'company_id.email', 'Seller email'),
    ('COMPANY_CORE', 'sale.order', 'company_id.phone', 'Seller phone'),
    ('COMPANY_CORE', 'sale.order', 'company_id.website', 'Seller website'),
    ('COMPANY_CORE', 'sale.order', 'company_id.logo', 'Company logo'),

    # ------------------------------------------------------------------------
    # G. Receiving bank / PF payment band. These are provenance-only checks;
    #    the template should still filter to the approved receiving bank.
    # ------------------------------------------------------------------------
    ('BANK_BAND', 'sale.order', 'company_id.partner_id.bank_ids.acc_number', 'Company bank account / IBAN'),
    ('BANK_BAND', 'sale.order', 'company_id.partner_id.bank_ids.bank_id.name', 'Bank name'),
    ('BANK_BAND', 'sale.order', 'company_id.partner_id.bank_ids.bank_id.bic', 'BIC/SWIFT'),
    ('BANK_BAND', 'sale.order', 'company_id.partner_id.bank_ids.bank_id.street', 'Bank street'),
    ('BANK_BAND', 'sale.order', 'company_id.partner_id.bank_ids.bank_id.city', 'Bank city'),
    ('BANK_BAND', 'sale.order', 'company_id.partner_id.bank_ids.bank_id.zip', 'Bank ZIP'),
    ('BANK_BAND', 'sale.order', 'company_id.partner_id.bank_ids.bank_id.country.name', 'Bank country field variant A'),
    ('BANK_BAND', 'sale.order', 'company_id.partner_id.bank_ids.bank_id.country_id.name', 'Bank country field variant B'),
    ('BANK_BAND', 'sale.order', 'company_id.partner_id.bank_ids.currency_id.name', 'Bank account currency if present'),

    # ------------------------------------------------------------------------
    # H. Sale lines.
    # ------------------------------------------------------------------------
    ('LINE_CORE', 'sale.order', 'order_line.display_type', 'section/note/normal discriminator'),
    ('LINE_CORE', 'sale.order', 'order_line.sequence', 'line ordering'),
    ('LINE_CORE', 'sale.order', 'order_line.product_id.default_code', 'Internal Reference / SKU'),
    ('LINE_CORE', 'sale.order', 'order_line.product_id.name', 'Product display name if used'),
    ('LINE_CORE', 'sale.order', 'order_line.name', 'Printed sale line description'),
    ('LINE_CORE', 'sale.order', 'order_line.product_uom_qty', 'Ordered quantity'),
    ('LINE_CORE', 'sale.order', 'order_line.product_uom.name', 'Unit of measure'),
    ('LINE_CORE', 'sale.order', 'order_line.price_unit', 'Unit Price'),
    ('LINE_CORE', 'sale.order', 'order_line.discount', 'Discount %'),
    ('LINE_CORE', 'sale.order', 'order_line.tax_id.name', 'Tax name/label'),
    ('LINE_CORE', 'sale.order', 'order_line.tax_id.description', 'Tax label on invoices, if used'),
    ('LINE_CORE', 'sale.order', 'order_line.tax_id.amount', 'Tax rate for inline breakdown'),
    ('LINE_CORE', 'sale.order', 'order_line.tax_id.type_tax_use', 'Tax usage sanity'),
    ('LINE_CORE', 'sale.order', 'order_line.price_subtotal', 'Line subtotal excluding tax'),
    ('LINE_CORE', 'sale.order', 'order_line.price_total', 'Line total including tax'),
    ('LINE_CORE', 'sale.order', 'order_line.currency_id.name', 'Line currency'),

    # ------------------------------------------------------------------------
    # I. HS Code / COO candidates. Only use the field path that resolves to a
    #    core/official owner on this DB.
    # ------------------------------------------------------------------------
    ('HS_COO_CANDIDATE', 'sale.order', 'order_line.product_id.hs_code', 'HS code on product.product if present'),
    ('HS_COO_CANDIDATE', 'sale.order', 'order_line.product_id.product_tmpl_id.hs_code', 'HS code on product.template if present'),
    ('HS_COO_CANDIDATE', 'sale.order', 'order_line.product_id.intrastat_code_id.code', 'Intrastat code on product.product if present'),
    ('HS_COO_CANDIDATE', 'sale.order', 'order_line.product_id.product_tmpl_id.intrastat_code_id.code', 'Intrastat code on product.template if present'),
    ('HS_COO_CANDIDATE', 'sale.order', 'order_line.product_id.commodity_code_id.code', 'Commodity code on product.product if present'),
    ('HS_COO_CANDIDATE', 'sale.order', 'order_line.product_id.product_tmpl_id.commodity_code_id.code', 'Commodity code on product.template if present'),
    ('HS_COO_CANDIDATE', 'sale.order', 'order_line.product_id.country_of_origin.name', 'COO variant A name on product.product'),
    ('HS_COO_CANDIDATE', 'sale.order', 'order_line.product_id.country_of_origin.code', 'COO variant A ISO code on product.product; matches current VAT invoice usage'),
    ('HS_COO_CANDIDATE', 'sale.order', 'order_line.product_id.product_tmpl_id.country_of_origin.name', 'COO variant A name on template'),
    ('HS_COO_CANDIDATE', 'sale.order', 'order_line.product_id.product_tmpl_id.country_of_origin.code', 'COO variant A ISO code on template'),
    ('HS_COO_CANDIDATE', 'sale.order', 'order_line.product_id.country_of_origin_id.name', 'COO variant B name on product.product'),
    ('HS_COO_CANDIDATE', 'sale.order', 'order_line.product_id.country_of_origin_id.code', 'COO variant B ISO code on product.product'),
    ('HS_COO_CANDIDATE', 'sale.order', 'order_line.product_id.product_tmpl_id.country_of_origin_id.name', 'COO variant B name on template'),
    ('HS_COO_CANDIDATE', 'sale.order', 'order_line.product_id.product_tmpl_id.country_of_origin_id.code', 'COO variant B ISO code on template'),
    ('HS_COO_CANDIDATE', 'sale.order', 'order_line.product_id.origin_country_id.name', 'COO variant C name on product.product'),
    ('HS_COO_CANDIDATE', 'sale.order', 'order_line.product_id.origin_country_id.code', 'COO variant C ISO code on product.product'),
    ('HS_COO_CANDIDATE', 'sale.order', 'order_line.product_id.product_tmpl_id.origin_country_id.name', 'COO variant C name on template'),
    ('HS_COO_CANDIDATE', 'sale.order', 'order_line.product_id.product_tmpl_id.origin_country_id.code', 'COO variant C ISO code on template'),
    ('HS_COO_CANDIDATE', 'sale.order', 'order_line.product_id.intrastat_origin_country_id.name', 'COO variant D name on product.product'),
    ('HS_COO_CANDIDATE', 'sale.order', 'order_line.product_id.intrastat_origin_country_id.code', 'COO variant D ISO code on product.product'),
    ('HS_COO_CANDIDATE', 'sale.order', 'order_line.product_id.product_tmpl_id.intrastat_origin_country_id.name', 'COO variant D name on template'),
    ('HS_COO_CANDIDATE', 'sale.order', 'order_line.product_id.product_tmpl_id.intrastat_origin_country_id.code', 'COO variant D ISO code on template'),

    # ------------------------------------------------------------------------
    # J. Known traps / negative controls. These should be BLOCK/MISSING.
    # ------------------------------------------------------------------------
    ('KNOWN_TRAP', 'sale.order', 'partner_id.dds_tax_id', 'DDS partner tax helper seen in copied reports'),
    ('KNOWN_TRAP', 'sale.order', 'order_line.x_studio_hs_code', 'Studio HS field if it exists'),
    ('KNOWN_TRAP', 'sale.order', 'order_line.x_studio_country_of_origin', 'Studio COO field if it exists'),
    ('KNOWN_TRAP', 'sale.order', 'order_line.product_id.x_studio_hs_code', 'Studio HS on product if it exists'),
    ('KNOWN_TRAP', 'sale.order', 'order_line.product_id.x_studio_country_of_origin', 'Studio COO on product if it exists'),
    ('KNOWN_TRAP', 'product.template', 'brn_date_code_lot_code', 'BRN-looking field; should prove dds_barani ownership'),
    ('KNOWN_TRAP', 'product.template', 'brn_alternative_part_number_1', 'BRN-looking field; should prove dds_barani ownership'),
    ('KNOWN_TRAP', 'product.template', 'brn_alternative_part_number_2', 'BRN-looking field; should prove dds_barani ownership'),
    ('KNOWN_TRAP', 'product.template', 'brn_notes', 'BRN-looking field; should prove dds_barani ownership'),
]

SCAN_MODELS = [
    'sale.order',
    'sale.order.line',
    'res.partner',
    'res.company',
    'res.partner.bank',
    'res.bank',
    'product.product',
    'product.template',
    'account.tax',
    'account.payment.term',
    'account.incoterms',
    'uom.uom',
    'res.currency',
    'res.country',
]

if PAGE < 1:
    raise UserError('ERROR: PAGE must be >= 1')
if PAGE_SIZE < 5000:
    raise UserError('ERROR: PAGE_SIZE must be >= 5000')

Field = env['ir.model.fields'].sudo()
Data = env['ir.model.data'].sudo()
Model = env['ir.model'].sudo()
Module = env['ir.module.module'].sudo()

has_modules_field = Field.search_count([('model', '=', 'ir.model.fields'), ('name', '=', 'modules')])

lines = []
lines.append('BARANI SO/Q/PF FIELD PROVENANCE PROBE v3 EXTENDED + COO CODE READ-ONLY')
lines.append('READ-ONLY:YES - metadata read only; output raised via UserError')
lines.append('PAGE=%s PAGE_SIZE=%s' % (PAGE, PAGE_SIZE))
lines.append('Scope: standalone BARANI sale.order Quotation / Sales Order / Pro-forma PDF')
lines.append('Axis audited: DATA / FIELD provenance. This complements the QWeb render-chain audit.')
lines.append('')
lines.append('Risk status rules:')
lines.append('  OK                 : field path resolves with no detected custom/DDS/Studio owner risk')
lines.append('  REVIEW             : related/computed, many-record traversal, unknown owner, or DDS extended a core field')
lines.append('  BLOCK_DDS_STUDIO   : dds_/dodo/studio-owned custom field or explicit dds_/x_studio_/x_/brn_ field name')
lines.append('  MISSING            : field path does not exist; a t-field/t-esc path would fail')
lines.append('')

# Installed module snapshot.
lines.append('============================================================')
lines.append('A. INSTALLED MODULES RELEVANT TO THIS CHECK')
lines.append('============================================================')
mod_names = ['sale', 'sale_management', 'sale_stock', 'delivery', 'account', 'account_intrastat', 'stock', 'product', 'uom', 'base', 'web', 'mail', 'web_studio', 'studio_customization', 'dds_barani', 'dds_setupbase', 'dds_setupbase_stock', 'dds_localization_sk', 'dds_down_payments_sk']
mods = Module.search([('name', 'in', mod_names)], order='name')
if not mods:
    lines.append('  (none of the monitored modules were found by name)')
for m in mods:
    lines.append('  %-28s state=%s' % (m.name, m.state))
lines.append('')

n_ok = 0
n_review = 0
n_block = 0
n_missing = 0
actions = []

lines.append('============================================================')
lines.append('B. FIELD PATH RESOLUTION')
lines.append('============================================================')

for item in FIELD_PATHS:
    group = item[0]
    root_model = item[1]
    path = item[2]
    note = item[3]

    current_model = root_model
    parts = path.split('.')
    chain = []
    missing = False
    hard_block = False
    review = False
    reasons = []

    for fname in parts:
        frec = Field.search([('model', '=', current_model), ('name', '=', fname)], limit=1)
        if not frec:
            missing = True
            reasons.append('missing %s.%s' % (current_model, fname))
            chain.append('%s.%s -> MISSING' % (current_model, fname))
            break

        xmls = Data.search([('model', '=', 'ir.model.fields'), ('res_id', '=', frec.id)], order='module,name')
        xml_mods = []
        for x in xmls:
            if x.module not in xml_mods:
                xml_mods.append(x.module)

        module_text = ''
        if has_modules_field:
            module_text = frec.modules or ''
        module_hits = []
        if module_text:
            raw_mods = module_text.replace(',', ' ').split(' ')
            for rm in raw_mods:
                if rm and rm not in module_hits:
                    module_hits.append(rm)

        # Field-name prefix risk.
        for pfx in CUSTOM_PREFIXES:
            if fname.startswith(pfx):
                if pfx == 'x_':
                    # x_studio_ already caught by same block; plain x_ still custom.
                    hard_block = True
                    reasons.append('custom field-name prefix %s on %s.%s' % (pfx, current_model, fname))
                else:
                    hard_block = True
                    reasons.append('blocked field-name prefix %s on %s.%s' % (pfx, current_model, fname))

        # Owner module risk. A core XML-ID owner makes DDS in modules a REVIEW,
        # not an automatic BLOCK, because core fields such as res.partner.vat may
        # be extended by DDS but still exist without DDS.
        has_core_xml_owner = False
        has_dds_xml_owner = False
        has_studio_xml_owner = False
        if xml_mods:
            for xm in xml_mods:
                xm_lower = (xm or '').lower()
                xm_is_core = False
                for cp in CORE_SAFE_PREFIXES:
                    if xm_lower == cp or xm_lower.startswith(cp):
                        xm_is_core = True
                if xm_is_core:
                    has_core_xml_owner = True
                for dp in DDS_PREFIXES:
                    if xm_lower.startswith(dp):
                        has_dds_xml_owner = True
                if xm_lower in STUDIO_MODULES:
                    has_studio_xml_owner = True
        else:
            review = True
            reasons.append('no ir.model.data XML-ID owner visible for %s.%s' % (current_model, fname))

        has_dds_modules_text = False
        has_studio_modules_text = False
        for mh in module_hits:
            ml = (mh or '').lower()
            for dp in DDS_PREFIXES:
                if ml.startswith(dp):
                    has_dds_modules_text = True
            if ml in STUDIO_MODULES:
                has_studio_modules_text = True

        if has_dds_xml_owner or has_studio_xml_owner:
            if has_core_xml_owner and not fname.startswith('dds_') and not fname.startswith('x_') and not fname.startswith('brn_'):
                review = True
                reasons.append('core field has additional DDS/Studio XML-ID owner; verify but field name is core')
            else:
                hard_block = True
                reasons.append('XML-ID owner is DDS/Studio for %s.%s' % (current_model, fname))

        if has_dds_modules_text or has_studio_modules_text:
            if has_core_xml_owner and not fname.startswith('dds_') and not fname.startswith('x_') and not fname.startswith('brn_'):
                review = True
                reasons.append('core field modules include DDS/Studio extension; not a field-name dependency')
            else:
                hard_block = True
                reasons.append('field.modules includes DDS/Studio without core XML-ID owner')

        if frec.related:
            review = True
            reasons.append('related=%s' % frec.related)
        if frec.compute:
            review = True
            reasons.append('computed field')

        rel = ''
        if frec.relation:
            rel = ' -> %s' % frec.relation
        owner_note = ''
        if xml_mods:
            owner_note = ' xmlid_owner=%s' % ','.join(xml_mods)
        if module_hits:
            owner_note = owner_note + ' modules=%s' % ','.join(module_hits)
        chain.append('%s.%s[%s%s]%s' % (current_model, fname, frec.ttype, rel, owner_note))

        if frec.ttype in ('one2many', 'many2many'):
            review = True
            reasons.append('many-record traversal through %s.%s; template must iterate/filter deliberately' % (current_model, fname))

        if frec.relation and frec.ttype in ('many2one', 'one2many', 'many2many'):
            current_model = frec.relation
        else:
            # If this is not the last part, the path is invalid.
            if fname != parts[-1]:
                missing = True
                reasons.append('cannot traverse through non-relational field %s.%s' % (current_model, fname))
                break

    status = 'OK'
    if missing:
        status = 'MISSING'
        n_missing = n_missing + 1
    else:
        if hard_block:
            status = 'BLOCK_DDS_STUDIO'
            n_block = n_block + 1
        else:
            if review:
                status = 'REVIEW'
                n_review = n_review + 1
            else:
                n_ok = n_ok + 1

    lines.append('[%s] %-24s %s.%s' % (status, group, root_model, path))
    lines.append('  note: %s' % note)
    lines.append('  chain: %s' % ' | '.join(chain))
    if reasons:
        lines.append('  reasons: %s' % '; '.join(reasons))
    lines.append('')

    if status != 'OK':
        actions.append('%-16s %-24s %s.%s -- %s' % (status, group, root_model, path, '; '.join(reasons)))

lines.append('============================================================')
lines.append('C. PREFIX SCAN FOR DDS/STUDIO/BRN FIELDS ON RELEVANT MODELS')
lines.append('============================================================')
for sm in SCAN_MODELS:
    lines.append('MODEL %s' % sm)
    found_any = False
    for pfx in CUSTOM_PREFIXES:
        fs = Field.search([('model', '=', sm), ('name', 'ilike', pfx)], limit=MAX_PREFIX_SCAN_ROWS, order='name')
        for f in fs:
            if f.name.startswith(pfx):
                found_any = True
                xmls = Data.search([('model', '=', 'ir.model.fields'), ('res_id', '=', f.id)], order='module,name')
                owners = []
                for x in xmls:
                    owner_key = '%s.%s' % (x.module, x.name)
                    if owner_key not in owners:
                        owners.append(owner_key)
                lines.append('  %s %-35s type=%s relation=%s xmlids=%s' % (pfx, f.name, f.ttype, f.relation or '', ','.join(owners) or '(none)'))
    if not found_any:
        lines.append('  (no monitored prefixes found)')
    lines.append('')

lines.append('============================================================')
lines.append('D. SUMMARY / ACTION LIST')
lines.append('============================================================')
lines.append('OK                 : %s' % n_ok)
lines.append('REVIEW             : %s' % n_review)
lines.append('BLOCK_DDS_STUDIO   : %s' % n_block)
lines.append('MISSING            : %s' % n_missing)
lines.append('')
if not actions:
    lines.append('No non-OK field paths found.')
else:
    lines.append('Resolve these before building the BARANI template:')
    for a in actions:
        lines.append('  - %s' % a)
lines.append('')
lines.append('Interpretation for the Q/SO/PF build:')
lines.append('  - Use OK core fields freely.')
lines.append('  - REVIEW fields can be used only after confirming the related/computed source does not terminate in DDS/Studio custom data.')
lines.append('  - Core fields such as partner_id.vat or company_id.vat may show DDS in field.modules because DDS extended the core field metadata; that is not the same as a missing-field dependency. Treat as REVIEW, not automatic block.')
lines.append('  - BLOCK_DDS_STUDIO fields must not be referenced by the standalone BARANI template unless you consciously accept that dependency.')
lines.append('  - MISSING fields must not be referenced; use the resolving HS/COO/incoterm/payment candidate that actually exists.')
lines.append('  - Do not t-call account.document_tax_totals; render totals inline from amount_untaxed / amount_tax / amount_total and order_line.tax_id values.')
lines.append('')
lines.append('Expected clean decisions unless this output proves otherwise:')
lines.append('  - Payment Method on PF: static "Wire transfer" plus approved bank band, not a sale.order payment-method field.')
lines.append('  - Incoterm: use sale.order.incoterm / incoterm_location only if this run resolves them as core/official fields.')
lines.append('  - HS Code / COO: use the product path that resolves as core/official; for COO prefer the .code path if it resolves, to match the VAT invoice short COO column. Never use x_studio_* or brn_* fields.')

full = '\n'.join(lines)
start = (PAGE - 1) * PAGE_SIZE
end = start + PAGE_SIZE
page_text = full[start:end]
more = 'NO'
if end < len(full):
    more = 'YES'
header = 'PAGE %s | chars %s-%s of %s | MORE REMAINS: %s\n' % (PAGE, start, end, len(full), more)
out = header + page_text
if more == 'YES':
    out = out + '\n--- END PAGE %s | MORE REMAINS: YES ---\nSet PAGE=%s and rerun to continue.' % (PAGE, PAGE + 1)
else:
    out = out + '\n--- END PAGE %s | MORE REMAINS: NO ---' % PAGE
raise UserError(out[:90000])
