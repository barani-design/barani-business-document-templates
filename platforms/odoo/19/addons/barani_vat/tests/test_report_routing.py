# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestBaraniReportRouting(TransactionCase):

    def test_templates_exist_exactly_once(self):
        """No key may resolve to more than one template."""
        for key in ['barani_vat.report_invoice_document_vat', 'barani_vat.external_layout_standard_titled']:
            views = self.env["ir.ui.view"].with_context(
                active_test=False).search([("key", "=", key)])
            self.assertEqual(
                len(views), 1,
                "expected exactly one template for %s, found %s"
                % (key, len(views)))
            self.assertTrue(views.active, "%s is switched off" % key)

    def test_routing_account_account_invoices(self):
        """The Print button must reach the BARANI layout."""
        report = self.env.ref("account.account_invoices")
        self.assertEqual(report.report_name, "barani_vat.report_invoice_document_vat")
        self.assertEqual(report.report_file, "barani_vat.report_invoice_document_vat")
        self.assertTrue(report.print_report_name)

    def test_routing_account_account_invoices_without_payment(self):
        """The Print button must reach the BARANI layout."""
        report = self.env.ref("account.account_invoices_without_payment")
        self.assertEqual(report.report_name, "barani_vat.report_invoice_document_vat")
        self.assertEqual(report.report_file, "barani_vat.report_invoice_document_vat")
        self.assertTrue(report.print_report_name)

