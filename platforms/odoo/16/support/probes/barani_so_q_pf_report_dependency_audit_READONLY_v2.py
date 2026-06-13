# ============================================================================
# ACTION NAME : READ-ONLY: BARANI SO/Q/PF/PO report dependency audit v2
# MODEL       : Module (ir.module.module) is convenient; selected records ignored.
# ACTION TO DO: Execute Python Code
# PURPOSE     : Map the CURRENT Odoo print/report/QWeb dependency graph for:
#                 - Quotations / Sales Orders / Pro-forma documents (sale.order)
#                 - RFQ / Purchase Orders (purchase.order)
#                 - Existing invoice/DDS/BARANI reference actions (account.move)
#
#               Use this BEFORE building an isolated BARANI commercial document
#               report family. The goal is to see whether the live SO/Q/PF/PO
#               reports are patched by DDS/DodoSys/Studio/Odoo inherited views,
#               shared layouts, shared paperformats, report actions, server
#               actions, or automated actions.
#
# READ-ONLY   : No create / write / unlink / set_param. It reads metadata and
#               QWeb arch text only, then raises UserError as the output channel.
#
# SAFE_EVAL   : no import / def / lambda / comprehension / with / getattr /
#               hasattr / setattr / eval / exec / open / dir / isinstance.
# ============================================================================

PAGE = 1
PAGE_SIZE = 32000
MAX_VIEW_DEPTH = 6
MAX_REPORTS = 220
MAX_CHILDREN_PER_VIEW = 120
GLOBAL_QWEB_SCAN = True
GLOBAL_VIEW_LIMIT_PER_TERM = 80
INCLUDE_ACCOUNT_MOVE_REFERENCE = True
DUMP_RISK_SNIPPETS = True
RISK_SNIPPET_CHARS = 240

TARGET_MODELS = ['sale.order', 'purchase.order']
REFERENCE_MODELS = ['account.move']
ACTION_IDS_TO_ALWAYS_INCLUDE = [234, 236, 842, 900, 918]

REPORT_KEYWORDS = [
    'quotation', 'quote', 'proforma', 'pro-forma', 'pro forma',
    'sales order', 'sale order', 'rfq', 'request for quotation',
    'purchase order', 'purchase quotation', 'invoice', 'credit note',
    'barani', 'dds', 'dodo', 'dodosys', 'studio'
]

KNOWN_REPORT_NAMES = [
    'sale.report_saleorder',
    'sale.report_saleorder_document',
    'sale.report_saleorder_pro_forma',
    'sale.report_saleorder_proforma',
    'purchase.report_purchasequotation',
    'purchase.report_purchasequotation_document',
    'purchase.report_purchaseorder',
    'purchase.report_purchaseorder_document',
    'account.report_invoice',
    'account.report_invoice_document',
    'barani_vat.report_invoice_document_vat',
    'barani_vat.external_layout_standard_titled',
    'web.html_container',
    'web.external_layout',
    'web.external_layout_standard',
    'web.external_layout_bold',
    'web.external_layout_boxed'
]

QWEB_KEYWORDS = [
    'sale.report_saleorder', 'saleorder', 'sale order', 'quotation', 'quote',
    'proforma', 'pro-forma', 'pro_forma', 'pro forma',
    'purchase.report', 'purchaseorder', 'purchase_order', 'purchase order', 'rfq',
    'account.report_invoice', 'invoice_document',
    'web.external_layout', 'barani', 'dds', 'dodo', 'dodosys',
    'Advanced Invoice:', 'advance invoice:', 'Down Payment'
]

RISK_TERMS = [
    'dds', 'dds_', 'dodo', 'dodosys', 'advanced invoice:', 'advance invoice:',
    'account.report_invoice_document', 'sale.report_saleorder_document',
    'purchase.report_purchaseorder_document', 'web.external_layout'
]

OWNER_TERMS = ['barani', 'dds', 'dodo', 'dodosys', 'studio', 'sale', 'purchase', 'account', 'web']

if PAGE < 1:
    raise UserError('ERROR: PAGE must be >= 1')
