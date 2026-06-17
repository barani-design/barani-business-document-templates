# ============================================================================
# ACTION NAME : READ-ONLY — BARANI DN L2 nested-kit package-count probe v5.0
# MODEL       : stock.picking preferred; Module (ir.module.module) is also OK.
# ACTION TO DO: Execute Python Code
# RUN BY      : Run after BOM/product master-data changes, on a newly generated or safely recreated delivery.
# PURPOSE     : Verify whether DN L2 will show the expected number of package identifiers when a
#               top-level sale product/kit contains another kit/subassembly and a product.
#               This probe performs no writes and does not render PDFs.
# READ-ONLY   : search/read only; raises paged UserError output. No create/write/unlink/set_param/commit.
# DDS/BRN     : No dds_ or brn_ dependencies.
# ============================================================================

ACTION_NAME = 'READ-ONLY — BARANI DN L2 nested-kit package-count probe v5.0'
READ_ONLY = True
PAGE = 1
PAGE_SIZE = 15000
MAX_PICKINGS = 6
MAX_LINES = 120

# Optional manual targets. Leave empty to use selected stock.picking records.
PICKING_NAMES = []
SALE_ORDER_NAMES = []

lines = []
lines.append(ACTION_NAME)
lines.append('READ_ONLY=%s | PAGE=%s PAGE_SIZE=%s | MAX_PICKINGS=%s' % (READ_ONLY, PAGE, PAGE_SIZE, MAX_PICKINGS))
lines.append('Purpose: verify actual stock-move package count vs top-level BoM/package expectation for DN L2; no writes.')
lines.append('Manual PICKING_NAMES=%s | SALE_ORDER_NAMES=%s' % (', '.join(PICKING_NAMES) if PICKING_NAMES else '(empty)', ', '.join(SALE_ORDER_NAMES) if SALE_ORDER_NAMES else '(empty)'))
lines.append('')

required_ok = True
required_models = ['stock.picking', 'stock.move', 'stock.move.line', 'sale.order', 'sale.order.line', 'mrp.bom', 'mrp.bom.line', 'product.product']
lines.append('1) MODEL READINESS')
for model_name in required_models:
    if model_name in env:
        lines.append('  %-18s FOUND id=%s' % (model_name, env['ir.model'].sudo().search([('model', '=', model_name)], limit=1).id))
    else:
        lines.append('  %-18s MISSING' % model_name)
        required_ok = False
if not required_ok:
    raise UserError('\n'.join(lines))
lines.append('')

field_specs = []
field_specs.append(('stock.picking', ['name', 'origin', 'sale_id', 'state', 'move_ids_without_package', 'move_line_ids']))
field_specs.append(('stock.move', ['product_id', 'sale_line_id', 'bom_line_id', 'move_line_ids', 'product_uom_qty', 'quantity_done', 'state']))
field_specs.append(('stock.move.line', ['move_id', 'product_id', 'lot_id', 'qty_done', 'reserved_uom_qty']))
field_specs.append(('sale.order', ['name', 'order_line', 'picking_ids']))
field_specs.append(('sale.order.line', ['order_id', 'display_type', 'product_id', 'product_uom_qty', 'qty_delivered', 'name']))
field_specs.append(('mrp.bom', ['product_tmpl_id', 'product_id', 'type', 'bom_line_ids', 'product_qty']))
field_specs.append(('mrp.bom.line', ['bom_id', 'product_id', 'product_qty']))
field_specs.append(('product.product', ['display_name', 'default_code', 'barcode', 'product_tmpl_id', 'tracking', 'hs_code', 'country_of_origin']))
lines.append('2) FIELD READINESS')
for model_name, field_list in field_specs:
    ok = True
    model = env[model_name]
    for fname in field_list:
        if fname not in model._fields:
            lines.append('  %s.%s: MISSING' % (model_name, fname))
            ok = False
            required_ok = False
    if ok:
        lines.append('  %s: PASS' % model_name)
if not required_ok:
    lines.append('ERROR: missing required fields; stop.')
    raise UserError('\n'.join(lines))
lines.append('')

Picking = env['stock.picking'].sudo()
Sale = env['sale.order'].sudo()
Bom = env['mrp.bom'].sudo()

