"""Read-only Odoo20 adapters for the accepted stock report semantics."""
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    barani_report_done_qty = fields.Float(
        compute='_compute_barani_report_done_qty', digits='Product Unit',
        string='BARANI report completed/picked quantity', store=False,
    )

    @api.depends('state', 'uom_id', 'move_line_ids.quantity',
                 'move_line_ids.picked', 'move_line_ids.uom_id')
    def _compute_barani_report_done_qty(self):
        for move in self:
            # move.picked is any(line.picked); it cannot guard move.quantity.
            lines = move.move_line_ids.filtered(
                lambda line: move.state == 'done' or line.picked)
            move.barani_report_done_qty = sum(
                line.uom_id._compute_quantity(
                    line.quantity, move.uom_id, round=False)
                for line in lines
            ) if move.state != 'cancel' else 0.0


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _barani_report_moves(self):
        self.ensure_one()
        moves = self.move_ids.filtered(lambda move: not move.is_scrap)
        if self.picking_type_entire_packs:
            # Odoo19 replaced package_level_id with is_entire_pack on move lines.
            # Preserve the legacy product-row exclusion for entire-package mode.
            moves = moves.filtered(lambda move:
                any(not line.is_entire_pack for line in move.move_line_ids)
                or (not move.move_line_ids and move.state not in ('assigned', 'done')))
        return moves