if PAGE_SIZE < 5000:
    raise UserError('ERROR: PAGE_SIZE must be >= 5000')
if MAX_VIEW_DEPTH < 1:
    raise UserError('ERROR: MAX_VIEW_DEPTH must be >= 1')

View = env['ir.ui.view'].sudo()
Report = env['ir.actions.report'].sudo()
Imd = env['ir.model.data'].sudo()
Paper = env['report.paperformat'].sudo()
Module = env['ir.module.module'].sudo()
ServerAction = env['ir.actions.server'].sudo()

lines = []
lines.append('BARANI SO/Q/PF/PO REPORT DEPENDENCY AUDIT v2 READ-ONLY')
lines.append('READ-ONLY:YES - performs no create/write/unlink/set_param')
lines.append('PAGE=%s PAGE_SIZE=%s MAX_VIEW_DEPTH=%s GLOBAL_QWEB_SCAN=%s' % (PAGE, PAGE_SIZE, MAX_VIEW_DEPTH, GLOBAL_QWEB_SCAN))
lines.append('Primary target models: %s' % ', '.join(TARGET_MODELS))
if INCLUDE_ACCOUNT_MOVE_REFERENCE:
    lines.append('Reference model included: account.move, plus known report ids 234/236/842/900/918')
lines.append('')

# ---------------------------------------------------------------------------
# 1) Installed suspect/custom modules.
# ---------------------------------------------------------------------------
lines.append('============================================================')
lines.append('1. INSTALLED / AVAILABLE MODULES MATCHING DDS / DODO / BARANI / STUDIO')
lines.append('============================================================')
module_ids = []
for mod_kw in ['dds', 'dodo', 'dodosys', 'barani', 'studio']:
    mods = Module.search(['|', '|', ('name', 'ilike', mod_kw), ('shortdesc', 'ilike', mod_kw), ('description', 'ilike', mod_kw)], order='name')
    for mod in mods:
        if mod.id not in module_ids:
            module_ids.append(mod.id)
            desc = ''
            if 'shortdesc' in Module._fields:
                desc = mod.shortdesc or ''
            lines.append('module id=%s name=%s state=%s shortdesc=%r' % (mod.id, mod.name or '', mod.state or '', desc))
if not module_ids:
    lines.append('(none found by name/shortdesc/description search)')
lines.append('')

# ---------------------------------------------------------------------------
# 2) Discover report actions.
# ---------------------------------------------------------------------------
report_ids = []

# Known historical invoice/DDS/BARANI references.
if INCLUDE_ACCOUNT_MOVE_REFERENCE:
    for rid in ACTION_IDS_TO_ALWAYS_INCLUDE:
        rr = Report.browse(rid)
        if rr and rr.exists():
            if rr.id not in report_ids:
                report_ids.append(rr.id)

# Reports by target model and binding model.
model_scan = []
for tm in TARGET_MODELS:
    if tm not in model_scan:
        model_scan.append(tm)
if INCLUDE_ACCOUNT_MOVE_REFERENCE:
    for rm in REFERENCE_MODELS:
        if rm not in model_scan:
            model_scan.append(rm)

for model_name in model_scan:
    rs = Report.search([('model', '=', model_name)], order='id')
    for rr in rs:
        if rr.id not in report_ids:
            report_ids.append(rr.id)
    if 'binding_model_id' in Report._fields:
        rsb = Report.search([('binding_model_id.model', '=', model_name)], order='id')
        for rr in rsb:
            if rr.id not in report_ids:
                report_ids.append(rr.id)

# Reports by keyword. This catches unbound/custom actions.
for kw in REPORT_KEYWORDS:
    if len(report_ids) >= MAX_REPORTS:
        continue
    if 'report_file' in Report._fields:
        rs = Report.search(['|', '|', ('name', 'ilike', kw), ('report_name', 'ilike', kw), ('report_file', 'ilike', kw)], order='id', limit=100)
    else:
        rs = Report.search(['|', ('name', 'ilike', kw), ('report_name', 'ilike', kw)], order='id', limit=100)
    for rr in rs:
        if len(report_ids) >= MAX_REPORTS:
            continue
        if rr.id not in report_ids:
            report_ids.append(rr.id)

