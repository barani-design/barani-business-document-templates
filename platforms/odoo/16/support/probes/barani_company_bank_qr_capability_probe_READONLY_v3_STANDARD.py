# ============================================================================
# ACTION NAME : READ-ONLY: BARANI bank/IBAN + QR capability + VAT layout band dump v3
# MODEL       : Company (res.company). Selected records are ignored.
# ACTION TO DO: Execute Python Code
# CREATE AT   : Settings -> Technical -> Actions -> Server Actions -> New
# RUN BY      : Save, then run from the server-action form or Action menu.
#
# PURPOSE     : Read-only input probe for the BARANI Q/PF/PO layout project.
#               It answers the payment-band questions before cloning the RI/DPI
#               visual design into BARANI commercial reports:
#                 (1) company bank accounts: IBAN/account + BIC + bank name +
#                     bank address;
#                 (2) installed QR/SEPA/by-square support modules;
#                 (3) QR/proxy fields on res.partner.bank;
#                 (4) the live barani_vat QWeb views, with focused bank/payment
#                     token windows and optional full arch for visual cloning.
#
# SCOPE NOTE  : PF may need the red payment band. Quotation/SO payment-band use
#               is a business decision. PO should normally NOT show a payment
#               request band; it may reuse the same visual layout without the band.
#
# READ-ONLY   : YES. This action performs search/read only. It does NOT call
#               create/write/unlink/set_param/commit and returns output only via
#               raise UserError. It will show company bank data and QWeb XML in
#               the popup, so run as an admin and copy results only to BARANI docs.
#
# SAFE_EVAL   : no import / def / lambda / comprehension / with / getattr /
#               hasattr / setattr / eval / exec / open / try-except.
# ============================================================================

ACTION_NAME = 'READ-ONLY: BARANI bank/IBAN + QR capability + VAT layout band dump v3'
PAGE = 1
PAGE_SIZE = 15000
DUMP_FULL_ARCH = True
MAX_TOKEN_WINDOWS_PER_TOKEN = 8

if PAGE < 1:
    raise UserError('PAGE must be >= 1')

Company = env['res.company'].sudo()
Bank    = env['res.partner.bank'].sudo()
ResBank = env['res.bank'].sudo()
Module  = env['ir.module.module'].sudo()
IMF     = env['ir.model.fields'].sudo()
View    = env['ir.ui.view'].sudo()

lines = []
lines.append(ACTION_NAME)
lines.append('READ-ONLY:YES | OUTPUT=paged UserError | PAGE=%s | PAGE_SIZE=%s' % (PAGE, PAGE_SIZE))
lines.append('DUMP_FULL_ARCH=%s | selected records ignored' % DUMP_FULL_ARCH)
lines.append('')
lines.append('SAFETY SUMMARY')
lines.append('  - search/read only; no business data or technical metadata is written')
lines.append('  - output contains company bank details and full QWeb arch when DUMP_FULL_ARCH=True')
lines.append('  - purpose is to clone the approved RI/DPI visual shell without touching it')
lines.append('')

# ---------------------------------------------------------------------------
# 1) Company bank accounts incl. bank NAME + ADDRESS
# ---------------------------------------------------------------------------
lines.append('==== 1) COMPANY BANK ACCOUNTS (IBAN/BIC/name/address) ====')
lines.append('International wire baseline: beneficiary/company, IBAN, BIC/SWIFT, bank name, bank address.')
lines.append('')

comps = Company.search([])
if not comps:
    lines.append('(no companies visible to this server action)')

for c in comps:
    lines.append('COMPANY: %s (id=%s)' % (c.name, c.id))
    banks = Bank.browse([])
    if c.partner_id:
        banks = c.partner_id.bank_ids
    if not banks:
        lines.append('  (no bank accounts on company.partner_id.bank_ids)')
    for b in banks:
        acc = ''
        if 'acc_number' in Bank._fields:
            acc = b.acc_number or ''
        cur = ''
        if 'currency_id' in Bank._fields and b.currency_id:
            cur = b.currency_id.name or ''

        bankname = ''
        bic = ''
        bstreet = ''
        bstreet2 = ''
        bcity = ''
        bzip = ''
        bcountry = ''
        if b.bank_id:
            if 'name' in ResBank._fields:
                bankname = b.bank_id.name or ''
            if 'bic' in ResBank._fields:
                bic = b.bank_id.bic or ''
            if 'street' in ResBank._fields:
                bstreet = b.bank_id.street or ''
            if 'street2' in ResBank._fields:
                bstreet2 = b.bank_id.street2 or ''
            if 'city' in ResBank._fields:
                bcity = b.bank_id.city or ''
            if 'zip' in ResBank._fields:
                bzip = b.bank_id.zip or ''
            if 'country' in ResBank._fields and b.bank_id.country:
                bcountry = b.bank_id.country.name or ''
            if not bcountry and 'country_id' in ResBank._fields and b.bank_id.country_id:
                bcountry = b.bank_id.country_id.name or ''

        missing = []
        if not acc:
            missing.append('IBAN/account')
        if not bic:
            missing.append('BIC/SWIFT')
        if not bankname:
            missing.append('bank name')
        if not bstreet and not bcity and not bcountry:
            missing.append('bank address')

        lines.append('  BANK ACCOUNT id=%s' % b.id)
        lines.append('     IBAN/acc   = %s' % acc)
        lines.append('     BIC/SWIFT  = %s | currency = %s' % (bic, cur))
        lines.append('     bank name  = %s' % bankname)
        lines.append('     bank addr  = %s %s, %s %s, %s' % (bstreet, bstreet2, bzip, bcity, bcountry))
        if missing:
            lines.append('     MISSING FOR COMPLETE INTERNATIONAL WIRE BAND: %s' % ', '.join(missing))
        else:
            lines.append('     COMPLETE: YES for baseline international wire display')
    lines.append('')

