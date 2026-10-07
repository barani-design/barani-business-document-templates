"""Real Odoo19 report actions and ORM fixtures; no mocked renderer."""
import base64
import hashlib
import io
import json
import logging
import os
from pathlib import Path

from lxml import html
from odoo import Command
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tools.safe_eval import safe_eval
from odoo.tools.pdf import PdfFileReader

_logger = logging.getLogger(__name__)
CONTRACTS = [('sale.action_report_saleorder', {'role': 'Quotation / Order primary', 'xmlid': 'sale.action_report_saleorder', 'label_en_US': 'Quotation / Order', 'label_languages': ['de_DE', 'en_US', 'sk_SK'], 'label_storage_md5': '519b09a6c40eaadae1f201984a1d2fde', 'model': 'sale.order', 'report_type': 'qweb-pdf', 'route': 'barani_commercial.report_saleorder', 'paperformat': 'BARANI Commercial A4 7mm', 'binding_model': 'sale.order', 'groups': [], 'binding_view_types': 'list,form', 'filename_expression': 'sale_numeric_first', 'filename_storage_md5': '24ce31cfe59eba20952a9fe697954012', 'attachment': None, 'filename': "(((object.name or '')[3:] if (object.name or '')[:3] in ('SO/','PF/') else (object.name or '')[2:] if (object.name or '')[:2] == 'Q/' else (object.name or ''))).replace('/', '_') + (' - Quotation' if object.state in ('draft','sent','cancel') else ' - Sales Order')", 'filename_key': 'sale_numeric_first'}), ('barani_commercial.action_report_saleorder_2026', {'role': 'Quotation / Order 2026+', 'xmlid': None, 'label_en_US': 'Quotation / Order — 2026+', 'label_languages': ['en_US'], 'label_storage_md5': 'f0c709e303d402a0b1e55cbd133547da', 'model': 'sale.order', 'report_type': 'qweb-pdf', 'route': 'barani_commercial.report_saleorder', 'paperformat': 'BARANI Commercial A4 7mm', 'binding_model': None, 'groups': ['sales_team.group_sale_salesman', 'sales_team.group_sale_salesman_all_leads', 'sales_team.group_sale_manager', 'account.group_account_invoice'], 'binding_view_types': 'list,form', 'filename_expression': 'sale_numeric_first', 'filename_storage_md5': 'f20633549b7b3968b89c7ff03c54a93f', 'attachment': None, 'filename': "(((object.name or '')[3:] if (object.name or '')[:3] in ('SO/','PF/') else (object.name or '')[2:] if (object.name or '')[:2] == 'Q/' else (object.name or ''))).replace('/', '_') + (' - Quotation' if object.state in ('draft','sent','cancel') else ' - Sales Order')", 'filename_key': 'sale_numeric_first'}), ('sale.action_report_pro_forma_invoice', {'role': 'Pro-Forma primary', 'xmlid': 'sale.action_report_pro_forma_invoice', 'label_en_US': 'PRO-FORMA Invoice', 'label_languages': ['de_DE', 'en_US', 'sk_SK'], 'label_storage_md5': '1246cb2879ea4917cb5df338e1a7fc0a', 'model': 'sale.order', 'report_type': 'qweb-pdf', 'route': 'barani_commercial.report_saleorder_proforma', 'paperformat': 'BARANI Commercial A4 7mm', 'binding_model': 'sale.order', 'groups': ['sale.group_proforma_sales'], 'binding_view_types': 'list,form', 'filename_expression': 'proforma_numeric_first', 'filename_storage_md5': 'cd32b0f098e74fa2387c356e9a1a969e', 'attachment': None, 'filename': "(((object.name or '')[3:] if (object.name or '')[:3] in ('SO/','PF/') else (object.name or '')[2:] if (object.name or '')[:2] == 'Q/' else (object.name or ''))).replace('/', '_') + ' - Pro-Forma Invoice'", 'filename_key': 'proforma_numeric_first'}), ('barani_commercial.action_report_proforma_2026', {'role': 'Pro-Forma 2026+', 'xmlid': None, 'label_en_US': 'PRO-FORMA — 2026+', 'label_languages': ['en_US'], 'label_storage_md5': '65320d935865acb78fbbd98793c1984b', 'model': 'sale.order', 'report_type': 'qweb-pdf', 'route': 'barani_commercial.report_saleorder_proforma', 'paperformat': 'BARANI Commercial A4 7mm', 'binding_model': None, 'groups': ['sales_team.group_sale_salesman', 'sales_team.group_sale_salesman_all_leads', 'sales_team.group_sale_manager', 'account.group_account_invoice'], 'binding_view_types': 'list,form', 'filename_expression': 'proforma_numeric_first', 'filename_storage_md5': 'ec9a83cb438c2a819ae3d871335eb496', 'attachment': None, 'filename': "(((object.name or '')[3:] if (object.name or '')[:3] in ('SO/','PF/') else (object.name or '')[2:] if (object.name or '')[:2] == 'Q/' else (object.name or ''))).replace('/', '_') + ' - Pro-Forma Invoice'", 'filename_key': 'proforma_numeric_first'})]