reports = Report.browse(report_ids)
lines.append('============================================================')
lines.append('2. REPORT ACTIONS SELECTED FOR PRINT-MENU / TEMPLATE MAP')
lines.append('============================================================')
lines.append('count=%s' % len(reports))
lines.append('')

root_view_ids = []
all_tree_view_ids = []
seed_keys = []
for kn in KNOWN_REPORT_NAMES:
    if kn not in seed_keys:
        seed_keys.append(kn)

for rep in reports:
    if not rep.exists():
        continue

    rep_xmls = []
    imds = Imd.search([('model', '=', 'ir.actions.report'), ('res_id', '=', rep.id)], order='module,name', limit=20)
    for imd in imds:
        rep_xmls.append('%s.%s' % (imd.module or '', imd.name or ''))
    rep_xml_line = '(no xmlid)'
    if rep_xmls:
        rep_xml_line = ', '.join(rep_xmls)

    binding_model = ''
    binding_type = ''
    binding_view_types = ''
    if 'binding_model_id' in Report._fields and rep.binding_model_id:
        binding_model = rep.binding_model_id.model or ''
    if 'binding_type' in Report._fields:
        binding_type = rep.binding_type or ''
    if 'binding_view_types' in Report._fields:
        binding_view_types = rep.binding_view_types or ''

    report_file = ''
    if 'report_file' in Report._fields:
        report_file = rep.report_file or ''
    print_name = ''
    if 'print_report_name' in Report._fields:
        print_name = rep.print_report_name or ''
    attachment = ''
    attachment_use = ''
    if 'attachment' in Report._fields:
        attachment = rep.attachment or ''
    if 'attachment_use' in Report._fields:
        attachment_use = rep.attachment_use

    # Paperformat detail and sharing.
    paper_line = '(none)'
    if 'paperformat_id' in Report._fields and rep.paperformat_id:
        p = rep.paperformat_id
        paper_xmls = []
        p_imds = Imd.search([('model', '=', 'report.paperformat'), ('res_id', '=', p.id)], order='module,name', limit=10)
        for pimd in p_imds:
            paper_xmls.append('%s.%s' % (pimd.module or '', pimd.name or ''))
        paper_xml_line = '(no xmlid)'
        if paper_xmls:
            paper_xml_line = ', '.join(paper_xmls)
        paper_user_count = 0
        same_paper = Report.search([('paperformat_id', '=', p.id)], order='id')
        for sx in same_paper:
            paper_user_count = paper_user_count + 1
        paper_line = 'id=%s xmlid=%s name=%r users=%s fmt=%s orient=%s margins T/B/L/R=%s/%s/%s/%s header_spacing=%s dpi=%s' % (
            p.id, paper_xml_line, p.name or '', paper_user_count,
            p.format or '', p.orientation or '', p.margin_top, p.margin_bottom,
            p.margin_left, p.margin_right, p.header_spacing, p.dpi
        )

    group_names = []
    if 'groups_id' in Report._fields:
        for group in rep.groups_id:
            gname = group.name or str(group.id)
            if 'full_name' in group._fields and group.full_name:
                gname = group.full_name
            group_names.append('%s:%s' % (group.id, gname))
    group_line = '(none)'
    if group_names:
        group_line = ', '.join(group_names)

    family_bits = []
    low_report = ((rep.name or '') + ' ' + (rep.model or '') + ' ' + binding_model + ' ' + (rep.report_name or '') + ' ' + report_file + ' ' + print_name + ' ' + rep_xml_line).lower()
    if rep.model == 'sale.order' or binding_model == 'sale.order':
        family_bits.append('SALE.ORDER_PRINT')
    if rep.model == 'purchase.order' or binding_model == 'purchase.order':
        family_bits.append('PURCHASE.ORDER_PRINT')
    if rep.model == 'account.move' or binding_model == 'account.move':
        family_bits.append('ACCOUNT.MOVE_REFERENCE')
    if 'proforma' in low_report or 'pro-forma' in low_report or 'pro forma' in low_report:
        family_bits.append('PROFORMA/PF')
    if 'quotation' in low_report or 'quote' in low_report:
        family_bits.append('QUOTATION/Q')
    if 'purchase' in low_report or 'rfq' in low_report:
        family_bits.append('PURCHASE/RFQ/PO')
    if 'barani' in low_report:
        family_bits.append('BARANI')
    if 'dds' in low_report or 'dodo' in low_report or 'dodosys' in low_report:
        family_bits.append('DDS/DODO')

    risk_bits = []
    for risk in RISK_TERMS:
        if risk in low_report:
            risk_bits.append(risk)

    if rep.report_name and rep.report_name not in seed_keys:
        seed_keys.append(rep.report_name)
    if report_file and report_file not in seed_keys and '.' in report_file:
        seed_keys.append(report_file)

    lines.append('------------------------------------------------------------')
    lines.append('REPORT ACTION id=%s xmlid=%s' % (rep.id, rep_xml_line))
    lines.append('  family=%s' % (', '.join(family_bits) or '(uncategorized)'))
    lines.append('  name=%r' % (rep.name or ''))
    lines.append('  model=%s binding_model=%s binding_type=%s binding_view_types=%s' % (rep.model or '', binding_model, binding_type, binding_view_types))
    lines.append('  report_type=%s report_name=%s report_file=%s' % (rep.report_type or '', rep.report_name or '', report_file))
    lines.append('  print_report_name=%r' % print_name)
    if attachment:
        lines.append('  attachment=%r attachment_use=%s' % (attachment, attachment_use))
    lines.append('  groups=%s' % group_line)
    lines.append('  paperformat=%s' % paper_line)
    lines.append('  action_risk_terms=%s' % (', '.join(risk_bits) or '(none)'))

    root_views = View.browse([])
    if rep.report_name:
        root_views = View.search([('type', '=', 'qweb'), ('key', '=', rep.report_name)], order='priority,id')
        if not root_views:
            root_views = View.search([('type', '=', 'qweb'), ('name', '=', rep.report_name)], order='priority,id')
    if not root_views:
        lines.append('  ROOT QWEB: NOT FOUND by key/name=%s' % (rep.report_name or ''))
        lines.append('')
        continue

    rv_ids_text = ''
    for rv in root_views:
        if rv_ids_text:
            rv_ids_text = rv_ids_text + ', '
        rv_ids_text = rv_ids_text + str(rv.id)
        if rv.id not in root_view_ids:
            root_view_ids.append(rv.id)
    lines.append('  ROOT QWEB VIEW IDS=%s' % rv_ids_text)
    lines.append('')

