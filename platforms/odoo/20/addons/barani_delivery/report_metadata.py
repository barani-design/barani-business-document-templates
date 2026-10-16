"""Install/update only the accepted report metadata; never infer duplicate roles."""
import logging

from odoo import api, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
NATIVE_LABEL_SOURCES = {
    'barani_delivery.action_report_delivery_note': (
        'stock.action_report_delivery', 'stock.report_deliveryslip',
        'barani_delivery.report_delivery_note_2026',
    ),
    'barani_delivery.action_report_picking_operations': (
        'stock.action_report_picking', 'stock.report_picking',
        'barani_delivery.report_picking_operations_2026',
    ),
}
CONTRACTS = [('barani_delivery.paperformat_delivery', 'report.paperformat', [('name', '=', 'BARANI Delivery A4 7mm')], {'name': 'BARANI Delivery A4 7mm', 'format': 'A4', 'orientation': 'Portrait', 'margin_top': 40.0, 'margin_bottom': 18.0, 'margin_left': 7.0, 'margin_right': 7.0, 'header_line': False, 'header_spacing': 35.0, 'dpi': 90, 'page_width': 0.0, 'page_height': 0.0, 'disable_shrinking': False, 'css_margins': False, 'default': False}), ('barani_delivery.paperformat_picking_operations', 'report.paperformat', [('name', '=', 'BARANI Picking Operations A4 7mm')], {'name': 'BARANI Picking Operations A4 7mm', 'format': 'A4', 'orientation': 'Portrait', 'margin_top': 40.0, 'margin_bottom': 18.0, 'margin_left': 7.0, 'margin_right': 7.0, 'header_line': False, 'header_spacing': 35.0, 'dpi': 90, 'page_width': 0.0, 'page_height': 0.0, 'disable_shrinking': False, 'css_margins': False, 'default': False}), ('barani_delivery.action_report_delivery_note', 'ir.actions.report', [('name', '=', 'Delivery Slip')], {'model': 'stock.picking', 'report_type': 'qweb-pdf', 'report_name': 'barani_delivery.report_delivery_note_2026', 'print_report_name': "(((object.name or '')[7:] if (object.name or '')[:7] == 'BA/OUT/' else (object.name or 'DN')).replace('/', '_')) + ' - Delivery Note'"}), ('barani_delivery.action_report_sale_delivery_note', 'ir.actions.report', [('name', '=', 'Delivery Note')], {'model': 'sale.order', 'report_type': 'qweb-pdf', 'report_name': 'barani_delivery.report_sale_order_delivery_note_2026', 'print_report_name': "(((((object.picking_ids.filtered_domain([('picking_type_id.code','=','outgoing'),('state','!=','cancel')])).name or '')[7:] if ((object.picking_ids.filtered_domain([('picking_type_id.code','=','outgoing'),('state','!=','cancel')])).name or '')[:7] == 'BA/OUT/' else ((object.picking_ids.filtered_domain([('picking_type_id.code','=','outgoing'),('state','!=','cancel')])).name or 'DN'))).replace('/', '_') + ' - Delivery Note') if len(object.picking_ids.filtered_domain([('picking_type_id.code','=','outgoing'),('state','!=','cancel')])) == 1 else ((((object.name or '')[3:] if (object.name or '')[:3] in ('SO/','PF/') else (object.name or '')[2:] if (object.name or '')[:2] == 'Q/' else (object.name or ''))).replace('/', '_') + (' - Delivery Notes' if len(object.picking_ids.filtered_domain([('picking_type_id.code','=','outgoing'),('state','!=','cancel')])) > 1 else ' - Delivery Note Unavailable'))"}), ('barani_delivery.action_report_picking_operations', 'ir.actions.report', [('name', '=', 'Picking Operations')], {'model': 'stock.picking', 'report_type': 'qweb-pdf', 'report_name': 'barani_delivery.report_picking_operations_2026', 'print_report_name': "(((object.name or '')[7:] if (object.name or '')[:7] == 'BA/OUT/' else (object.name or 'Picking')).replace('/', '_')) + ' - Picking Operations'"})]


class BaraniReportMetadata(models.Model):
    _inherit = 'ir.actions.report'

    @api.model
    def _barani_delivery_adopt_metadata(self):
        # XML loader calls this in the same transaction before loading owned records.
        # No deletion, record merge, business write or explicit commit is performed.
        for xmlid, model, domain, expected in CONTRACTS:
            module, name = xmlid.split('.', 1)
            data = self.env['ir.model.data'].sudo().search([
                ('module', '=', module), ('name', '=', name),
            ])
            rows = self.env[model].sudo().with_context(lang='en_US', active_test=False).search(domain)
            if len(data) > 1:
                raise ValidationError('Ambiguous BARANI metadata: ' + xmlid)
            if xmlid in NATIVE_LABEL_SOURCES:
                native_xmlid, native_route, barani_route = NATIVE_LABEL_SOURCES[xmlid]
                native = self.env.ref(native_xmlid, raise_if_not_found=False)
                if (not native or native._name != model or not native.exists()
                        or native.model != 'stock.picking'
                        or native.report_type != 'qweb-pdf'
                        or native.report_name not in (native_route, barani_route)):
                    raise ValidationError('Native BARANI label source mismatch: ' + native_xmlid)
                if data and data.model == model and data.res_id == native.id:
                    raise ValidationError('BARANI metadata XML ID collision: ' + xmlid)
                # Native actions are label sources here. The final XML override
                # routes them to BARANI documents while keeping them unbound.
                # Never adopt or modify the native actions in this method.
                # Exclude by exact XML ID only; unknown same-label rows still fail.
                rows -= native
            if len(rows) > 1:
                raise ValidationError('Ambiguous BARANI metadata: ' + xmlid)
            if data:
                if data.model != model or not rows or data.res_id != rows.id:
                    raise ValidationError('BARANI metadata XML ID collision: ' + xmlid)
                # Existing managed record: validate identity, allow controlled XML update.
                continue
            if not rows:
                continue  # Clean installation: the following XML creates this role.
            for key, value in expected.items():
                actual = rows[key]
                if actual != value:
                    raise ValidationError('Legacy BARANI metadata mismatch: ' + xmlid + ':' + key)
            self.env['ir.model.data'].sudo().create({
                'module': module, 'name': name, 'model': model,
                'res_id': rows.id, 'noupdate': False,
            })
            _logger.info('BARANI metadata adopted %s -> %s,%s', xmlid, model, rows.id)

    @api.model
    def _barani_delivery_sync_labels(self):
        languages = self.env['res.lang'].with_context(active_test=False).search([('active', '=', True)]).mapped('code')
        for native, target in [
            ('stock.action_report_delivery', 'barani_delivery.action_report_delivery_note'),
            ('stock.action_report_picking', 'barani_delivery.action_report_picking_operations'),
        ]:
            for lang in set(languages + ['en_US']):
                label = self.env.ref(native).with_context(lang=lang).name
                self.env.ref(target).with_context(lang=lang).name = label