pickings = Picking.browse()
selected = records if records and records._name == 'stock.picking' else Picking.browse()
if selected:
    pickings = selected[:MAX_PICKINGS]
    lines.append('3) PICKING COLLECTION')
    lines.append('  Source: selected stock.picking records')
else:
    lines.append('3) PICKING COLLECTION')
    if PICKING_NAMES:
        for pname in PICKING_NAMES:
            found = Picking.search([('name', '=', pname)], limit=MAX_PICKINGS)
            pickings = pickings | found
            found_ids_txt = ''
            for x in found:
                if found_ids_txt:
                    found_ids_txt += ','
                found_ids_txt += str(x.id)
            lines.append('  manual picking lookup %s -> ids=%s' % (pname, found_ids_txt))
    if not pickings and SALE_ORDER_NAMES:
        for sname in SALE_ORDER_NAMES:
            so = Sale.search([('name', '=', sname)], limit=1)
            if so:
                pickings = pickings | so.picking_ids
                so_pick_ids_txt = ''
                for x in so.picking_ids:
                    if so_pick_ids_txt:
                        so_pick_ids_txt += ','
                    so_pick_ids_txt += str(x.id)
                lines.append('  manual sale lookup %s -> picking ids=%s' % (sname, so_pick_ids_txt))
    if not pickings:
        pickings = Picking.search([('picking_type_id.code', '=', 'outgoing')], order='id desc', limit=MAX_PICKINGS)
        lines.append('  fallback: recent outgoing pickings')
pick_ids_txt = ''
for x in pickings:
    if pick_ids_txt:
        pick_ids_txt += ','
    pick_ids_txt += str(x.id)
lines.append('  Count: %s ids=%s' % (len(pickings), pick_ids_txt))
lines.append('')

lines.append('4) NESTED KIT / PACKAGE COUNT EVIDENCE')
if not pickings:
    lines.append('  No pickings found.')