# ---------------------------------------------------------------------------
# 3) Walk QWeb dependency graph from seed keys and report root views.
# ---------------------------------------------------------------------------
lines.append('============================================================')
lines.append('3. QWEB DEPENDENCY WALK: ROOT VIEW -> T-CALLS -> LAYOUTS + INHERITED CHILDREN')
lines.append('============================================================')
lines.append('This section is the core contamination check. Any active inherited child under the live sale/purchase templates is part of the current render path.')
lines.append('')

queue_ids = []
queue_levels = []
queue_via = []
seen_view_ids = []

# Seed by known keys and report names.
for sk in seed_keys:
    tvs = View.search([('type', '=', 'qweb'), ('key', '=', sk)], order='priority,id')
    if not tvs:
        tvs = View.search([('type', '=', 'qweb'), ('name', '=', sk)], order='priority,id')
    for tv in tvs:
        if tv.id not in queue_ids:
            queue_ids.append(tv.id)
            queue_levels.append(0)
            queue_via.append('seed_key:%s' % sk)

# Explicit root views from report action resolution.
for rvid in root_view_ids:
    if rvid not in queue_ids:
        queue_ids.append(rvid)
        queue_levels.append(0)
        queue_via.append('report_root_view')

qi = 0
while qi < len(queue_ids):
    vid = queue_ids[qi]
    level = queue_levels[qi]
    via = queue_via[qi]
    qi = qi + 1

    if vid in seen_view_ids:
        continue
    seen_view_ids.append(vid)
    if vid not in all_tree_view_ids:
        all_tree_view_ids.append(vid)

    vw = View.browse(vid)
    if not vw.exists():
        continue

    indent = ''
    ii = 0
    while ii < level:
        indent = indent + '  '
        ii = ii + 1

    v_xmls = []
    v_imds = Imd.search([('model', '=', 'ir.ui.view'), ('res_id', '=', vw.id)], order='module,name', limit=20)
    for vimd in v_imds:
        v_xmls.append('%s.%s' % (vimd.module or '', vimd.name or ''))
    v_xml_line = '(no xmlid)'
    if v_xmls:
        v_xml_line = ', '.join(v_xmls)

    parent_line = 'inherit_id=EMPTY/STANDALONE'
    if vw.inherit_id:
        parent_line = 'inherit_id=%s[%s]' % (vw.inherit_id.id, vw.inherit_id.key or vw.inherit_id.name or '')

    arch = vw.arch_db or ''
    combined_arch = ''
    if 'arch' in View._fields:
        try:
            combined_arch = vw.arch or ''
        except Exception:
            combined_arch = ''
    scan_text = ((vw.key or '') + ' ' + (vw.name or '') + ' ' + v_xml_line + ' ' + arch + ' ' + combined_arch).lower()

    flags = []
    if not vw.active:
        flags.append('INACTIVE')
    if vw.inherit_id:
        flags.append('INHERITED/EXTENSION_VIEW')
    else:
        flags.append('STANDALONE_VIEW')
    for rt in RISK_TERMS:
        if rt in scan_text:
            flags.append('HAS_%s' % rt.replace(' ', '_').replace(':', '').replace('.', '_').upper())
    owner_bits = []
    owner_scan = ((vw.key or '') + ' ' + (vw.name or '') + ' ' + v_xml_line).lower()
    for ot in OWNER_TERMS:
        if ot in owner_scan:
            owner_bits.append(ot)

    flags_line = '(none)'
    if flags:
        flags_line = ', '.join(flags)
    owner_line = '(none)'
    if owner_bits:
        owner_line = ', '.join(owner_bits)

    lines.append('%sVIEW id=%s xmlid=%s key=%s name=%r type=%s mode=%s active=%s priority=%s write_date=%s via=%s %s' % (
        indent, vw.id, v_xml_line, vw.key or '', vw.name or '', vw.type or '', vw.mode or '', vw.active, vw.priority, vw.write_date, via, parent_line
    ))
    lines.append('%s  owner_terms=%s flags=%s arch_db_len=%s combined_arch_len=%s' % (indent, owner_line, flags_line, len(arch), len(combined_arch)))

    if DUMP_RISK_SNIPPETS:
        for rt in RISK_TERMS:
            idx = scan_text.find(rt)
            if idx >= 0:
                safe_text = (arch or combined_arch).replace('\n', ' ')
                low_safe = safe_text.lower()
                idx2 = low_safe.find(rt)
                if idx2 >= 0:
                    st = idx2 - RISK_SNIPPET_CHARS
                    if st < 0:
                        st = 0
                    en = idx2 + RISK_SNIPPET_CHARS
                    if en > len(safe_text):
                        en = len(safe_text)
                    lines.append('%s  risk_snippet[%s]=%r' % (indent, rt, safe_text[st:en]))

    # Extract static t-call targets from own arch and combined arch.
    tcalls = []
    for src in [arch, combined_arch]:
        if src:
            pos = 0
            while pos < len(src):
                idx1 = src.find('t-call="', pos)
                idx2 = src.find("t-call='", pos)
                idx = -1
                quote = '"'
                if idx1 >= 0 and idx2 >= 0:
                    if idx1 <= idx2:
                        idx = idx1
                        quote = '"'
                    else:
                        idx = idx2
                        quote = "'"
                elif idx1 >= 0:
                    idx = idx1
                    quote = '"'
                elif idx2 >= 0:
                    idx = idx2
                    quote = "'"
                else:
                    idx = -1
                if idx < 0:
                    pos = len(src)
                else:
                    start = idx + 8
                    end = src.find(quote, start)
                    if end < 0:
                        pos = len(src)
                    else:
                        target = src[start:end]
                        if target and target not in tcalls:
                            tcalls.append(target)
                        pos = end + 1
    if tcalls:
        lines.append('%s  t-call targets=%s' % (indent, ', '.join(tcalls)))
    else:
        lines.append('%s  t-call targets=(none)' % indent)

    # Queue parent, inherited children, and t-call target views.
    if level < MAX_VIEW_DEPTH:
        if vw.inherit_id and vw.inherit_id.id not in seen_view_ids and vw.inherit_id.id not in queue_ids:
            queue_ids.append(vw.inherit_id.id)
            queue_levels.append(level + 1)
            queue_via.append('inherit_parent_of:%s' % vw.id)

        children = View.search([('inherit_id', '=', vw.id)], order='priority,id', limit=MAX_CHILDREN_PER_VIEW)
        child_lines = []
        child_count = 0
        for child in children:
            child_count = child_count + 1
            c_xmls = []
            c_imds = Imd.search([('model', '=', 'ir.ui.view'), ('res_id', '=', child.id)], order='module,name', limit=8)
            for cimd in c_imds:
                c_xmls.append('%s.%s' % (cimd.module or '', cimd.name or ''))
            c_xml_line = '(no xmlid)'
            if c_xmls:
                c_xml_line = ', '.join(c_xmls)
            c_arch = child.arch_db or ''
            c_low = ((child.key or '') + ' ' + (child.name or '') + ' ' + c_xml_line + ' ' + c_arch).lower()
            c_flags = []
            for rt in RISK_TERMS:
                if rt in c_low:
                    c_flags.append(rt)
            c_owner = []
            c_owner_low = ((child.key or '') + ' ' + (child.name or '') + ' ' + c_xml_line).lower()
            for ot in OWNER_TERMS:
                if ot in c_owner_low:
                    c_owner.append(ot)
            c_flags_line = '(none)'
            if c_flags:
                c_flags_line = ', '.join(c_flags)
            c_owner_line = '(none)'
            if c_owner:
                c_owner_line = ', '.join(c_owner)
            child_lines.append('%s mode=%s active=%s prio=%s owner=%s risk=%s key=%s name=%r xmlid=%s' % (child.id, child.mode or '', child.active, child.priority, c_owner_line, c_flags_line, child.key or '', child.name or '', c_xml_line))
            if child.id not in seen_view_ids and child.id not in queue_ids:
                queue_ids.append(child.id)
                queue_levels.append(level + 1)
                queue_via.append('inherits_child_of:%s' % vw.id)
        if child_lines:
            lines.append('%s  direct inherited children=%s' % (indent, len(child_lines)))
            for cl in child_lines:
                lines.append('%s    child %s' % (indent, cl))
        else:
            lines.append('%s  direct inherited children=0' % indent)

        for target in tcalls:
            tvs = View.search([('type', '=', 'qweb'), ('key', '=', target)], order='priority,id')
            if not tvs:
                tvs = View.search([('type', '=', 'qweb'), ('name', '=', target)], order='priority,id')
            if not tvs:
                lines.append('%s  t-call target unresolved: %s' % (indent, target))
            for tv in tvs:
                if tv.id not in seen_view_ids and tv.id not in queue_ids:
                    queue_ids.append(tv.id)
                    queue_levels.append(level + 1)
                    queue_via.append('t-call:%s' % target)

    lines.append('')

