# BARANI Delivery Note 2026 create current restore point SAFE
APPLY = False
CONFIRM = ''
BACKUP_TAG = 'delivery_note_2026_dn_l1_qr_only_dds_free'
BODY_KEY='barani_delivery.report_delivery_note_2026'
LAYOUT_KEY='barani_delivery.external_layout_delivery_2026'
IDS_KEY='barani.delivery_note_2026.ids'
PREFIX='barani.delivery_note_2026.restore_point.' + BACKUP_TAG
CURRENT_KEY='barani.delivery_note_2026.restore_point.current'
View=env['ir.ui.view'].sudo(); Report=env['ir.actions.report'].sudo(); Paper=env['report.paperformat'].sudo(); Param=env['ir.config_parameter'].sudo()
lines=[]
lines.append('BARANI Delivery Note 2026 — CREATE CURRENT RESTORE POINT SAFE')
lines.append('APPLY=%s CONFIRM=%s BACKUP_TAG=%s' % (APPLY,CONFIRM,BACKUP_TAG))
lines.append('WRITES: ir.config_parameter only.')
lines.append('')
body=View.search([('key','=',BODY_KEY)])
layout=View.search([('key','=',LAYOUT_KEY)])
report=Report.search([('report_name','=',BODY_KEY),('model','=','stock.picking')])
if len(body)!=1 or len(layout)!=1 or len(report)!=1:
    lines.append('ERROR: expected exactly one body/layout/report; found body=%s layout=%s report=%s' % (len(body),len(layout),len(report)))
    raise UserError('\n'.join(lines))
paper=report.paperformat_id
lines.append('RESOLVED')
lines.append('  body id=%s key=%s len=%s' % (body.id, body.key, len(body.arch_db or '')))
lines.append('  layout id=%s key=%s len=%s' % (layout.id, layout.key, len(layout.arch_db or '')))
lines.append('  report id=%s name=%r' % (report.id, report.name))
lines.append('  paper id=%s name=%r' % (paper.id if paper else 0, paper.name if paper else ''))
markers=[('product QR','barcode_type=%s' in (body.arch_db or '') and 'move.product_id.barcode' in (body.arch_db or '')),('delivery table','barani_delivery_line_table' in (body.arch_db or '')),('right header title','barani_delivery_doc_title_right' in (layout.arch_db or '')),('no EORI from VAT','EORI:' not in (layout.arch_db or '')),('no DDS/brn strings','dds_' not in (body.arch_db or '') and 'brn_' not in (body.arch_db or '') and 'dds_' not in (layout.arch_db or '') and 'brn_' not in (layout.arch_db or ''))]
err=False
for name, ok in markers:
    lines.append('  marker %-20s %s' % (name, 'PASS' if ok else 'FAIL'))
    if not ok: err=True
if err:
    lines.append('ERROR: marker check failed; refusing backup.')
    raise UserError('\n'.join(lines))
exists=bool(Param.get_param(PREFIX + '.created', ''))
lines.append('')
lines.append('TARGET prefix=%s exists_now=%s' % (PREFIX, exists))
if exists:
    lines.append('ERROR: restore point exists; refusing to overwrite.')
    raise UserError('\n'.join(lines))
lines.append('PLAN: store body/layout/report/paper metadata in ir.config_parameter only.')
if not APPLY:
    lines.append('DRY RUN COMPLETE: no writes performed.')
    lines.append("Set APPLY=True and CONFIRM='CREATE_DELIVERY_RESTORE_POINT' to create.")
    raise UserError('\n'.join(lines))
if CONFIRM != 'CREATE_DELIVERY_RESTORE_POINT':
    lines.append('ERROR: wrong CONFIRM.')
    raise UserError('\n'.join(lines))
Param.set_param(PREFIX+'.created','1')
Param.set_param(PREFIX+'.ids','%s,%s,%s,%s' % (body.id, report.id, paper.id if paper else 0, layout.id))
Param.set_param(PREFIX+'.body_arch', body.arch_db or '')
Param.set_param(PREFIX+'.layout_arch', layout.arch_db or '')
Param.set_param(PREFIX+'.report.name', report.name or '')
Param.set_param(PREFIX+'.report.print_report_name', report.print_report_name or '')
if paper:
    Param.set_param(PREFIX+'.paper.margin_top', str(paper.margin_top))
    Param.set_param(PREFIX+'.paper.margin_bottom', str(paper.margin_bottom))
    Param.set_param(PREFIX+'.paper.margin_left', str(paper.margin_left))
    Param.set_param(PREFIX+'.paper.margin_right', str(paper.margin_right))
    Param.set_param(PREFIX+'.paper.header_spacing', str(paper.header_spacing))
    Param.set_param(PREFIX+'.paper.dpi', str(paper.dpi))
Param.set_param(CURRENT_KEY, BACKUP_TAG)
try:
    env.invalidate_all()
except Exception:
    env.cache.invalidate()
lines.append('PASS: created delivery restore point %s.' % BACKUP_TAG)
raise UserError('\n'.join(lines)[:90000])
