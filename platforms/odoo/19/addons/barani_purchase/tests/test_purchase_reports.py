"""Real Odoo ORM/QWeb/PDF tests. Run on a development/test database only."""
import io
import json
import os
from pathlib import Path

from lxml import html

from odoo import Command
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tools.pdf import PdfFileReader
from odoo.tools.safe_eval import safe_eval

from ..hooks import ACTION, BACKUP_XMLID, ROUTE, pre_init_hook, uninstall_hook


@tagged('post_install', '-at_install', 'barani_purchase_reports')
class TestBaraniPurchaseReports(AccountTestInvoicingCommon):
    @classmethod
    def get_default_groups(cls):
        return (super().get_default_groups()
                | cls.env.ref('purchase.group_purchase_manager')
                | cls.env.ref('stock.group_stock_manager'))

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.external_report_layout_id = cls.env.ref('web.external_layout_standard')
        cls.delivery_partner = cls.env['res.partner'].create({
            'name': 'PO QA Receiving Address', 'street': '17 Receiving Road',
            'city': 'Bratislava', 'zip': '83101', 'country_id': cls.env.ref('base.sk').id,
            'phone': '+421111222333', 'email': 'receiving@example.invalid',
        })
        cls.warehouse = cls.env['stock.warehouse'].create({
            'name': 'PO QA Warehouse', 'code': 'BPQ',
            'company_id': cls.env.company.id, 'partner_id': cls.delivery_partner.id,
        })
        cls.partner_a.write({'name': 'PO QA Supplier', 'street': '8 Supplier Road',
                             'phone': '+421222333444', 'email': 'supplier@example.invalid'})
        cls.tax_23 = cls.env['account.tax'].create({
            'name': 'PO QA VAT 23%', 'amount': 23, 'amount_type': 'percent',
            'type_tax_use': 'purchase', 'company_id': cls.env.company.id,
            'tax_group_id': cls.tax_purchase_a.tax_group_id.id,
        })

    def _order(self, name='PO-QA-001'):
        return self.env['purchase.order'].create({
            'name': name, 'partner_id': self.partner_a.id,
            'company_id': self.env.company.id, 'currency_id': self.env.ref('base.EUR').id,
            'picking_type_id': self.warehouse.in_type_id.id,
            'date_order': '2026-09-15 12:00:00',
            'payment_term_id': self.pay_terms_a.id,
            'order_line': [Command.create({
                'product_id': self.product_a.id, 'name': 'PRECISION NUT M5',
                'product_qty': 1000, 'product_uom_id': self.uom_unit.id,
                'price_unit': 0.0119, 'date_planned': '2026-09-17 12:00:00',
                'tax_ids': [Command.set(self.tax_23.ids)],
            })],
        })

    def _html(self, orders):
        self.assertFalse(self.env.su, 'Render with ordinary test-user access rights')
        body, kind = self.env['ir.actions.report'].with_context(
            allowed_company_ids=orders.company_id.ids,
        )._render_qweb_html(ACTION, orders.ids)
        self.assertEqual(kind, 'html')
        return html.fromstring(body)

    def _pdf(self, orders, label, minimum_pages):
        body, kind = self.env['ir.actions.report'].with_context(
            force_report_rendering=True, report_pdf_no_attachment=True,
        )._render_qweb_pdf(ACTION, orders.ids)
        self.assertEqual(kind, 'pdf')
        self.assertTrue(body.startswith(b'%PDF-'))
        pdf = PdfFileReader(io.BytesIO(body))
        self.assertGreaterEqual(len(pdf.pages), minimum_pages)
        for page in pdf.pages:
            self.assertAlmostEqual(float(page.mediabox.width), 595.28, delta=2)
            self.assertAlmostEqual(float(page.mediabox.height), 841.89, delta=2)
        output = Path(os.environ.get('BARANI_REPORT_OUTPUT', '/tmp/barani_purchase_reports'))
        output.mkdir(parents=True, exist_ok=True)
        (output / (label + '.pdf')).write_bytes(body)

    def test_native_action_titles_and_filename(self):
        report = self.env.ref(ACTION)
        self.assertEqual(report.report_name, ROUTE)
        self.assertEqual(report.report_file, ROUTE)
        self.assertEqual(report.paperformat_id, self.env.ref('barani_purchase.paperformat_purchase'))
        self.assertFalse(report.attachment_use)
        self.assertEqual(self.env.ref('purchase.report_purchase_quotation').report_name,
                         'purchase.report_purchasequotation')
        order = self._order()
        for state, title in [('draft', 'Request for Quotation'), ('sent', 'Request for Quotation'),
                             ('to approve', 'Request for Quotation'), ('purchase', 'Purchase Order'),
                             ('cancel', 'Cancelled Purchase Order')]:
            order.write({'state': state})
            document = self._html(order)
            self.assertEqual(document.xpath('//*[@name="barani_purchase_title"]')[0].text_content(), title)
            self.assertEqual(safe_eval(report.print_report_name, {'object': order}), 'PO-QA-001 - ' + title)
            self.assertEqual(report.report_action(order)['report_name'], ROUTE)

    def test_precision_column_order_and_rounded_totals(self):
        order = self._order()
        document = self._html(order)
        headers = document.xpath('//table[@name="barani_po_lines"]/thead/tr/th')
        self.assertEqual([h.text_content().strip() for h in headers],
                         ['Description', 'HS Code', 'COO', 'Qty', 'Unit', 'Unit Price',
                          'Disc.', 'VAT Rate', 'VAT', 'VAT Base'])
        self.assertIn('0.0119', document.xpath('//*[@name="td_priceunit"]')[0].text_content())
        self.assertIn('1,000', document.xpath('//*[@name="td_qty"]')[0].text_content())
        self.assertIn(self.uom_unit.name, document.xpath('//*[@name="td_unit"]')[0].text_content())
        self.assertAlmostEqual(order.amount_untaxed, 11.90)
        self.assertAlmostEqual(order.amount_tax, 2.74)
        self.assertAlmostEqual(order.amount_total, 14.64)
        self.assertIn('14.64', document.xpath('//*[@name="barani_po_tax_totals"]')[0].text_content())

    def test_discount_included_tax_and_global_rounding(self):
        order = self._order()
        line = order.order_line
        for included in (False, True):
            tax = self.tax_23.copy({'price_include_override': 'tax_included' if included else 'tax_excluded'})
            line.write({'product_qty': 3, 'price_unit': 12.30, 'discount': 10,
                        'tax_ids': [Command.set(tax.ids)]})
            order.company_id.tax_calculation_rounding_method = 'round_globally'
            document = self._html(order)
            self.assertIn('10', document.xpath('//*[@name="td_discount"]')[0].text_content())
            self.assertIn('23', document.xpath('//*[@name="td_vatrate"]')[0].text_content())
            totals = document.xpath('//*[@name="barani_po_tax_totals"]')[0].text_content()
            self.assertIn('%.2f' % order.amount_total, totals)
            self.assertAlmostEqual(order.amount_total, 33.21 if included else 40.85)
        line.tax_ids = [Command.clear()]
        document = self._html(order)
        self.assertIn('N/A', document.xpath('//*[@name="td_vatrate"]')[0].text_content())
        self.assertAlmostEqual(order.amount_tax, 0)

    def test_warehouse_and_explicit_delivery_address(self):
        order = self._order()
        document = self._html(order)
        shipping = document.xpath('//*[@name="barani_po_shipping"]')[0].text_content()
        self.assertIn('PO QA Warehouse', shipping)
        self.assertIn('17 Receiving Road', shipping)
        destination = self.env['res.partner'].create({
            'name': 'PO QA Drop Ship Contact', 'street': '29 Customer Road',
            'phone': '+421333444555', 'email': 'drop@example.invalid',
        })
        order.dest_address_id = destination
        shipping = self._html(order).xpath('//*[@name="barani_po_shipping"]')[0].text_content()
        for marker in ('PO QA Drop Ship Contact', '29 Customer Road', 'drop@example.invalid'):
            self.assertIn(marker, shipping)
        self.assertNotIn('17 Receiving Road', shipping)

    def test_sections_notes_incoterms_and_internal_note(self):
        order = self._order()
        order.order_line.sequence = 10
        for sequence, kind, name in [(1, 'line_section', 'PUBLIC SECTION'),
                                    (2, 'line_subsection', 'PUBLIC SUBSECTION'),
                                    (3, 'line_note', 'PUBLIC LINE NOTE')]:
            self.env['purchase.order.line'].create({
                'order_id': order.id, 'sequence': sequence, 'display_type': kind, 'name': name,
            })
        order.write({'note': '<p>PUBLIC SUPPLIER TERMS</p>',
                     'incoterm_id': self.env.ref('account.incoterm_EXW').id,
                     'incoterm_location': 'SUPPLIER LOADING BAY'})
        if 'x_studio_internal_note' in order._fields:
            order.x_studio_internal_note = 'PRIVATE INTERNAL NOTE — DO NOT PRINT'
        document = self._html(order)
        text = document.text_content()
        for marker in ('PUBLIC SECTION', 'PUBLIC SUBSECTION', 'PUBLIC LINE NOTE',
                       'PUBLIC SUPPLIER TERMS', 'SUPPLIER LOADING BAY'):
            self.assertIn(marker, text)
        self.assertNotIn('PRIVATE INTERNAL NOTE', text)
        self.assertEqual(len(document.xpath('//tr[@name="barani_po_product_line"]')), 1)
        self.assertEqual(len(document.xpath('//td[@colspan="10"]')), 5)

    def test_order_company_is_used_in_batch(self):
        order = self._order()
        other_company = self.env['res.company'].sudo().create({
            'name': 'PO QA SECOND COMPANY', 'currency_id': self.env.ref('base.EUR').id,
        })
        self.env.user.sudo().write({'company_ids': [Command.link(other_company.id)]})
        other_company.external_report_layout_id = self.env.ref('web.external_layout_standard')
        other_warehouse = self.env['stock.warehouse'].sudo().search([('company_id', '=', other_company.id)], limit=1)
        if not other_warehouse:
            other_warehouse = self.env['stock.warehouse'].sudo().create({
                'name': 'PO QA Second Warehouse', 'code': 'BPS', 'company_id': other_company.id,
            })
        other_order = self.env['purchase.order'].with_company(other_company).create({
            'name': 'PO-QA-002', 'partner_id': self.partner_a.id,
            'company_id': other_company.id, 'picking_type_id': other_warehouse.in_type_id.id,
        })
        document = self._html(order | other_order)
        articles = document.xpath('//div[contains(concat(" ", normalize-space(@class), " "), " article ")]')
        headers = document.xpath('//*[@name="barani_purchase_company_address"]')
        self.assertEqual([a.get('data-oe-id') for a in articles], [str(order.id), str(other_order.id)])
        self.assertIn(order.company_id.name, headers[0].text_content())
        self.assertIn(other_company.name, headers[1].text_content())

    def test_real_pdf_short_and_multipage(self):
        order = self._order()
        order.write({'state': 'purchase', 'date_approve': '2026-09-15 12:00:00'})
        self._pdf(order, 'purchase_short', 1)
        order.write({'order_line': [Command.create({
            'product_id': self.product_a.id,
            'name': 'LONG PO LINE %02d — description with enough detail to wrap on the page' % index,
            'product_qty': index + 1, 'product_uom_id': self.uom_unit.id,
            'price_unit': 12.3456, 'date_planned': '2026-09-20 12:00:00',
            'tax_ids': [Command.set(self.tax_23.ids)],
        }) for index in range(65)]})
        self._pdf(order, 'purchase_multipage', 2)

    def test_uninstall_restores_saved_action_and_foreign_route_is_protected(self):
        admin_env = self.env['ir.actions.report'].sudo().env
        report = admin_env.ref(ACTION).with_context(lang=None)
        backup = json.loads(admin_env.ref(BACKUP_XMLID).value)
        current = {field: report[field] for field in ('report_name', 'report_file', 'print_report_name')}
        current['paperformat_id'] = report.paperformat_id.id
        uninstall_hook(admin_env)
        for field, expected in backup['values'].items():
            actual = report[field].id or False if field == 'paperformat_id' else report[field]
            self.assertEqual(actual, expected)
        report.write(current)
        report.report_name = 'other_module.custom_purchase_report'
        uninstall_hook(admin_env)
        self.assertEqual(report.report_name, 'other_module.custom_purchase_report')
        with self.assertRaises(UserError):
            pre_init_hook(admin_env)

    def test_english_labels_with_slovak_supplier_language(self):
        self.env['res.lang'].sudo()._activate_lang('sk_SK')
        order = self._order()
        order.partner_id.lang = 'sk_SK'
        document = self._html(order)
        self.assertIn('Supplier:', document.text_content())
        self.assertIn('Delivery address:', document.text_content())
        self.assertIn('Prepared by:', document.text_content())
        self.assertEqual(document.xpath('//*[@data-oe-model="purchase.order"]')[0].get('data-oe-lang'), 'en_US')

    def test_structured_company_header_does_not_repeat_freeform_details(self):
        order = self._order()
        order.company_id.sudo().company_details = '<p>LEGACY DUPLICATE VAT HEADER</p>'
        document = self._html(order)
        self.assertNotIn('LEGACY DUPLICATE VAT HEADER', document.text_content())
        registration = document.xpath('//*[@name="barani_purchase_company_registration"]')[0].text_content()
        if order.company_id.vat:
            self.assertEqual(registration.count(order.company_id.vat), 1)