# ---------------------------------------------------------------------------
# 4) Global scan for orphan/indirect QWeb references.
# ---------------------------------------------------------------------------
if GLOBAL_QWEB_SCAN:
    lines.append('============================================================')
    lines.append('4. GLOBAL QWEB SCAN FOR SO/Q/PF/PO/DDS TERMS')
    lines.append('============================================================')
    global_view_ids = []
    for qkw in QWEB_KEYWORDS:
        views = View.search(['|', '|', ('key', 'ilike', qkw), ('name', 'ilike', qkw), ('arch_db', 'ilike', qkw)], order='id', limit=GLOBAL_VIEW_LIMIT_PER_TERM)
        for vw in views:
            if vw.id not in global_view_ids:
                global_view_ids.append(vw.id)
                v_xmls = []
                v_imds = Imd.search([('model', '=', 'ir.ui.view'), ('res_id', '=', vw.id)], order='module,name', limit=10)
                for vimd in v_imds:
                    v_xmls.append('%s.%s' % (vimd.module or '', vimd.name or ''))
                v_xml_line = '(no xmlid)'
                if v_xmls:
                    v_xml_line = ', '.join(v_xmls)
                parent_txt = 'EMPTY/STANDALONE'
                if vw.inherit_id:
                    parent_txt = '%s[%s]' % (vw.inherit_id.id, vw.inherit_id.key or vw.inherit_id.name or '')
                arch = vw.arch_db or ''
                low = ((vw.key or '') + ' ' + (vw.name or '') + ' ' + v_xml_line + ' ' + arch).lower()
                flags = []
                for rt in RISK_TERMS:
                    if rt in low:
                        flags.append(rt)
                owner_bits = []
                owner_low = ((vw.key or '') + ' ' + (vw.name or '') + ' ' + v_xml_line).lower()
                for ot in OWNER_TERMS:
                    if ot in owner_low:
                        owner_bits.append(ot)
                flag_txt = '(none)'
                if flags:
                    flag_txt = ', '.join(flags)
                owner_txt = '(none)'
                if owner_bits:
                    owner_txt = ', '.join(owner_bits)
                lines.append('match_kw=%r view id=%s xmlid=%s owner=%s key=%s name=%r active=%s mode=%s inherit_id=%s risk=%s write_date=%s' % (
                    qkw, vw.id, v_xml_line, owner_txt, vw.key or '', vw.name or '', vw.active, vw.mode or '', parent_txt, flag_txt, vw.write_date
                ))
    if not global_view_ids:
        lines.append('(no global QWeb matches)')
    lines.append('')

