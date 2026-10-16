"""Install/update only the accepted report metadata; never infer duplicate roles."""
import logging

from odoo import api, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
CONTRACTS = [('barani_commercial.paperformat_commercial', 'report.paperformat', [('name', '=', 'BARANI Commercial A4 7mm')], {'name': 'BARANI Commercial A4 7mm', 'format': 'A4', 'orientation': 'Portrait', 'margin_top': 40.0, 'margin_bottom': 18.0, 'margin_left': 7.0, 'margin_right': 7.0, 'header_line': False, 'header_spacing': 35.0, 'dpi': 90, 'page_width': 0.0, 'page_height': 0.0, 'disable_shrinking': False, 'css_margins': False, 'default': False}), ('barani_commercial.action_report_saleorder_2026', 'ir.actions.report', [('name', '=', 'Quotation / Order — 2026+')], {'model': 'sale.order', 'report_type': 'qweb-pdf', 'report_name': 'barani_commercial.report_saleorder', 'print_report_name': "(((object.name or '')[3:] if (object.name or '')[:3] in ('SO/','PF/') else (object.name or '')[2:] if (object.name or '')[:2] == 'Q/' else (object.name or ''))).replace('/', '_') + (' - Quotation' if object.state in ('draft','sent','cancel') else ' - Sales Order')"}), ('barani_commercial.action_report_proforma_2026', 'ir.actions.report', [('name', '=', 'PRO-FORMA — 2026+')], {'model': 'sale.order', 'report_type': 'qweb-pdf', 'report_name': 'barani_commercial.report_saleorder_proforma', 'print_report_name': "(((object.name or '')[3:] if (object.name or '')[:3] in ('SO/','PF/') else (object.name or '')[2:] if (object.name or '')[:2] == 'Q/' else (object.name or ''))).replace('/', '_') + ' - Pro-Forma Invoice'"})]


class BaraniReportMetadata(models.Model):
    _inherit = 'ir.actions.report'

    @api.model
    def _barani_commercial_adopt_metadata(self):
        # XML loader calls this in the same transaction before loading owned records.
        # No deletion, record merge, business write or explicit commit is performed.
        for xmlid, model, domain, expected in CONTRACTS:
            module, name = xmlid.split('.', 1)
            data = self.env['ir.model.data'].sudo().search([
                ('module', '=', module), ('name', '=', name),
            ])
            rows = self.env[model].sudo().with_context(lang='en_US', active_test=False).search(domain)
            if len(data) > 1 or len(rows) > 1:
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