@tagged('post_install', '-at_install', 'barani_reports')
class TestBaraniCommercialRendering(AccountTestInvoicingCommon):

    @classmethod
    def get_default_groups(cls):
        # AccountTestInvoicingCommon does not grant Sales access.
        return (super().get_default_groups()
                | cls.env.ref('sales_team.group_sale_salesman')
                | cls.env.ref('sale.group_proforma_sales'))

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Make the isolated company ready for the ordinary Print action.
        cls.env.company.external_report_layout_id = cls.env.ref('web.external_layout_standard')

    def _capture(self, label, action, record, body, extension):
        folder = Path(os.environ.get('BARANI_REPORT_OUTPUT', '/tmp/barani_reports_runtime'))
        folder.mkdir(parents=True, exist_ok=True)
        filename = self.__class__.__name__ + '__' + self._testMethodName + '__' + label + '.' + extension
        path = folder / filename
        path.write_bytes(body)
        row = {'test': self.id(), 'case': label, 'action': action, 'record_ids': record.ids,
               'model': record._name, 'company_id': record.company_id.id,
               'environment_company_id': self.env.company.id, 'format': extension,
               'sha256': hashlib.sha256(body).hexdigest(), 'bytes': len(body),
               'database': self.env.cr.dbname, 'file': filename}
        path.with_suffix(path.suffix + '.json').write_text(json.dumps(row, sort_keys=True, indent=2) + '\n')
        _logger.info('BARANI_REPORT_OUTPUT %s', json.dumps(row, sort_keys=True))

    def _html(self, action, record, label):
        self.assertFalse(self.env.su, 'Report actions must run with the test user ACLs')
        report = self.env.ref(action)
        self.assertEqual(report.model, record._name)
        route = report.report_action(record)
        self.assertEqual(route['type'], 'ir.actions.report')
        self.assertEqual(route['context']['active_ids'], record.ids)
        self.assertEqual(route['report_name'], report.report_name)
        body, kind = self.env['ir.actions.report']._render_qweb_html(action, record.ids)
        self.assertEqual(kind, 'html')
        self.assertGreater(len(body), 500)
        self._capture(label, action, record, body, 'html')
        return html.fromstring(body)

    def _pdf(self, action, record, label, minimum_pages=1):
        self.assertFalse(self.env.su, 'PDF rendering must run with the test user ACLs')
        body, kind = self.env['ir.actions.report'].with_context(
            force_report_rendering=True, report_pdf_no_attachment=True,
        )._render_qweb_pdf(action, record.ids)
        self.assertEqual(kind, 'pdf', 'HTML fallback is not PDF acceptance')
        self.assertTrue(body.startswith(b'%PDF-'))
        pdf = PdfFileReader(io.BytesIO(body))
        self.assertGreaterEqual(len(pdf.pages), minimum_pages)
        for page in pdf.pages:
            self.assertAlmostEqual(float(page.mediabox.width), 595.28, delta=2)
            self.assertAlmostEqual(float(page.mediabox.height), 841.89, delta=2)
        self._capture(label, action, record, body, 'pdf')

    def test_action_metadata_and_idempotence(self):
        reports = self.env['ir.actions.report']
        before = (reports.search_count([]), self.env['report.paperformat'].search_count([]))
        reports._barani_commercial_adopt_metadata()
        reports._barani_commercial_adopt_metadata()
        self.assertEqual(before, (reports.search_count([]), self.env['report.paperformat'].search_count([])))
        for xmlid, contract in CONTRACTS:
            report = self.env.ref(xmlid)
            self.assertEqual(report.with_context(lang='en_US').name, contract['label_en_US'])
            self.assertEqual(report.report_name, contract['route'])
            self.assertEqual(report.report_file, contract['route'])
            self.assertEqual(report.model, contract['model'])
            self.assertEqual(report.report_type, contract['report_type'])
            self.assertEqual(report.print_report_name, contract['filename'])
            self.assertEqual(report.binding_model_id.model or None, contract['binding_model'])
            self.assertEqual(report.binding_view_types, contract['binding_view_types'])
            self.assertEqual(set(report.group_ids.ids), {self.env.ref(g).id for g in contract['groups']})
            self.assertEqual(report.paperformat_id.name, contract['paperformat'])
            self.assertEqual(report.paperformat_id.format, 'A4')
            for field, value in [('margin_top', 40), ('margin_bottom', 18), ('margin_left', 7),
                                 ('margin_right', 7), ('header_spacing', 35), ('dpi', 90)]:
                self.assertEqual(report.paperformat_id[field], value)

    def test_metadata_collision_stops(self):
        report = self.env.ref(CONTRACTS[0][0])
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            report.paperformat_id.copy({'name': report.paperformat_id.name})
            self.env['ir.actions.report']._barani_commercial_adopt_metadata()

    def _order(self):
        self.partner_a.write({'name': 'REPORT CUSTOMER', 'street': '1 Test Street',
                              'city': 'Bratislava', 'zip': '83101', 'phone': False, 'email': False})
        order = self.env['sale.order'].create({
            'name': 'Q/260901', 'partner_id': self.partner_a.id,
            'partner_invoice_id': self.partner_a.id, 'partner_shipping_id': self.partner_a.id,
            'order_line': [Command.create({'product_id': self.product_a.id,
                'name': 'REPORT PRODUCT', 'product_uom_qty': 2, 'product_uom_id': self.uom_unit.id,
                'price_unit': 125, 'discount': 10,
                'tax_ids': [Command.set(self.tax_sale_a.ids)]})],
        })
        return order

    def test_quotation_order_and_proforma_all_actions(self):
        order = self._order()
        for state in ('draft', 'sale'):
            if state == 'sale':
                order.action_confirm()
            for xmlid, contract in CONTRACTS:
                doc = self._html(xmlid, order, state + '_' + xmlid.split('.')[-1])
                text = doc.text_content()
                title = 'Pro-Forma Invoice' if 'proforma' in contract['filename_key'] else ('Quotation' if state == 'draft' else 'Sales Order')
                self.assertIn(title, text)
                self.assertIn('REPORT PRODUCT', text)
                self.assertIn('260901', text)
                self.assertIn('MISSING TEL', text)
                self.assertIn('MISSING EMAIL', text)
                self.assertIn('260901 - ', safe_eval(contract['filename'], {'object': order}))
                self.assertEqual(len(doc.xpath('//td[@name="td_unit"]')), 1)

    def test_sections_subsections_notes_discount_and_taxes(self):
        order = self._order()
        for sequence, kind, name in [(1, 'line_section', 'SECTION MARKER'),
                                      (2, 'line_subsection', 'SUBSECTION MARKER'),
                                      (3, 'line_note', 'NOTE MARKER')]:
            self.env['sale.order.line'].create({'order_id': order.id, 'sequence': sequence,
                                               'display_type': kind, 'name': name})
        doc = self._html('sale.action_report_saleorder', order, 'subsections')
        self.assertEqual(len(doc.xpath('//td[@name="td_qty"]')), 1)
        for marker in ('SECTION MARKER', 'SUBSECTION MARKER', 'NOTE MARKER'):
            self.assertIn(marker, doc.text_content())
        self.assertAlmostEqual(order.amount_untaxed, 225)
        self.assertIn('10', doc.xpath('//td[@name="td_discount"]')[0].text_content())
        self.assertIn(str(int(self.tax_sale_a.amount)), doc.text_content())

    def test_shipping_contacts_and_incoterms(self):
        order = self._order()
        child = self.env['res.partner'].create({'name': 'CHILD CONTACT', 'parent_id': self.partner_a.id,
            'type': 'delivery', 'street': self.partner_a.street, 'city': self.partner_a.city,
            'zip': self.partner_a.zip, 'phone': '+421123456789', 'email': 'contact@example.invalid'})
        order.partner_shipping_id = child
        incoterm = self.env['account.incoterms'].search([('code', '=', 'EXW')], limit=1)
        self.assertTrue(incoterm)
        order.write({'incoterm': incoterm.id, 'incoterm_location': 'TEST LOADING BAY'})
        doc = self._html('sale.action_report_saleorder', order, 'same_address_child')
        for marker in ('CHILD CONTACT', '+421123456789', 'contact@example.invalid', 'TEST LOADING BAY'):
            self.assertIn(marker, doc.text_content())
        child.write({'parent_id': False, 'is_company': True, 'name': 'DIFFERENT SHIPPING COMPANY', 'street': '99 Other Street'})
        doc = self._html('sale.action_report_saleorder', order, 'different_shipping')
        self.assertIn('DIFFERENT SHIPPING COMPANY', doc.text_content())
        self.assertIn('99 Other Street', doc.text_content())

    def test_pdf_standard_and_fallback_actions(self):
        order = self._order()
        for xmlid, unused in CONTRACTS:
            self._pdf(xmlid, order, xmlid.split('.')[-1])
        order.action_confirm()
        self._pdf('sale.action_report_saleorder', order, 'confirmed_order')


    def test_background_selection_and_legacy_image_as_custom(self):
        record = self._order()
        asset = Path(__file__).resolve().parents[1] / 'static/img/bg_background_template.jpg'
        legacy = base64.b64encode(asset.read_bytes())
        for choice, picture, expected in (
            ('Blank', False, 'background-image: url();'),
            ('Custom', legacy, 'data:image/png;base64,' + legacy.decode()),
            ('Demo logo', False, '/base/static/img/demo_logo_report.png'),
        ):
            record.company_id.write({'layout_background': choice, 'layout_background_image': picture})
            for action in ('sale.action_report_saleorder',):
                document = self._html(action, record, 'background_' + choice.replace(' ', '_') + '_' + action.split('.')[-1])
                article = document.xpath('//div[contains(concat(" ", normalize-space(@class), " "), " article ")]')
                self.assertTrue(article)
                self.assertIn(expected, article[0].get('style'))
                self.assertEqual('o_report_layout_background' in article[0].get('class'), choice != 'Blank')
                self._pdf(action, record, 'background_' + choice.replace(' ', '_') + '_' + action.split('.')[-1])
        # Migrated literal Geometric requires an actual migration registry/data gate.
        # This test uses the supported Custom selection with exact legacy image bytes.
