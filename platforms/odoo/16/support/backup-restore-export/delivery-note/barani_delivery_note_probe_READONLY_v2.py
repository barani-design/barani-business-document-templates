# BARANI Delivery Note 2026 readiness probe READ-ONLY v2
# Model: any. Action: Execute Python Code. Selected records ignored unless they are stock.picking samples.
PAGE = 1
PAGE_SIZE = 32000
View = env['ir.ui.view'].sudo(); Report = env['ir.actions.report'].sudo(); Model = env['ir.model'].sudo(); Param = env['ir.config_parameter'].sudo()
lines=[]
lines.append('READ-ONLY: BARANI Delivery Note 2026 readiness probe v2')
lines.append('READ-ONLY:YES — search/read only; no writes. PAGE=%s PAGE_SIZE=%s' % (PAGE, PAGE_SIZE))
lines.append('Plan: DN L1 QR-only DDS-free; flat native picking lines; no DDS Update Delivered Quantity replacement.')
lines.append('')
lines.append('1) STOCK/DELIVERY MODELS')
for model_name in ['stock.picking','stock.move','stock.move.line','product.product','sale.order']:
    m=Model.search([('model','=',model_name)], limit=1)
    lines.append('  %s: %s' % (model_name, 'FOUND id=%s' % m.id if m else 'MISSING'))
lines.append('')
lines.append('2) REQUIRED FIELD CHECK')
checks=[('stock.picking',['name','partner_id','scheduled_date','date_done','origin','picking_type_id','move_ids_without_package','state','company_id','sale_id','create_uid']),('stock.move',['product_id','description_picking','product_uom_qty','quantity_done','product_uom','move_line_ids','state']),('stock.move.line',['lot_id','product_id']),('product.product',['barcode','default_code','hs_code','country_of_origin'])]
missing_any=False
for model_name, fields in checks:
    lines.append('  %s:' % model_name)
    if model_name in env:
        flds=env[model_name]._fields
        for f in fields:
            ok=f in flds
            lines.append('    %-30s %s' % (f, 'YES' if ok else 'NO'))
            if not ok:
                missing_any=True
    else:
        missing_any=True
        lines.append('    MODEL MISSING')
lines.append('  REQUIRED FIELD RESULT: %s' % ('FAIL - adapt before install' if missing_any else 'PASS'))
lines.append('')
lines.append('3) OPTIONAL FUTURE FIELDS')
optional=[('stock.picking',['carrier_id']),('sale.order',['incoterm','incoterm_location'])]
for model_name, fields in optional:
    lines.append('  %s:' % model_name)
    if model_name in env:
        flds=env[model_name]._fields
        for f in fields:
            lines.append('    %-30s %s' % (f, 'YES' if f in flds else 'NO'))
    else:
        lines.append('    MODEL MISSING')
lines.append('')
lines.append('4) REPORT ACTIONS ON stock.picking')
for r in Report.search([('model','=','stock.picking')], order='id'):
    b=''
    try:
        b=r.binding_model_id.model or ''
    except Exception:
        b=''
    lines.append('  id=%s name=%r report_name=%s report_file=%s binding_model=%s paper=%s' % (r.id,r.name,r.report_name,r.report_file,b,r.paperformat_id.name if r.paperformat_id else ''))
lines.append('')
lines.append('5) BARANI DELIVERY ARTIFACTS')
for key in ['barani_delivery.report_delivery_note_2026','barani_delivery.external_layout_delivery_2026']:
    vs=View.search([('key','=',key)])
    id_text=''
    for v in vs:
        id_text = (id_text + ',' if id_text else '') + str(v.id)
    lines.append('  view key=%s count=%s ids=%s' % (key, len(vs), id_text))
rs=Report.search([('report_name','=','barani_delivery.report_delivery_note_2026'),('model','=','stock.picking')])
rid_text=''
for r in rs:
    rid_text = (rid_text + ',' if rid_text else '') + str(r.id)
lines.append('  technical reports count=%s ids=%s' % (len(rs), rid_text))
lines.append('')
lines.append('6) SELECTED PICKING SAMPLE SUMMARY')
try:
    if records and records._name == 'stock.picking':
        for p in records.sudo()[:10]:
            moves=p.move_ids_without_package
            with_barcode=0
            without_barcode=0
            for m in moves:
                if m.product_id and m.product_id.barcode:
                    with_barcode=with_barcode+1
                elif m.product_id:
                    without_barcode=without_barcode+1
            lines.append('  %s id=%s state=%s moves=%s products_with_barcode=%s products_without_barcode=%s origin=%s' % (p.name,p.id,p.state,len(moves),with_barcode,without_barcode,p.origin or ''))
    else:
        lines.append('  No stock.picking records selected; sample section skipped.')
except Exception as e:
    lines.append('  Sample inspection skipped/error: %s' % str(e)[:500])
lines.append('')
text='\n'.join(lines)
start=(PAGE-1)*PAGE_SIZE; end=start+PAGE_SIZE
slice_text=text[start:end]
more=end<len(text)
raise UserError('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s\n%s' % (PAGE,start,min(end,len(text)),len(text),'YES' if more else 'NO',slice_text))