# ---------------------------------------------------------------------------
# 5) Server action and automation scan.
# ---------------------------------------------------------------------------
lines.append('============================================================')
lines.append('5. SERVER ACTIONS / AUTOMATED ACTIONS MENTIONING REPORT ROUTING TERMS')
lines.append('============================================================')
sa_terms = ['sale.report', 'saleorder', 'proforma', 'pro-forma', 'pro forma', 'quotation', 'quote', 'purchase.report', 'purchaseorder', 'purchase order', 'ir.actions.report', 'report_name', 'report_action', 'qweb', 'dds', 'dodo', 'dodosys', 'barani']
sa_ids = []
for term in sa_terms:
    sas = ServerAction.search(['|', ('name', 'ilike', term), ('code', 'ilike', term)], order='name,id', limit=80)
    for sa in sas:
        if sa.id not in sa_ids:
            sa_ids.append(sa.id)
if sa_ids:
    for said in sa_ids:
        sa = ServerAction.browse(said)
        if not sa.exists():
            continue
        model_txt = ''
        if 'model_id' in ServerAction._fields and sa.model_id:
            model_txt = sa.model_id.model or ''
        code_txt = ''
        if 'code' in ServerAction._fields:
            code_txt = sa.code or ''
        low = ((sa.name or '') + ' ' + model_txt + ' ' + code_txt).lower()
        hits = []
        for term in sa_terms:
            if term in low:
                hits.append(term)
        xmls = []
        imds = Imd.search([('model', '=', 'ir.actions.server'), ('res_id', '=', sa.id)], order='module,name', limit=8)
        for imd in imds:
            xmls.append('%s.%s' % (imd.module or '', imd.name or ''))
        lines.append('SERVER_ACTION id=%s name=%r model=%s state=%s xmlid=%s code_len=%s hits=%s' % (
            sa.id, sa.name or '', model_txt, sa.state or '', ', '.join(xmls) or '(no xmlid)', len(code_txt), ', '.join(hits) or '(none)'
        ))
