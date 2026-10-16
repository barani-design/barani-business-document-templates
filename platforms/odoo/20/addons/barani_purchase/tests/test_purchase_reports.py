"""Real Odoo ORM/QWeb/PDF tests. Run on a development/test database only."""
import io
import json
import os
import re
from pathlib import Path
from unittest.mock import patch

from lxml import etree, html

from odoo import Command
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.exceptions import UserError
from odoo.modules.module import load_script
from odoo.tests import tagged
from odoo.tools.pdf import PdfFileReader
from odoo.tools.safe_eval import safe_eval

from ..hooks import (
    ACTION, BACKUP_XMLID, ROUTE, RFQ_ACTION, RFQ_BACKUP_XMLID, RFQ_ROUTE,
    backup_rfq_action, pre_init_hook, uninstall_hook,
)


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

    def _order(self, name='PO-QA-001', partner=None):
        return self.env['purchase.order'].create({
            'name': name, 'partner_id': (partner or self.partner_a).id,
            'company_id': self.env.company.id, 'currency_id': self.env.ref('base.EUR').id,
            'picking_type_id': self.warehouse.in_type_id.id,
            'date_order': '2026-09-15 12:00:00',
            'payment_term_id': self.pay_terms_a.id,
            'order_line': [Command.create({
                'product_id': self.product_a.id, 'name': 'PRECISION NUT M5',
                'product_qty': 1000, 'uom_id': self.uom_unit.id,
                'price_unit': 0.0119, 'date_planned': '2026-09-17 12:00:00',
                'tax_ids': [Command.set(self.tax_23.ids)],
            })],
        })

    def _html(self, orders, report_action=ACTION):
        self.assertFalse(self.env.su, 'Render with ordinary test-user access rights')
        body, kind = self.env['ir.actions.report'].with_context(
            allowed_company_ids=orders.company_id.ids,
        )._render_qweb_html(report_action, orders.ids)
        self.assertEqual(kind, 'html')
        return html.fromstring(body)

    def _pdf(self, orders, label, minimum_pages, report_action=ACTION):
        # Let wkhtmltopdf's asset requests use the test cursor and release the
        # test HTTP lock while the real renderer runs (Odoo 19 test helper).
        with self.allow_pdf_render():
            body, kind = self.env['ir.actions.report'].with_context(
                force_report_rendering=True, report_pdf_no_attachment=True,
            )._render_qweb_pdf(report_action, orders.ids)
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
        self.assertNotIn('report_file', report._fields)  # Removed in Odoo 20.
        self.assertEqual(report.paperformat_id, self.env.ref('barani_purchase.paperformat_purchase'))
        self.assertFalse(report.attachment_use)
        self.assertEqual(self.env.ref('purchase.report_purchase_quotation').report_name,
                         RFQ_ROUTE)
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
            tax = self.tax_23.copy({
                'name': 'PO QA VAT 23% included' if included else 'PO QA VAT 23% excluded',
                'price_include_override': 'tax_included' if included else 'tax_excluded',
            })
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
                # Odoo 19 requires a quantity even for sections and notes.
                'product_qty': 0.0,
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
        self._pdf(order, 'rfq_short', 1, RFQ_ACTION)
        order.write({'state': 'purchase', 'date_approve': '2026-09-15 12:00:00'})
        self._pdf(order, 'purchase_short', 1)
        order.write({'order_line': [Command.create({
            'product_id': self.product_a.id,
            'name': 'LONG PO LINE %02d — description with enough detail to wrap on the page' % index,
            'product_qty': index + 1, 'uom_id': self.uom_unit.id,
            'price_unit': 12.3456, 'date_planned': '2026-09-20 12:00:00',
            'tax_ids': [Command.set(self.tax_23.ids)],
        }) for index in range(65)]})
        self._pdf(order, 'purchase_multipage', 2)
        self._pdf(order, 'rfq_multipage', 2, RFQ_ACTION)

    def test_rfq_button_routing_and_unpriced_content(self):
        order = self._order()
        report = self.env.ref(RFQ_ACTION)
        # Odoo 20 removed print_quotation(): the form's Print button runs the
        # RFQ report action directly and leaves the state unchanged.
        self.assertFalse(hasattr(order, 'print_quotation'))
        form = etree.fromstring(self.env.ref('purchase.purchase_order_form').sudo().arch)
        self.assertTrue(form.xpath('//button[@type="action"][@name="%d"]' % report.id))
        self.assertEqual(report.report_action(order)['report_name'], RFQ_ROUTE)
        self.assertEqual(order.state, 'draft')  # Keep Odoo's native Print RFQ behavior.
        self.assertEqual(report.paperformat_id, self.env.ref('barani_purchase.paperformat_purchase'))
        self.assertFalse(report.attachment_use)
        self.assertEqual(safe_eval(report.print_report_name, {'object': order}),
                         'PO-QA-001 - Request for Quotation')
        for state in ('draft', 'sent', 'to approve', 'purchase', 'cancel'):
            order.state = state
            document = self._html(order, RFQ_ACTION)
            self.assertEqual(order.state, state, 'Rendering must not change the document state')
            self.assertEqual(document.xpath('//*[@name="barani_purchase_title"]')[0].text_content(),
                             'Request for Quotation')
            self.assertEqual([h.text_content().strip() for h in document.xpath(
                '//table[@name="barani_rfq_lines"]/thead/tr/th')],
                ['Description', 'Expected Date', 'Qty', 'Unit'])
            self.assertFalse(document.xpath('//*[@name="barani_po_tax_totals"]'))
            self.assertFalse(document.xpath('//*[@name="td_priceunit" or @name="td_vatbase"]'))
            self.assertIn('17 Sep 2026', document.text_content())
            self.assertIn('PO QA Supplier', document.text_content())
            self.assertIn('17 Receiving Road', document.text_content())
            self.assertNotIn('0.0119', document.text_content())
            self.assertNotIn('14.64', document.text_content())

    def test_rfq_sections_notes_and_internal_note(self):
        order = self._order()
        order.order_line.sequence = 10
        for sequence, kind, name in [(1, 'line_section', 'RFQ SECTION'),
                                    (2, 'line_subsection', 'RFQ SUBSECTION'),
                                    (3, 'line_note', 'RFQ PUBLIC NOTE')]:
            self.env['purchase.order.line'].create({
                'order_id': order.id, 'sequence': sequence, 'display_type': kind,
                'name': name, 'product_qty': 0.0,
            })
        order.note = '<p>RFQ SUPPLIER TERMS</p>'
        if 'x_studio_internal_note' in order._fields:
            order.x_studio_internal_note = 'RFQ PRIVATE NOTE'
        document = self._html(order, RFQ_ACTION)
        for marker in ('RFQ SECTION', 'RFQ SUBSECTION', 'RFQ PUBLIC NOTE', 'RFQ SUPPLIER TERMS'):
            self.assertIn(marker, document.text_content())
        self.assertNotIn('RFQ PRIVATE NOTE', document.text_content())
        self.assertEqual(len(document.xpath('//td[@colspan="4"]')), 3)
        self.assertEqual(len(document.xpath('//tr[@name="barani_rfq_product_line"]')), 1)

    def test_rfq_upgrade_backup_restore_and_foreign_route(self):
        admin_env = self.env['ir.actions.report'].sudo().env
        report = admin_env.ref(RFQ_ACTION).with_context(lang=None)
        po_backup = admin_env.ref(BACKUP_XMLID).value
        rfq_snapshot = json.loads(admin_env.ref(RFQ_BACKUP_XMLID).value)
        self.assertEqual(rfq_snapshot['values']['report_name'], 'purchase.report_purchasequotation')
        current = {field: report[field] for field in ('report_name', 'print_report_name')}
        current['paperformat_id'] = report.paperformat_id.id
        # Simulate the installed 19.0.1.0.0 database, where RFQ was untouched.
        report.write(rfq_snapshot['values'])
        report.print_report_name = "'Existing RFQ - ' + object.name"
        expected = dict(rfq_snapshot['values'], print_report_name=report.print_report_name)
        backup = admin_env.ref(RFQ_BACKUP_XMLID)
        admin_env['ir.model.data'].search([
            ('module', '=', 'barani_purchase'), ('name', '=', 'original_rfq_report_action'),
        ]).unlink()
        backup.unlink()
        migration = load_script(str(Path(__file__).resolve().parents[1] /
            'migrations' / '19.0.1.0.1' / 'pre-10-backup-rfq-action.py'),
            'barani_purchase_test_rfq_upgrade')
        migration.migrate(self.env.cr, '19.0.1.0.0')
        self.assertEqual(admin_env.ref(BACKUP_XMLID).value, po_backup)
        self.assertEqual(json.loads(admin_env.ref(RFQ_BACKUP_XMLID).value)['values'], expected)
        report.write(current)  # The upgrade's report-action XML applies this route.
        uninstall_hook(admin_env)
        for field, value in expected.items():
            actual = report[field].id or False if field == 'paperformat_id' else report[field]
            self.assertEqual(actual, value)
        report.report_name = 'other_module.custom_rfq_report'
        uninstall_hook(admin_env)
        self.assertEqual(report.report_name, 'other_module.custom_rfq_report')
        with self.assertRaises(UserError):
            backup_rfq_action(admin_env)

    def test_uninstall_restores_saved_action_and_foreign_route_is_protected(self):
        admin_env = self.env['ir.actions.report'].sudo().env
        report = admin_env.ref(ACTION).with_context(lang=None)
        backup = json.loads(admin_env.ref(BACKUP_XMLID).value)
        current = {field: report[field] for field in ('report_name', 'print_report_name')}
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

    # ------------------------------------------------------------------
    # Odoo 20 compatibility cases (real records and production actions).
    # ------------------------------------------------------------------
    def _line_descriptions(self, document, cell='td_description'):
        # The text widget renders newlines as <br>, which text_content() drops.
        return [span.text_content() for span in document.xpath('//td[@name="%s"]/span[1]' % cell)]

    def test_legacy_backup_report_file_is_dropped_and_other_keys_fail(self):
        admin_env = self.env['ir.actions.report'].sudo().env
        report = admin_env.ref(ACTION).with_context(lang=None)
        backup = admin_env.ref(BACKUP_XMLID)
        snapshot = json.loads(backup.value)
        self.assertEqual(set(snapshot['values']), {'report_name', 'paperformat_id', 'print_report_name'})
        current = {field: report[field] for field in ('report_name', 'print_report_name')}
        current['paperformat_id'] = report.paperformat_id.id
        # Backups saved by the Odoo 19 releases also hold report_file.
        backup.value = json.dumps(dict(snapshot, values=dict(
            snapshot['values'], report_file='purchase.report_purchaseorder')))
        uninstall_hook(admin_env)
        for field, expected in snapshot['values'].items():
            actual = report[field].id or False if field == 'paperformat_id' else report[field]
            self.assertEqual(actual, expected)
        self.assertNotIn('report_file', report._fields)
        report.write(current)
        unexpected = dict(snapshot['values'], name='Unexpected action name')
        missing = {key: value for key, value in snapshot['values'].items() if key != 'print_report_name'}
        for values in (unexpected, missing):
            backup.value = json.dumps(dict(snapshot, values=values))
            with self.assertRaises(UserError):
                uninstall_hook(admin_env)
            self.assertEqual(report.report_name, ROUTE)
            self.assertEqual(report.print_report_name, current['print_report_name'])

    def test_registration_identifiers_are_stored_en_only(self):
        company_partner = self.env.company.partner_id.sudo()
        company_ids = {'OTHER': 'COOTHER7', 'SK_EN': '35742968', 'EAN_GLN': '9780471117094'}
        company_partner.write({'additional_identifiers': company_ids})
        self.assertEqual(company_partner.additional_identifiers, company_ids)
        supplier = self.env['res.partner'].create({
            'name': 'PO QA Registered Supplier', 'is_company': True, 'street': '5 Registry Road',
            'additional_identifiers': {'OTHER': 'SUPEN1'},
        })
        contact = self.env['res.partner'].create({'name': 'PO QA Buyer Contact', 'parent_id': supplier.id})
        order = self._order(partner=contact)
        for report_action in (ACTION, RFQ_ACTION):
            document = self._html(order, report_action)
            # Native labels, ordered by native sequence (SK_EN 10, OTHER 1000).
            self.assertEqual(
                [e.text_content() for e in document.xpath('//*[@name="barani_purchase_company_identifier"]')],
                ['Company ID: 35742968', 'Company ID: COOTHER7'])
            registration = document.xpath('//*[@name="barani_purchase_company_registration"]')[0].text_content()
            self.assertNotIn('9780471117094', registration)  # GLN is not an EN identifier.
            self.assertEqual(
                [e.text_content() for e in document.xpath('//*[@name="barani_po_supplier_identifier"]')],
                ['Company ID: SUPEN1'])
        # No VAT fallback: VAT stays on its own line and is never printed as an ID.
        supplier.with_context(no_vat_validation=True).write({'additional_identifiers': {}, 'vat': 'SK2022749619'})
        document = self._html(order)
        self.assertFalse(document.xpath('//*[@name="barani_po_supplier_identifier"]'))
        supplier_block = document.xpath('//*[@name="barani_po_supplier"]')[0].text_content()
        self.assertEqual(supplier_block.count('SK2022749619'), 1)
        self.assertIn('VAT: SK2022749619', supplier_block)

    def test_native_product_labels_new_vendor_edited_and_historical(self):
        product = self.product_a
        product.description_purchase = 'PURCHASE DESCRIPTION A'
        order = self._order()
        line = self.env['purchase.order.line'].create({
            'order_id': order.id, 'product_id': product.id, 'product_qty': 2,
        })
        # New Odoo 20 lines store only the description; label adds the product.
        self.assertEqual(line.name, 'PURCHASE DESCRIPTION A')
        self.assertEqual(line.label, product.display_name + '\nPURCHASE DESCRIPTION A')
        for report_action, cell in ((ACTION, 'td_description'), (RFQ_ACTION, 'td_rfq_description')):
            descriptions = self._line_descriptions(self._html(order, report_action), cell)
            self.assertEqual(descriptions, [product.display_name + 'PRECISION NUT M5',
                                            product.display_name + 'PURCHASE DESCRIPTION A'])
        # Supplier-specific product name and code come from the vendor price list.
        self.env['product.supplierinfo'].create({
            'partner_id': self.partner_a.id, 'product_tmpl_id': product.product_tmpl_id.id,
            'product_name': 'VENDOR NUT', 'product_code': 'VEND-77', 'price': 1.0,
            'company_id': order.company_id.id,
        })
        descriptions = self._line_descriptions(self._html(order))
        self.assertEqual(descriptions[1], '[VEND-77] VENDOR NUTPURCHASE DESCRIPTION A')
        # An edited description keeps the product name in front of it.
        line.name = 'EDITED DESCRIPTION'
        descriptions = self._line_descriptions(self._html(order))
        self.assertEqual(descriptions[1], '[VEND-77] VENDOR NUTEDITED DESCRIPTION')
        # Historical Odoo 19 lines already start with the product name: printed once.
        line.name = line._get_product_display_name() + '\nLEGACY 19 DESCRIPTION'
        self.assertEqual(line.label, line.name)
        for report_action, cell in ((ACTION, 'td_description'), (RFQ_ACTION, 'td_rfq_description')):
            descriptions = self._line_descriptions(self._html(order, report_action), cell)
            self.assertEqual(descriptions[1], '[VEND-77] VENDOR NUTLEGACY 19 DESCRIPTION')
            self.assertEqual(descriptions[1].count('VEND-77'), 1)

    def test_rfq_portal_edi_link(self):
        order = self._order()
        self.env['res.users'].sudo().create({
            'name': 'PO QA Portal Supplier', 'login': 'po_qa_portal_supplier',
            'partner_id': self.partner_a.id,
            'group_ids': [Command.set([self.env.ref('base.group_portal').id])],
        })
        self.assertTrue(any(user._is_portal() for user in self.partner_a.user_ids))
        if not order._get_edi_builders():
            self.assertNotIn('Connect your software', self._html(order, RFQ_ACTION).text_content())
        # EDI builders come from optional modules; emulate one being available.
        with patch.object(type(self.env['purchase.order']), '_get_edi_builders', return_value=['edi']):
            document = self._html(order, RFQ_ACTION)
        base_url = self.env['ir.config_parameter'].sudo().get_str('web.base.url')
        self.assertEqual(
            [a.get('href') for a in document.xpath('//a[contains(@href, "portal_connect_software_modal")]')],
            [base_url + '/my/purchase/%d#portal_connect_software_modal' % order.id])
        self.assertIn('to create quotes automatically', document.text_content())
        self.assertIn(order.company_id.name, document.text_content())

    def test_batch_company_identifiers_and_supplier_language_isolation(self):
        self.env['res.lang'].sudo()._activate_lang('sk_SK')
        product = self.product_b
        product.product_tmpl_id.with_context(lang='sk_SK').name = 'SK PRODUKT B'
        self.env.company.partner_id.sudo().write({'additional_identifiers': {'OTHER': 'COAEN1'}})
        slovak_supplier = self.env['res.partner'].create({'name': 'PO QA Slovak Supplier', 'lang': 'sk_SK'})
        english_supplier = self.env['res.partner'].create({'name': 'PO QA English Supplier', 'lang': 'en_US'})
        order = self._order(partner=slovak_supplier)
        self.env['purchase.order.line'].create({'order_id': order.id, 'product_id': product.id, 'product_qty': 1})
        other_company = self.env['res.company'].sudo().create({
            'name': 'PO QA ISOLATED COMPANY', 'currency_id': self.env.ref('base.EUR').id,
        })
        other_company.partner_id.sudo().write({'additional_identifiers': {'OTHER': 'COBEN2'}})
        self.env.user.sudo().write({'company_ids': [Command.link(other_company.id)]})
        other_company.external_report_layout_id = self.env.ref('web.external_layout_standard')
        other_warehouse = self.env['stock.warehouse'].sudo().search([('company_id', '=', other_company.id)], limit=1)
        if not other_warehouse:
            other_warehouse = self.env['stock.warehouse'].sudo().create({
                'name': 'PO QA Isolated Warehouse', 'code': 'BPI', 'company_id': other_company.id,
            })
        other_order = self.env['purchase.order'].with_company(other_company).create({
            'name': 'PO-QA-ISO', 'partner_id': english_supplier.id, 'company_id': other_company.id,
            'picking_type_id': other_warehouse.in_type_id.id,
        })
        self.env['purchase.order.line'].with_company(other_company).create({
            'order_id': other_order.id, 'product_id': product.id, 'product_qty': 1,
        })
        document = self._html(order | other_order)
        articles = document.xpath('//div[contains(concat(" ", normalize-space(@class), " "), " article ")]')
        self.assertEqual([a.get('data-oe-lang') for a in articles], ['en_US', 'en_US'])
        registrations = [e.text_content() for e in document.xpath('//*[@name="barani_purchase_company_registration"]')]
        self.assertIn('COAEN1', registrations[0])
        self.assertNotIn('COBEN2', registrations[0])
        self.assertIn('COBEN2', registrations[1])
        self.assertNotIn('COAEN1', registrations[1])
        # English report wording; product wording follows each supplier's language.
        self.assertEqual(document.text_content().count('Supplier:'), 2)
        descriptions = self._line_descriptions(document)
        self.assertIn('SK PRODUKT B', descriptions[1])
        self.assertIn('product_b', descriptions[2])
        self.assertNotIn('SK PRODUKT B', descriptions[2])

    # ------------------------------------------------------------------
    # Native document-level tax mode (purchase.order.document_tax_mode).
    # The tax used here has no price_include_override, so only the
    # document mode decides whether prices include VAT.
    # ------------------------------------------------------------------
    def _document_mode_order(self, mode, rounding, lines):
        self.assertFalse(self.tax_23.price_include_override)
        self.assertEqual(self.tax_23._is_price_included(mode), mode == 'tax_included')
        order = self._order(name='PO-QA-%s-%s-%d' % (mode, rounding, len(lines)))
        order.company_id.tax_calculation_rounding_method = rounding
        order.document_tax_mode = mode
        order.order_line.write(dict(lines[0], tax_ids=[Command.set(self.tax_23.ids)]))
        for values in lines[1:]:
            self.env['purchase.order.line'].create(dict(
                values, order_id=order.id, product_id=self.product_a.id, uom_id=self.uom_unit.id,
                date_planned='2026-09-17 12:00:00', tax_ids=[Command.set(self.tax_23.ids)]))
        self.assertEqual(order.document_tax_mode, mode)
        self.assertEqual(set(order.order_line.mapped('document_tax_mode')), {mode})
        self.assertEqual(order.order_line.tax_ids, self.tax_23)
        return order

    def _amounts(self, element):
        # en_US rendering: ',' groups thousands, '.' is the decimal separator.
        text = element.text_content().replace('\xa0', ' ')
        return [float(value.replace(',', '')) for value in re.findall(r'-?\d[\d,]*(?:\.\d+)?', text)]

    def _assert_amounts(self, element, expected):
        rendered = self._amounts(element)
        self.assertEqual(len(rendered), len(expected), rendered)
        for actual, value in zip(rendered, expected):
            self.assertAlmostEqual(actual, value, places=6)

    def _assert_amount_rendered(self, element, value):
        rendered = self._amounts(element)
        self.assertTrue(any(abs(actual - value) < 0.000001 for actual in rendered), (value, rendered))

    def _assert_po_matches_native(self, document, order):
        currency = order.currency_id
        rows = document.xpath('//tr[@name="barani_po_product_line"]')
        lines = order.order_line.filtered(lambda line: not line.display_type)
        self.assertEqual(len(rows), len(lines))
        for row, line in zip(rows, lines):
            cells = {cell.get('name'): cell for cell in row.xpath('./td[@name]')}
            self._assert_amounts(cells['td_priceunit'], [line.price_unit])
            self._assert_amounts(cells['td_discount'], [line.discount])
            self._assert_amounts(cells['td_vatrate'], [self.tax_23.amount])
            self._assert_amounts(cells['td_vatamount'], [currency.round(line.price_total - line.price_subtotal)])
            self._assert_amounts(cells['td_vatbase'], [currency.round(line.price_subtotal)])
        totals = document.xpath('//*[@name="barani_po_tax_totals"]')[0]
        summary = order.tax_totals
        for native_value, field_value in ((summary['base_amount_currency'], order.amount_untaxed),
                                          (summary['tax_amount_currency'], order.amount_tax),
                                          (summary['total_amount_currency'], order.amount_total)):
            self.assertFalse(currency.compare_amounts(native_value, field_value))
            self._assert_amount_rendered(totals, currency.round(field_value))
        rounding_note = "Tax totals follow Odoo's document rounding" in document.text_content()
        line_tax_sum = sum(lines.mapped('price_tax'))
        self.assertEqual(rounding_note, bool(currency.compare_amounts(line_tax_sum, order.amount_tax)))

    def _assert_rfq_unpriced(self, order, forbidden):
        document = self._html(order, RFQ_ACTION)
        self.assertEqual([h.text_content().strip() for h in document.xpath(
            '//table[@name="barani_rfq_lines"]/thead/tr/th')], ['Description', 'Expected Date', 'Qty', 'Unit'])
        self.assertFalse(document.xpath('//table[@name="barani_po_lines"]'))
        self.assertFalse(document.xpath('//*[@name="barani_po_tax_totals"]'))
        self.assertFalse(document.xpath('//*[@name="td_priceunit" or @name="td_discount" or @name="td_vatrate"'
                                        ' or @name="td_vatamount" or @name="td_vatbase"]'))
        text = document.text_content()
        for heading in ('Unit Price', 'Disc.', 'VAT Rate', 'VAT Base', 'Untaxed Amount'):
            self.assertNotIn(heading, text)
        for amount in forbidden:
            self.assertNotIn(amount, text)
        self.assertEqual(len(document.xpath('//tr[@name="barani_rfq_product_line"]')),
                         len(order.order_line.filtered(lambda line: not line.display_type)))

    def test_document_tax_mode_discount_and_global_rounding(self):
        # Agreed fixture: 3 x 12.30, 10 % discount, 23 % VAT.
        expected = {'tax_excluded': (33.21, 7.64, 40.85), 'tax_included': (27.00, 6.21, 33.21)}
        for mode, (untaxed, tax, total) in expected.items():
            for rounding in ('round_globally', 'round_per_line'):
                order = self._document_mode_order(mode, rounding, [
                    {'product_qty': 3, 'price_unit': 12.30, 'discount': 10}])
                line = order.order_line
                self.assertAlmostEqual(line.price_unit, 12.30)
                self.assertAlmostEqual(line.price_subtotal, untaxed)
                self.assertAlmostEqual(line.price_total, total)
                self.assertAlmostEqual(order.amount_untaxed, untaxed)
                self.assertAlmostEqual(order.amount_tax, tax)
                self.assertAlmostEqual(order.amount_total, total)
                document = self._html(order)
                self._assert_po_matches_native(document, order)
                self.assertIn('12.30', document.xpath('//*[@name="td_priceunit"]')[0].text_content())
                self.assertIn('10.00', document.xpath('//*[@name="td_discount"]')[0].text_content())
                self.assertIn('%.2f' % untaxed, document.xpath('//*[@name="td_vatbase"]')[0].text_content())
                self.assertIn('%.2f' % tax, document.xpath('//*[@name="td_vatamount"]')[0].text_content())
                self.assertIn('%.2f' % total,
                              document.xpath('//*[@name="barani_po_tax_totals"]')[0].text_content())
                self._assert_rfq_unpriced(order, ('12.30', '%.2f' % untaxed, '%.2f' % tax, '%.2f' % total))

    def test_document_tax_mode_global_rounding_differs_from_per_line(self):
        # Two lines of 0.07 at 23 %: line VAT (0.0161 excluded, 0.01309
        # included) is rounded per line, or its document sum once globally.
        expected = {
            ('tax_excluded', 'round_per_line'): (0.14, 0.04, 0.18),
            ('tax_excluded', 'round_globally'): (0.14, 0.03, 0.17),
            ('tax_included', 'round_per_line'): (0.12, 0.02, 0.14),
            ('tax_included', 'round_globally'): (0.11, 0.03, 0.14),
        }
        for (mode, rounding), (untaxed, tax, total) in expected.items():
            order = self._document_mode_order(mode, rounding, [
                {'product_qty': 1, 'price_unit': 0.07, 'discount': 0},
                {'product_qty': 1, 'price_unit': 0.07, 'discount': 0, 'name': 'SECOND ROUNDING LINE'}])
            self.assertEqual(len(order.order_line), 2)
            self.assertAlmostEqual(order.amount_untaxed, untaxed)
            self.assertAlmostEqual(order.amount_tax, tax)
            self.assertAlmostEqual(order.amount_total, total)
            document = self._html(order)
            self._assert_po_matches_native(document, order)
            self.assertIn('%.2f' % total, document.xpath('//*[@name="barani_po_tax_totals"]')[0].text_content())
            self._assert_rfq_unpriced(order, ('0.07', '%.2f' % untaxed, '%.2f' % tax, '%.2f' % total))

    def test_document_tax_mode_unit_price_precision_0119(self):
        expected = {'tax_excluded': (11.90, 2.74, 14.64), 'tax_included': (9.67, 2.23, 11.90)}
        for mode, (untaxed, tax, total) in expected.items():
            order = self._document_mode_order(mode, 'round_globally', [
                {'product_qty': 1000, 'price_unit': 0.0119, 'discount': 0}])
            self.assertAlmostEqual(order.order_line.price_unit, 0.0119)
            self.assertAlmostEqual(order.amount_untaxed, untaxed)
            self.assertAlmostEqual(order.amount_tax, tax)
            self.assertAlmostEqual(order.amount_total, total)
            document = self._html(order)
            self._assert_po_matches_native(document, order)
            self.assertIn('0.0119', document.xpath('//*[@name="td_priceunit"]')[0].text_content())
            self.assertIn('%.2f' % total, document.xpath('//*[@name="barani_po_tax_totals"]')[0].text_content())
            self._assert_rfq_unpriced(order, ('0.0119', '%.2f' % untaxed, '%.2f' % tax, '%.2f' % total))

    def test_tax_override_takes_precedence_over_document_mode(self):
        # Native _is_price_included: an explicit tax override wins over the
        # document mode. Same fixture as the document-mode case, crossed.
        for mode, override, untaxed, total in (('tax_included', 'tax_excluded', 33.21, 40.85),
                                               ('tax_excluded', 'tax_included', 27.00, 33.21)):
            tax = self.tax_23.copy({'name': 'PO QA VAT 23% override ' + override,
                                    'price_include_override': override})
            self.assertEqual(tax._is_price_included(mode), override == 'tax_included')
            order = self._order(name='PO-QA-OVERRIDE-' + mode)
            order.company_id.tax_calculation_rounding_method = 'round_globally'
            order.document_tax_mode = mode
            order.order_line.write({'product_qty': 3, 'price_unit': 12.30, 'discount': 10,
                                    'tax_ids': [Command.set(tax.ids)]})
            self.assertEqual(order.order_line.document_tax_mode, mode)
            self.assertAlmostEqual(order.amount_untaxed, untaxed)
            self.assertAlmostEqual(order.amount_total, total)
            document = self._html(order)
            totals = document.xpath('//*[@name="barani_po_tax_totals"]')[0]
            self._assert_amount_rendered(totals, order.currency_id.round(order.amount_total))
            self.assertIn('%.2f' % total, totals.text_content())
            self._assert_amounts(document.xpath('//*[@name="td_vatbase"]')[0],
                                 [order.currency_id.round(order.order_line.price_subtotal)])
