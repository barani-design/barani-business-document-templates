# ============================================================================
# ACTION NAME : BARANI COMMERCIAL PACKAGE EXPORT READ-ONLY v1.2 STANDARD
# MODEL       : Module recommended; selected records ignored.
# ACTION TO DO: Execute Python Code
# VISIBILITY  : Maintenance-only; run from Settings -> Technical -> Server Actions.
# PURPOSE     : Exports base-language XML for the four commercial views plus full
#               reconstruction metadata for both report actions and the paperformat.
# READ-ONLY   : no create/write/unlink/set_param/SQL/commit.
# PAGINATION  : set PAGE=2,3,... until MORE REMAINS:NO.
# ============================================================================
PAGE=1
PAGE_SIZE=16000
NL=chr(10)
ViewB=env['ir.ui.view'].sudo().with_context(lang=None)
Rep=env['ir.actions.report'].sudo().with_context(lang=None)
PF=env['report.paperformat'].sudo().with_context(lang=None)
IMD=env['ir.model.data'].sudo()
VIEW_KEYS=['barani_commercial.report_saleorder_document','barani_commercial.external_layout_standard_titled','barani_commercial.report_saleorder','barani_commercial.report_saleorder_proforma']
REPORT_NAMES=['barani_commercial.report_saleorder','barani_commercial.report_saleorder_proforma']
PF_NAME='BARANI Commercial A4 7mm'
lines=['BARANI COMMERCIAL PACKAGE EXPORT READ-ONLY v1.2 STANDARD','READ-ONLY:YES. Base-language views use lang=None.','']
for key in VIEW_KEYS:
    vs=ViewB.search([('key','=',key),('type','=','qweb')],limit=2)
    if len(vs)!=1:
        lines.append('VIEW key=%s RESOLVED=%s expected=1' % (key,len(vs)))
    else:
        v=vs[0]; arch=v.arch_db or ''
        lines.append('VIEW id=%s key=%s name=%s inherit_id=%s write_date=%s arch_len=%s' % (v.id,v.key,repr(v.name),bool(v.inherit_id),v.write_date,len(arch)))
        lines.append('<<<ARCH_BEGIN %s %s>>>' % (v.id,v.key)); lines.append(arch); lines.append('<<<ARCH_END %s>>>' % v.id)
for rn in REPORT_NAMES:
    rs=Rep.search([('report_name','=',rn)],limit=2)
    if len(rs)!=1:
        lines.append('REPORT report_name=%s RESOLVED=%s expected=1' % (rn,len(rs)))
    else:
        r=rs[0]; bm=r.binding_model_id; pf=r.paperformat_id; gr=[]
        for g in r.groups_id:
            gi=IMD.search([('model','=','res.groups'),('res_id','=',g.id)],limit=1)
            gr.append((gi.module+'.'+gi.name) if gi else ('id:%s' % g.id))
        gr.sort()
        lines.append('REPORT id=%s name=%s' % (r.id,repr(r.name)))
        lines.append('  model=%s report_type=%s report_name=%s report_file=%s' % (r.model,r.report_type,r.report_name,r.report_file or ''))
        lines.append('  binding_model_id=%s binding_model=%s binding_type=%s binding_view_types=%s' % ((bm.id if bm else 0),(bm.model if bm else ''),r.binding_type or '',r.binding_view_types or ''))
        lines.append('  paperformat_id=%s paperformat_name=%s' % ((pf.id if pf else 0),repr(pf.name if pf else '')))
        lines.append('  groups_xmlids=%s' % ', '.join(gr))
        lines.append('  print_report_name=%s' % repr(r.print_report_name or ''))
        lines.append('  attachment_use=%s attachment=%s multi=%s active=%s' % (bool(r.attachment_use),repr(r.attachment or ''),(bool(r.multi) if 'multi' in r._fields else '-'),(bool(r.active) if 'active' in r._fields else '-')))
pfs=PF.search([('name','=',PF_NAME)],limit=2)
if len(pfs)!=1:
    lines.append('PAPERFORMAT name=%s RESOLVED=%s expected=1' % (PF_NAME,len(pfs)))
else:
    p=pfs[0]
    lines.append('PAPERFORMAT id=%s name=%s' % (p.id,repr(p.name)))
    lines.append('  format=%s orientation=%s margins=%s/%s/%s/%s' % (p.format,p.orientation,p.margin_top,p.margin_bottom,p.margin_left,p.margin_right))
    lines.append('  header_line=%s header_spacing=%s dpi=%s disable_shrinking=%s' % (bool(p.header_line),p.header_spacing,p.dpi,bool(p.disable_shrinking)))
    lines.append('  page_width=%s page_height=%s default=%s' % (p.page_width,p.page_height,bool(p.default)))
lines.append('READ-ONLY EXPORT COMPLETE.')
text=NL.join(lines); total=len(text); start=(PAGE-1)*PAGE_SIZE; end=start+PAGE_SIZE; more='YES' if end<total else 'NO'
raise UserError(('PAGE %s | chars %s-%s of %s | MORE REMAINS: %s' % (PAGE,start,min(end,total),total,more))+NL+text[start:end])