else:
    lines.append('(no matching server actions found)')

# Automated actions are optional depending on installed modules.
try:
    Automation = env['base.automation'].sudo()
    auto_ids = []
    for term in sa_terms:
        autos = Automation.search(['|', ('name', 'ilike', term), ('action_server_ids.code', 'ilike', term)], order='name,id', limit=80)
        for au in autos:
            if au.id not in auto_ids:
                auto_ids.append(au.id)
    if auto_ids:
        for aid in auto_ids:
            au = Automation.browse(aid)
            if not au.exists():
                continue
            model_txt = ''
            if 'model_id' in Automation._fields and au.model_id:
                model_txt = au.model_id.model or ''
            active_txt = ''
            if 'active' in Automation._fields:
                active_txt = au.active
            trigger_txt = ''
            if 'trigger' in Automation._fields:
                trigger_txt = au.trigger or ''
            lines.append('AUTOMATION id=%s name=%r model=%s active=%s trigger=%s' % (au.id, au.name or '', model_txt, active_txt, trigger_txt))
    else:
        lines.append('(no matching automated actions found)')
except Exception:
    lines.append('(base.automation scan skipped/unavailable on this database)')
lines.append('')

# ---------------------------------------------------------------------------
# 6) Paperformat sharing detail for all selected reports.
# ---------------------------------------------------------------------------
lines.append('============================================================')
lines.append('6. PAPERFORMAT SHARING SUMMARY')
lines.append('============================================================')
paper_ids = []
for rep in reports:
    if rep.exists() and 'paperformat_id' in Report._fields and rep.paperformat_id:
        if rep.paperformat_id.id not in paper_ids:
            paper_ids.append(rep.paperformat_id.id)
