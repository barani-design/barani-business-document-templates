"""Install/update only the accepted report metadata; never infer duplicate roles."""
import logging

from odoo import api, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
CONTRACTS = [('barani_vat.paperformat_vat', 'report.paperformat', [('name', '=', 'BARANI VAT A4 7mm')], {'name': 'BARANI VAT A4 7mm', 'format': 'A4', 'orientation': 'Portrait', 'margin_top': 40.0, 'margin_bottom': 18.0, 'margin_left': 7.0, 'margin_right': 7.0, 'header_line': False, 'header_spacing': 35.0, 'dpi': 90, 'page_width': 0.0, 'page_height': 0.0, 'disable_shrinking': False, 'css_margins': False, 'default': False}), ('barani_vat.action_report_vat_2026', 'ir.actions.report', [('name', '=', 'VAT Invoices RI/DPI - 2026+')], {'model': 'account.move', 'report_type': 'qweb-pdf', 'report_name': 'barani_vat.report_invoice_document_vat', 'print_report_name': "((object.name or '').replace('/', '_') + ' - ' if object.name and object.name != '/' else '') + ('Credit Note' if object.move_type == 'out_refund' else 'Vendor Credit Note' if object.move_type == 'in_refund' else 'Vendor Bill' if object.move_type == 'in_invoice' else 'Draft Invoice' if object.state == 'draft' else 'Cancelled Invoice' if object.state == 'cancel' else 'Invoice')"}), ('barani_vat.action_invoice_preview', 'ir.actions.report', [('name', '=', 'Invoice Preview')], {'model': 'account.move', 'report_type': 'qweb-html', 'report_name': 'barani_vat.report_invoice_document_vat', 'print_report_name': "((object.name or '').replace('/', '_') + ' - ' if object.name and object.name != '/' else '') + ('Credit Note' if object.move_type == 'out_refund' else 'Vendor Credit Note' if object.move_type == 'in_refund' else 'Vendor Bill' if object.move_type == 'in_invoice' else 'Draft Invoice' if object.state == 'draft' else 'Cancelled Invoice' if object.state == 'cancel' else 'Invoice')"})]


class BaraniReportMetadata(models.Model):
    _inherit = 'ir.actions.report'

    @api.model
    def _barani_vat_adopt_metadata(self):
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


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _barani_report_attachment_filename(self):
        # Odoo19 removed the accepted Odoo16 attachment helper. Preserve its rule.
        self.ensure_one()
        name = (self.name or self.env._('INV')) if self.state == 'posted' else self._get_report_base_filename()
        return f"{name.replace('/', '_')}.pdf"
