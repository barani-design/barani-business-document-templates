"""Retire legacy invoice Preview routing while retaining its audit record."""

import logging

from odoo import api, models


_logger = logging.getLogger(__name__)


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    @api.model
    def _barani_vat_retire_legacy_preview_views(self):
        """Deactivate active, XML-ID-less direct invoice Preview extensions.

        Called on install and update before the module's Preview view loads.
        Keep module, Studio and imported views with any XML ID untouched.
        Never delete a view; repeated calls are no-ops after retirement.
        """
        form = self.env.ref("account.view_move_form")
        candidates = self.sudo().with_context(active_test=False).search([
            ("model", "=", "account.move"),
            ("type", "=", "form"),
            ("mode", "=", "extension"),
            ("inherit_id", "=", form.id),
            ("active", "=", True),
        ])
        if not candidates:
            return
        with_xmlid = set(self.env["ir.model.data"].sudo().search([
            ("model", "=", "ir.ui.view"),
            ("res_id", "in", candidates.ids),
        ]).mapped("res_id"))
        legacy = candidates.filtered(
            lambda view: view.id not in with_xmlid
            and "preview_invoice" in (view.arch or "")
        )
        for view in legacy:
            _logger.info(
                "BARANI VAT retiring legacy preview view %s (%r, priority %s, created %s)",
                view.id, view.name, view.priority, view.create_date,
            )
        if legacy:
            legacy.write({"active": False})
