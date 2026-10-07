# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestBaraniReportRouting(TransactionCase):

    def test_templates_exist_exactly_once(self):
        """No key may resolve to more than one template."""
        for key in ['barani_delivery.report_delivery_note_2026', 'barani_delivery.report_sale_order_delivery_note_2026', 'barani_delivery.report_picking_operations_2026', 'barani_delivery.external_layout_delivery_2026', 'barani_delivery.external_layout_picking_operations_2026']:
            views = self.env["ir.ui.view"].with_context(
                active_test=False).search([("key", "=", key)])
            self.assertEqual(
                len(views), 1,
                "expected exactly one template for %s, found %s"
                % (key, len(views)))
            self.assertTrue(views.active, "%s is switched off" % key)

