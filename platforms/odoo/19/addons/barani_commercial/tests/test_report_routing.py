# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestBaraniReportRouting(TransactionCase):

    def test_templates_exist_exactly_once(self):
        """No key may resolve to more than one template."""
        for key in ['barani_commercial.report_saleorder', 'barani_commercial.report_saleorder_document', 'barani_commercial.report_saleorder_proforma', 'barani_commercial.external_layout_standard_titled']:
            views = self.env["ir.ui.view"].with_context(
                active_test=False).search([("key", "=", key)])
            self.assertEqual(
                len(views), 1,
                "expected exactly one template for %s, found %s"
                % (key, len(views)))
            self.assertTrue(views.active, "%s is switched off" % key)

    def test_routing_sale_action_report_saleorder(self):
        """The Print button must reach the BARANI layout."""
        report = self.env.ref("sale.action_report_saleorder")
        self.assertEqual(report.report_name, "barani_commercial.report_saleorder")
        self.assertEqual(report.report_file, "barani_commercial.report_saleorder")
        self.assertTrue(report.print_report_name)

    def test_routing_sale_action_report_pro_forma_invoice(self):
        """The Print button must reach the BARANI layout."""
        report = self.env.ref("sale.action_report_pro_forma_invoice")
        self.assertEqual(report.report_name, "barani_commercial.report_saleorder_proforma")
        self.assertEqual(report.report_file, "barani_commercial.report_saleorder_proforma")
        self.assertTrue(report.print_report_name)