if paper_ids:
    for pid in paper_ids:
        p = Paper.browse(pid)
        if not p.exists():
            continue
        users = Report.search([('paperformat_id', '=', p.id)], order='model,name,id')
        lines.append('PAPER id=%s name=%r used_by=%s reports margins T/B/L/R=%s/%s/%s/%s header_spacing=%s dpi=%s' % (p.id, p.name or '', len(users), p.margin_top, p.margin_bottom, p.margin_left, p.margin_right, p.header_spacing, p.dpi))
        ucount = 0
        for ur in users:
            ucount = ucount + 1
            if ucount > 30:
                lines.append('  ... more paperformat users omitted')
                break
            lines.append('  user report id=%s model=%s name=%r report_name=%s' % (ur.id, ur.model or '', ur.name or '', ur.report_name or ''))
else:
    lines.append('(no paperformats on selected reports)')
lines.append('')

# ---------------------------------------------------------------------------
# 7) Interpretation guide.
# ---------------------------------------------------------------------------
lines.append('============================================================')
lines.append('7. HOW TO READ THIS OUTPUT / NEXT DECISION')
lines.append('============================================================')
lines.append('A. For each print option, read REPORT ACTION -> report_name -> ROOT QWEB VIEW IDS -> VIEW -> t-call targets.')
lines.append('B. direct inherited children under sale.report_saleorder*, purchase.report_purchase*, web.external_layout*, or account.report_invoice* are live patch points.')
lines.append('C. DDS/Dodo/Studio/Advanced Invoice risk terms mean do not reuse that chain for a BARANI isolated report.')
lines.append('D. To reproduce the safe VAT pattern for SO/Q/PF/PO, use a new report action, standalone root view with inherit_id empty, standalone layout view with inherit_id empty, and dedicated paperformat.')
lines.append('E. Do not modify the current DDS/Odoo print actions until this map is reviewed.')
lines.append('F. Paste all pages of this output back. If MORE REMAINS is YES, increment PAGE and rerun.')
lines.append('')

full = '\n'.join(lines)
start = (PAGE - 1) * PAGE_SIZE
end = PAGE * PAGE_SIZE
chunk = full[start:end]
more = 'NO'
if end < len(full):
    more = 'YES'
header = 'PAGE %s | chars %s-%s of %s | MORE REMAINS: %s\n' % (PAGE, start, end, len(full), more)
footer = '\n--- END PAGE %s | MORE REMAINS: %s ---' % (PAGE, more)
if more == 'YES':
    footer = footer + '\nSet PAGE=%s and rerun to continue.' % (PAGE + 1)
raise UserError(header + chunk + footer)
