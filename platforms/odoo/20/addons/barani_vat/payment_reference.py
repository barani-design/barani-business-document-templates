"""Read-only report references; assignment remains with the existing workflow."""
from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _barani_report_payment_reference(self):
        """Display the stored reference without deriving a new payment identity.

        Marked order invoices reuse the companion's existing validation, including
        after its company option is disabled. Unmarked records retain their native
        reference exactly; blank draft references remain blank. No record is written.
        """
        self.ensure_one()
        marker_fields = ('barani_order_payment_reference', 'barani_reference_order_id')
        if any(field in self._fields and self[field] for field in marker_fields):
            self._barani_validate_order_payment_reference()
        return '' if self.move_type == 'out_refund' else (self.payment_reference or '')

    def _barani_report_original_payment_reference(self):
        """A credit's historical reference must come from its linked original."""
        self.ensure_one()
        if self.move_type not in ('out_refund', 'in_refund') or not self.reversed_entry_id:
            return ''
        return self.reversed_entry_id._barani_report_payment_reference()
