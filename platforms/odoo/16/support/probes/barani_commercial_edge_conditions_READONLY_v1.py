# ============================================================================
# ACTION NAME : BARANI COMMERCIAL EDGE-CONDITION PROBE READ-ONLY v1
# MODEL       : Module recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
# VISIBILITY  : Maintenance-only; run from Settings -> Technical -> Server Actions.
# PURPOSE     : Quantifies deferred commercial-template edge cases before any tune:
#               cancel states, blank tax labels, invoice-address differences,
#               currencies/rounding, naming patterns, incoterm location, long docs,
#               and payment-band flag consumption.
# READ-ONLY   : no create/write/unlink/set_param/SQL/commit.
# ============================================================================
PAGE=1
PAGE_SIZE=16000
NL=chr(10)
SO=env['sale.order'].sudo()
Tax=env['account.tax'].sudo().with_context(active_test=False)
Cur=env['res.currency'].sudo()
View=env['ir.ui.view'].sudo().with_context(lang=None)
Rep=env['ir.actions.report'].sudo().with_context(lang=None)
lines=['BARANI COMMERCIAL EDGE-CONDITION PROBE READ-ONLY v1','READ-ONLY:YES. No writes.','']
# cancel state
cancel_count=SO.search_count([('state','=','cancel')]); lines.append('CANCELLED ORDERS count=%s' % cancel_count)
for o in SO.search([('state','=','cancel')],order='id desc',limit=10): lines.append('  id=%s name=%s partner=%s date=%s' % (o.id,o.name,o.partner_id.display_name,o.date_order))
# tax descriptions
blank=Tax.search([('type_tax_use','in',['sale','all']),('|'),('description','=',False),('description','=','')],order='active desc,id')
lines.append('SALE/ALL TAXES WITH BLANK DESCRIPTION count=%s' % len(blank))
for t in blank[:30]: lines.append('  id=%s active=%s name=%s amount=%s use=%s' % (t.id,t.active,t.name,t.amount,t.type_tax_use))
# address semantics in recent sample
sample=SO.search([],order='id desc',limit=2000); diff=0; examples=[]
for o in sample:
    if o.partner_invoice_id and o.partner_invoice_id!=o.partner_id:
        diff+=1
        if len(examples)<15: examples.append(o)
lines.append('RECENT ADDRESS SAMPLE orders=%s partner_invoice_id!=partner_id=%s' % (len(sample),diff))
for o in examples: lines.append('  %s customer=%s invoice=%s shipping=%s' % (o.name,o.partner_id.display_name,o.partner_invoice_id.display_name,o.partner_shipping_id.display_name))
# currencies via read_group
lines.append('CURRENCIES USED BY SALE ORDERS')
for g in SO.read_group([],['currency_id'],['currency_id'],lazy=False):
    if g.get('currency_id'):
        c=Cur.browse(g['currency_id'][0]); lines.append('  %s count=%s decimal_places=%s rounding=%s symbol=%s position=%s' % (c.name,g.get('__count',0),c.decimal_places,c.rounding,c.symbol,c.position))
# names + incoterm locations + long docs
cats={'Q/':0,'Q':0,'S':0,'SO/':0,'PF/':0,'OTHER':0}; long_notes=0; many_lines=0; inc_loc=0; ns=SO.search([],order='id desc',limit=2000)
for o in ns:
    n=o.name or ''
    if n[:3]=='SO/': cats['SO/']+=1
    elif n[:3]=='PF/': cats['PF/']+=1
    elif n[:2]=='Q/': cats['Q/']+=1
    elif n[:1]=='Q': cats['Q']+=1
    elif n[:1]=='S': cats['S']+=1
    else: cats['OTHER']+=1
    if o.incoterm_location: inc_loc+=1
    if len(o.note or '')>1000: long_notes+=1
    if len(o.order_line)>30: many_lines+=1
lines.append('RECENT NAME PATTERNS sample=%s values=%s' % (len(ns),cats))
lines.append('RECENT INCOTERM LOCATION populated=%s; notes>1000 chars=%s; orders>30 lines=%s' % (inc_loc,long_notes,many_lines))
# template markers
vs=View.search([('key','=','barani_commercial.report_saleorder_document'),('type','=','qweb')],limit=2)
if len(vs)==1:
    a=vs[0].arch_db or ''
    lines.append('TEMPLATE payment flag set/consumed: set_marker=%s consumed_in_band=%s' % (('barani_show_payment_band' in a),('t-if="barani_show_payment_band and' in a)))
    lines.append('TEMPLATE cancel treated as quotation=%s' % ("('draft', 'sent', 'cancel')" in a))
    lines.append('TEMPLATE safe tax fallback=%s' % ("filtered('description')" in a))
    lines.append('TEMPLATE currency-aware unit price=%s rounding_is_zero=%s' % ('display_currency' in a[a.find('td_priceunit'):a.find('td_discount')], 'currency_id.is_zero' in a))
rs=Rep.search([('report_name','=','barani_commercial.report_saleorder')],limit=2)
if len(rs)==1: lines.append('Q/SO print_report_name=%s' % repr(rs[0].print_report_name or ''))
lines.append('READ-ONLY PROBE COMPLETE.')
text=NL.join(lines); total=len(text); start=(PAGE-1)*PAGE_SIZE; end=start+PAGE_SIZE; more='YES' if end<total else 'NO'
raise UserError(('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s' % (PAGE,start,min(end,total),total,more))+NL+text[start:end])