for picking in pickings[:MAX_PICKINGS]:
    lines.append('-' * 80)
    lines.append('PICKING %s id=%s state=%s origin=%s sale=%s moves=%s move_lines=%s' % (
        picking.name, picking.id, picking.state, picking.origin or '', picking.sale_id.name if picking.sale_id else '',
        len(picking.move_ids_without_package), len(picking.move_line_ids)))
    if not picking.sale_id:
        lines.append('  NO SALE ORDER: DN L2 kit grouping cannot compare against invoice/sale parent lines.')
        continue
    for sol in picking.sale_id.order_line:
        if sol.display_type:
            if sol.display_type == 'line_note' and sol.name:
                lines.append('  SO NOTE id=%s name=%s' % (sol.id, sol.name[:100]))
            continue
        parent_product = sol.product_id
        # Find BoM candidates for the sale-line product.
        boms = Bom.search(['|', ('product_id', '=', parent_product.id), '&', ('product_id', '=', False), ('product_tmpl_id', '=', parent_product.product_tmpl_id.id)], limit=10)
        chosen_bom = Bom.browse()
        for bom in boms:
            if not chosen_bom:
                chosen_bom = bom
        # Component stock moves linked to this sale line and not the parent product.
        component_moves = env['stock.move'].sudo().browse()
        parent_moves = env['stock.move'].sudo().browse()
        for move in picking.move_ids_without_package:
            if move.state != 'cancel' and move.product_id and move.sale_line_id and move.sale_line_id.id == sol.id:
                if move.product_id.id == parent_product.id:
                    parent_moves = parent_moves | move
                else:
                    component_moves = component_moves | move
        top_bom_line_count = len(chosen_bom.bom_line_ids) if chosen_bom else 0
        component_move_count = len(component_moves)
        lines.append('  SALE LINE id=%s product=%s default_code=%s barcode=%s hs=%s coo=%s ordered=%s delivered=%s' % (
            sol.id, parent_product.display_name or '', parent_product.default_code or '', parent_product.barcode or '',
            parent_product.hs_code or '', parent_product.country_of_origin.code if parent_product.country_of_origin else '',
            sol.product_uom_qty, sol.qty_delivered))
        if chosen_bom:
            lines.append('    TOP BOM id=%s type=%s top_lines=%s' % (chosen_bom.id, chosen_bom.type or '', top_bom_line_count))
            idx = 0
            for bl in chosen_bom.bom_line_ids:
                idx += 1
                nested_boms = Bom.search(['|', ('product_id', '=', bl.product_id.id), '&', ('product_id', '=', False), ('product_tmpl_id', '=', bl.product_id.product_tmpl_id.id)], limit=5)
                nested_ids_txt = ''
                for nb in nested_boms:
                    if nested_ids_txt:
                        nested_ids_txt += ','
                    nested_ids_txt += str(nb.id)
                nested_txt = 'nested_bom_ids=%s' % nested_ids_txt
                lines.append('      TOP BOMLINE %s id=%s product=%s default_code=%s barcode=%s qty=%s %s' % (
                    idx, bl.id, bl.product_id.display_name or '', bl.product_id.default_code or '', bl.product_id.barcode or '', bl.product_qty, nested_txt))
        else:
            lines.append('    TOP BOM: none found')
        lines.append('    DN L2 current package count from actual component stock moves = %s' % component_move_count)
        if component_moves:
            cidx = 0
            for cm in component_moves:
                cidx += 1
                lots_txt = ''
                for ml in cm.move_line_ids:
                    if ml.lot_id and ml.lot_id.name:
                        if lots_txt:
                            lots_txt += ', '
                        lots_txt += ml.lot_id.name
                nested_boms_for_move = Bom.search(['|', ('product_id', '=', cm.product_id.id), '&', ('product_id', '=', False), ('product_tmpl_id', '=', cm.product_id.product_tmpl_id.id)], limit=5)
                nested_move_ids_txt = ''
                for nb in nested_boms_for_move:
                    if nested_move_ids_txt:
                        nested_move_ids_txt += ','
                    nested_move_ids_txt += str(nb.id)
                lines.append('      MOVE package %s id=%s product=%s default_code=%s barcode=%s bom_line_id=%s qty=%s done=%s lots=%s nested_bom_ids=%s' % (
                    cidx, cm.id, cm.product_id.display_name or '', cm.product_id.default_code or '', cm.product_id.barcode or '',
                    cm.bom_line_id.id if cm.bom_line_id else '', cm.product_uom_qty, cm.quantity_done, lots_txt or '(none)',
                    nested_move_ids_txt))
        if chosen_bom and component_move_count == top_bom_line_count:
            lines.append('    VERDICT: ACTUAL_PACKAGES_MATCH_TOP_LEVEL_BOM_LINES. DN L2 should show %s package(s).' % component_move_count)
        elif chosen_bom and component_move_count > top_bom_line_count:
            lines.append('    VERDICT: ACTUAL_MOVES_EXCEED_TOP_LEVEL_BOM_LINES. Nested phantom/subcomponent expansion may make DN L2 show leaf packages, not top-level packages.')
        elif chosen_bom and component_move_count < top_bom_line_count:
            lines.append('    VERDICT: ACTUAL_MOVES_LESS_THAN_TOP_LEVEL_BOM_LINES. Delivery may be partial, unassigned, or generated from changed BoM.')
        elif not chosen_bom and component_move_count:
            lines.append('    VERDICT: COMPONENT_MOVES_WITHOUT_TOP_BOM. Investigate sale/move links before trusting DN L2 grouping.')
        else:
            lines.append('    VERDICT: NON_KIT_OR_NO_COMPONENT_MOVES. DN L2 should print normal stock-move rows.')
lines.append('')
lines.append('5) SUMMARY / RULE')
lines.append('  DN L2 does not mutate BoMs or pickings. It prints package identifiers from actual stock moves linked to the top sale line.')
lines.append('  If top-level kit contains another kit and a product, DN L2 will show two package(s) only when the resulting picking has two linked component stock moves.')
lines.append('  If Odoo recursively explodes the nested kit into additional stock moves, DN L2 may show the leaf stock moves unless master data is adjusted or report logic is changed to collapse by top-level BoM line.')
lines.append('END OF READ-ONLY PROBE')

full = '\n'.join(lines)
start = (PAGE - 1) * PAGE_SIZE
end = start + PAGE_SIZE
more = 'YES' if end < len(full) else 'NO'
header = '============ PAGED OUTPUT ============\nFULL = %s chars | PAGE %s | SHOWING %s-%s | MORE REMAINS: %s\n======================================\n' % (len(full), PAGE, start, min(end, len(full)), more)
raise UserError(header + full[start:end])