# ---------------------------------------------------------------------------
# 2) Installed QR / SEPA / PAY-BY-SQUARE modules
# ---------------------------------------------------------------------------
lines.append('==== 2) INSTALLED QR / SEPA / PAY-BY-SQUARE MODULES ====')
mods = Module.search(['&', ('state', '=', 'installed'), '|', '|',
                      ('name', 'ilike', 'qr'),
                      ('name', 'ilike', 'sepa'),
                      ('name', 'ilike', 'square')], order='name')
if not mods:
    lines.append('  (none found)')
for m in mods:
    lines.append('  %s : %s' % (m.name, m.shortdesc or ''))
lines.append('  NOTE: EPC/SEPA QR is usually account_qr_code_sepa. Slovak PAY-by-square requires a separate module if it is not listed above.')
lines.append('')

# ---------------------------------------------------------------------------
# 3) QR / proxy fields on res.partner.bank
# ---------------------------------------------------------------------------
lines.append('==== 3) QR / PROXY FIELDS ON res.partner.bank ====')
qfields = IMF.search(['&', ('model', '=', 'res.partner.bank'), '|', '|',
                      ('name', 'ilike', 'qr'),
                      ('name', 'ilike', 'proxy'),
                      ('name', 'ilike', 'square')], order='name')
if not qfields:
    lines.append('  (none found; QR, if available, is probably generated from account/payment data)')
for f in qfields:
    label = ''
    if 'field_description' in IMF._fields:
        label = f.field_description or ''
    lines.append('  %s  (%s)  type=%s  state=%s' % (f.name, label, f.ttype or '', f.state or ''))
lines.append('')

# ---------------------------------------------------------------------------
# 4) barani_vat invoice views: bank/payment token windows
# ---------------------------------------------------------------------------
lines.append('==== 4) barani_vat VIEWS: BANK/PAYMENT TOKEN WINDOWS ====')
lines.append('Purpose: identify what the current RI/DPI red band actually reads today.')
vat_views = View.search([('key', 'ilike', 'barani_vat')], order='key,id')
if not vat_views:
    lines.append('  (no views with key ilike barani_vat found)')

TOKENS = ['acc_number', 'bank_id', 'bank_ids', 'partner_bank', 'iban', 'bic',
          'payment_reference', 'payment', 'wire', 'sepa', 'qr', 'bank']

for v in vat_views:
    inh = 'EMPTY/STANDALONE'
    if v.inherit_id:
        inh = '%s[%s]' % (v.inherit_id.id, v.inherit_id.key)
    arch = ''
    if 'arch_db' in View._fields:
        arch = v.arch_db or ''
    low = arch.lower()
    lines.append('  ---- VIEW id=%s key=%s type=%s mode=%s inherit_id=%s len=%s ----' % (
        v.id, v.key, v.type, v.mode, inh, len(arch)))
    any_hit = False
    for tok in TOKENS:
        pos = low.find(tok)
        guard = 0
        while pos != -1 and guard < MAX_TOKEN_WINDOWS_PER_TOKEN:
            s = pos - 140
            if s < 0:
                s = 0
            e = pos + 260
            lines.append('    [%s @ %s] ...%s...' % (tok, pos, arch[s:e]))
            any_hit = True
            pos = low.find(tok, pos + 1)
            guard = guard + 1
    if not any_hit:
        lines.append('    (no configured bank/payment tokens found in this view)')
    lines.append('')

# ---------------------------------------------------------------------------
# 5) Full arch dump, optional
# ---------------------------------------------------------------------------
lines.append('==== 5) barani_vat VIEWS: FULL arch_db ====')
if not DUMP_FULL_ARCH:
    lines.append('DUMP_FULL_ARCH=False, so full QWeb arch is suppressed. Set True if cloning the design.')
else:
    for v in vat_views:
        arch = ''
        if 'arch_db' in View._fields:
            arch = v.arch_db or ''
        lines.append('  ---- FULL ARCH BEGIN: id=%s key=%s ----' % (v.id, v.key))
        lines.append(arch)
        lines.append('  ---- FULL ARCH END: id=%s key=%s ----' % (v.id, v.key))
        lines.append('')

lines.append('END OF READ-ONLY PROBE')

# ---------------------------------------------------------------------------
# OUTPUT: zero-write paged UserError
# ---------------------------------------------------------------------------
full = '\n'.join(lines)
full_len = len(full)
pages_int = int(full_len / PAGE_SIZE)
if pages_int * PAGE_SIZE < full_len:
    pages_int = pages_int + 1
if pages_int < 1:
    pages_int = 1
start = (PAGE - 1) * PAGE_SIZE
if start < 0:
    start = 0
end = start + PAGE_SIZE
more = 'NO'
if start >= full_len:
    chunk = '(PAGE %s past end; full length %s chars.)' % (PAGE, full_len)
else:
    chunk = full[start:end]
    if end < full_len:
        more = 'YES'
header = []
header.append('============ PAGED OUTPUT ============')
header.append('FULL = %s chars | PAGE %s of %s | SHOWING %s-%s | MORE REMAINS: %s' % (full_len, PAGE, pages_int, start, end, more))
header.append('======================================')
header.append('')
footer = ''
if more == 'YES':
    footer = '\n--- Set PAGE=%s and rerun to continue. ---' % (PAGE + 1)
raise UserError(('\n'.join(header) + chunk + footer)[:60000])
