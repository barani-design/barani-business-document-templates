"""Real Odoo19 report actions and ORM fixtures; no mocked renderer."""
import base64
import hashlib
import io
import json
import logging
import os
from pathlib import Path

from lxml import html, etree
from odoo import Command
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tools.safe_eval import safe_eval
from odoo.tools.pdf import PdfFileReader

_logger = logging.getLogger(__name__)
CONTRACTS = [('account.account_invoices', {'role': 'VAT invoice primary', 'xmlid': 'account.account_invoices', 'label_en_US': 'Invoices', 'label_languages': ['de_DE', 'en_US', 'sk_SK'], 'label_storage_md5': '5da741f380815eaa3471da7278886588', 'model': 'account.move', 'report_type': 'qweb-pdf', 'route': 'barani_vat.report_invoice_document_vat', 'paperformat': 'BARANI VAT A4 7mm', 'binding_model': 'account.move', 'groups': ['account.group_account_readonly', 'account.group_account_invoice'], 'binding_view_types': 'list,form', 'filename_expression': 'vat_numeric_first', 'filename_storage_md5': '627c9c93078dbb4c391c7cab95d4e3e6', 'attachment': 'object._get_report_attachment_filename()', 'filename': "((object.name or '').replace('/', '_') + ' - ' if object.name and object.name != '/' else '') + ('Credit Note' if object.move_type == 'out_refund' else 'Vendor Credit Note' if object.move_type == 'in_refund' else 'Vendor Bill' if object.move_type == 'in_invoice' else 'Draft Invoice' if object.state == 'draft' else 'Cancelled Invoice' if object.state == 'cancel' else 'Invoice')", 'filename_key': 'vat_numeric_first'}), ('account.account_invoices_without_payment', {'role': 'VAT invoice without payment', 'xmlid': 'account.account_invoices_without_payment', 'label_en_US': 'Invoices without Payment', 'label_languages': ['de_DE', 'en_US', 'sk_SK'], 'label_storage_md5': '60add45e54cb52d70ce13a69e45f2c58', 'model': 'account.move', 'report_type': 'qweb-pdf', 'route': 'barani_vat.report_invoice_document_vat', 'paperformat': 'BARANI VAT A4 7mm', 'binding_model': None, 'groups': [], 'binding_view_types': 'list,form', 'filename_expression': 'vat_numeric_first', 'filename_storage_md5': '627c9c93078dbb4c391c7cab95d4e3e6', 'attachment': 'object._get_report_attachment_filename()', 'filename': "((object.name or '').replace('/', '_') + ' - ' if object.name and object.name != '/' else '') + ('Credit Note' if object.move_type == 'out_refund' else 'Vendor Credit Note' if object.move_type == 'in_refund' else 'Vendor Bill' if object.move_type == 'in_invoice' else 'Draft Invoice' if object.state == 'draft' else 'Cancelled Invoice' if object.state == 'cancel' else 'Invoice')", 'filename_key': 'vat_numeric_first'}), ('barani_vat.action_report_vat_2026', {'role': 'VAT 2026+', 'xmlid': None, 'label_en_US': 'VAT Invoices RI/DPI - 2026+', 'label_languages': ['en_US'], 'label_storage_md5': 'be2bfcbdbcbfb597f6d39c2bf077d922', 'model': 'account.move', 'report_type': 'qweb-pdf', 'route': 'barani_vat.report_invoice_document_vat', 'paperformat': 'BARANI VAT A4 7mm', 'binding_model': None, 'groups': ['sales_team.group_sale_manager', 'account.group_account_invoice'], 'binding_view_types': 'list,form', 'filename_expression': 'vat_numeric_first', 'filename_storage_md5': '36058b39c8865fb8ad5dadee41a8c6eb', 'attachment': None, 'filename': "((object.name or '').replace('/', '_') + ' - ' if object.name and object.name != '/' else '') + ('Credit Note' if object.move_type == 'out_refund' else 'Vendor Credit Note' if object.move_type == 'in_refund' else 'Vendor Bill' if object.move_type == 'in_invoice' else 'Draft Invoice' if object.state == 'draft' else 'Cancelled Invoice' if object.state == 'cancel' else 'Invoice')", 'filename_key': 'vat_numeric_first'}), ('barani_vat.action_invoice_preview', {'role': 'Invoice Preview runtime resolver', 'xmlid': None, 'label_en_US': 'Invoice Preview', 'label_languages': ['en_US'], 'label_storage_md5': '801b3dec5fb4dca6092404182eba6ce7', 'model': 'account.move', 'report_type': 'qweb-html', 'route': 'barani_vat.report_invoice_document_vat', 'paperformat': 'BARANI VAT A4 7mm', 'binding_model': None, 'groups': [], 'binding_view_types': 'form', 'filename_expression': 'vat_numeric_first', 'filename_storage_md5': '36058b39c8865fb8ad5dadee41a8c6eb', 'attachment': None, 'filename': "((object.name or '').replace('/', '_') + ' - ' if object.name and object.name != '/' else '') + ('Credit Note' if object.move_type == 'out_refund' else 'Vendor Credit Note' if object.move_type == 'in_refund' else 'Vendor Bill' if object.move_type == 'in_invoice' else 'Draft Invoice' if object.state == 'draft' else 'Cancelled Invoice' if object.state == 'cancel' else 'Invoice')", 'filename_key': 'vat_numeric_first'})]


@tagged('post_install', '-at_install', 'barani_reports')
class TestBaraniVatRendering(AccountTestInvoicingCommon):

    @classmethod
    def get_default_groups(cls):
        # Linked advance history is read through real sale.order/line records.
        return super().get_default_groups() | cls.env.ref('sales_team.group_sale_salesman')

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.external_report_layout_id = cls.env.ref('web.external_layout_standard')
        # Reuse one account when a test creates several invoices in one transaction.
        cls.report_advance_account = cls.env['account.account'].create({
            'name': 'REPORT ADVANCE', 'code': '324991', 'account_type': 'liability_current',
            'company_ids': [Command.set(cls.env.company.ids)],
        })

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
        self.assertFalse(self.env.su)
        report = self.env.ref(action)
        self.assertEqual(report.model, record._name)
        route = report.report_action(record)
        self.assertEqual(route['type'], 'ir.actions.report')
        self.assertEqual(route['report_name'], report.report_name)
        self.assertEqual(route['context']['active_ids'], record.ids)
        body, kind = self.env['ir.actions.report']._render_qweb_html(action, record.ids)
        self.assertEqual(kind, 'html')
        self.assertGreater(len(body), 500)
        self._capture(label, action, record, body, 'html')
        return html.fromstring(body)

    def _pdf(self, action, record, label, minimum_pages=1):
        self.assertFalse(self.env.su)
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
        reports._barani_vat_adopt_metadata()
        reports._barani_vat_adopt_metadata()
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
            self.env['ir.actions.report']._barani_vat_adopt_metadata()

    def _invoice(self, advance=False, deduction=False, refund=False, post=True):
        account = self.report_advance_account
        product = self.product_a
        lines = []
        if not advance:
            lines.append(Command.create({'product_id': product.id, 'name': 'REPORT GOODS',
                'quantity': 2, 'price_unit': 100, 'account_id': self.company_data['default_account_revenue'].id,
                'tax_ids': [Command.set(self.tax_sale_a.ids)]}))
        if advance or deduction:
            lines.append(Command.create({'name': 'REPORT ADVANCE' if advance else 'REPORT DEDUCTION',
                'quantity': 1, 'price_unit': -40 if deduction else 40, 'account_id': account.id,
                'tax_ids': [Command.set(self.tax_sale_a.ids)]}))
        invoice = self._create_invoice(move_type='out_refund' if refund else 'out_invoice',
            invoice_line_ids=lines, invoice_origin='SO/260904', payment_reference='260904', post=post)
        return invoice, account

    def test_regular_invoice_all_actions_and_preview_view(self):
        invoice, account = self._invoice()
        self.partner_a.write({'phone': False, 'email': False})
        for xmlid, contract in CONTRACTS:
            doc = self._html(xmlid, invoice, xmlid.split('.')[-1])
            self.assertIn('REPORT GOODS', doc.text_content())
            self.assertIn('260904', doc.text_content())
            self.assertNotIn('Down Payment Invoice', doc.text_content())
            self.assertIn(' - Invoice', safe_eval(contract['filename'], {'object': invoice}))
        view = self.env['account.move'].get_view(view_id=self.env.ref('account.view_move_form').id, view_type='form')
        arch = etree.fromstring(view['arch'].encode())
        buttons = arch.xpath('//button[@name="%s"]' % self.env.ref('barani_vat.action_invoice_preview').id)
        self.assertEqual(len(buttons), 1)
        self.assertEqual(buttons[0].get('type'), 'action')
        self.assertEqual(self.env.ref('barani_vat.action_invoice_preview').report_type, 'qweb-html')
        self.assertEqual(invoice._barani_report_attachment_filename(), invoice.name.replace('/', '_') + '.pdf')

    def test_positive_324_and_cross_company_context(self):
        invoice, account = self._invoice(advance=True)
        other = self.setup_other_company(name='REPORT OTHER COMPANY',
            external_report_layout_id=self.env.ref('web.external_layout_standard').id)['company']
        # Authorize the test user and explicitly share this account before assigning
        # its second company-dependent code. Rendering still runs without sudo.
        self.env.user.company_ids = [Command.link(other.id)]
        self.env = self.env(context=dict(self.env.context,
            allowed_company_ids=[invoice.company_id.id, other.id]))
        account = account.with_env(self.env)
        # Odoo requires a code for every shared company at the end of write().
        account.write({
            'code_mapping_ids': [Command.create({'company_id': other.id, 'code': '700991'})],
            'company_ids': [Command.link(other.id)],
        })
        self.assertEqual(set(account.company_ids.ids), {invoice.company_id.id, other.id})
        self.assertTrue(account.with_company(invoice.company_id).code.startswith('324'))
        self.assertFalse(account.with_company(other).code.startswith('324'))
        self.env = self.env(context=dict(self.env.context, allowed_company_ids=[other.id, invoice.company_id.id]))
        self.assertEqual(self.env.company, other)
        self.assertFalse(self.env.su)
        doc = self._html('account.account_invoices', invoice, 'company_324')
        self.assertIn('Down Payment Invoice', doc.text_content())
        self.assertIn('REPORT ADVANCE', doc.text_content())
        self._pdf('account.account_invoices', invoice, 'company_324')

    def test_negative_324_linked_history(self):
        source, account = self._invoice(advance=True)
        order = self.env['sale.order'].create({'partner_id': self.partner_a.id,
            'order_line': [Command.create({'name': 'Advance payment', 'is_downpayment': True, 'price_unit': 40})]})
        source.invoice_line_ids.sale_line_ids = order.order_line
        # A single fixture account is reused for the settlement deduction.
        invoice = self._create_invoice(invoice_origin='SO/260904', invoice_line_ids=[
            Command.create({'product_id': self.product_a.id, 'name': 'REPORT GOODS', 'quantity': 2,
                'price_unit': 100, 'account_id': self.company_data['default_account_revenue'].id,
                'tax_ids': [Command.set(self.tax_sale_a.ids)]}),
            Command.create({'name': 'REPORT DEDUCTION', 'quantity': 1, 'price_unit': -40,
                'account_id': account.id, 'tax_ids': [Command.set(self.tax_sale_a.ids)],
                'sale_line_ids': [Command.set(order.order_line.ids)]}),
        ], post=True)
        doc = self._html('account.account_invoices', invoice, 'negative_324_history')
        self.assertIn('Down Payment Invoice ' + source.name, doc.text_content())
        self.assertIn('REPORT GOODS', doc.text_content())
        self.assertAlmostEqual(invoice.amount_untaxed, 160)
        self._pdf('account.account_invoices', invoice, 'negative_324_history')

    def test_credit_note_and_original_reference(self):
        invoice, account = self._invoice(refund=True)
        invoice.ref = 'RI/260800'
        doc = self._html('account.account_invoices', invoice, 'credit_note')
        self.assertIn('Credit Note', doc.text_content())
        self.assertIn('Amount credited', doc.text_content())
        self.assertIn('RI/260800', doc.text_content())
        self.assertIn(' - Credit Note', safe_eval(self.env.ref('account.account_invoices').print_report_name, {'object': invoice}))
        self._pdf('account.account_invoices', invoice, 'credit_note')

    def test_invoice_contacts_and_subsection(self):
        invoice, account = self._invoice(post=False)
        shipping = self.env['res.partner'].create({'name': 'REPORT SHIPPING COMPANY', 'is_company': True,
            'street': '99 Shipping Street', 'phone': '+421987654321', 'email': 'ship@example.invalid'})
        invoice.partner_shipping_id = shipping
        self.env['account.move.line'].create({'move_id': invoice.id, 'display_type': 'line_subsection', 'name': 'INVOICE SUBSECTION'})
        doc = self._html('barani_vat.action_invoice_preview', invoice, 'shipping_subsection')
        for marker in ('REPORT SHIPPING COMPANY', '99 Shipping Street', '+421987654321', 'INVOICE SUBSECTION'):
            self.assertIn(marker, doc.text_content())
        self.assertEqual(len(doc.xpath('//td[@name="td_qty"]')), 1)

    def test_payment_widget_and_receiving_bank(self):
        invoice, account = self._invoice(advance=True)
        self._register_payment(invoice, journal_id=self.company_data['default_journal_bank'].id,
                               amount=invoice.amount_total)
        self.assertTrue(invoice.invoice_payments_widget)
        self.assertTrue(invoice.invoice_payments_widget.get('content'))
        bank = self.env['res.bank'].create({'name': 'REPORT FIO BANK', 'bic': 'FIOZSKBAXXX'})
        self.env['res.partner.bank'].create({'partner_id': invoice.company_id.partner_id.id,
            'bank_id': bank.id, 'acc_number': 'SK1483300000002401465895'})
        doc = self._html('account.account_invoices', invoice, 'paid_advance_bank')
        for marker in ('SK1483300000002401465895', 'FIOZSKBAXXX', 'REPORT FIO BANK'):
            self.assertIn(marker, doc.text_content().replace(' ', '')) if marker.startswith('SK') else self.assertIn(marker, doc.text_content())
        self._pdf('account.account_invoices', invoice, 'paid_advance_bank')

    def test_pdf_all_invoice_actions(self):
        invoice, account = self._invoice()
        for xmlid, contract in CONTRACTS:
            if contract['report_type'] == 'qweb-pdf':
                self._pdf(xmlid, invoice, xmlid.split('.')[-1])


    def test_background_selection_and_legacy_image_as_custom(self):
        record = self._invoice()[0]
        asset = Path(__file__).resolve().parents[1] / 'static/img/bg_background_template.jpg'
        legacy = base64.b64encode(asset.read_bytes())
        for choice, picture, expected in (
            ('Blank', False, 'background-image: url();'),
            ('Custom', legacy, 'data:image/png;base64,' + legacy.decode()),
            ('Demo logo', False, '/base/static/img/demo_logo_report.png'),
        ):
            record.company_id.write({'layout_background': choice, 'layout_background_image': picture})
            for action in ('account.account_invoices',):
                document = self._html(action, record, 'background_' + choice.replace(' ', '_') + '_' + action.split('.')[-1])
                article = document.xpath('//div[contains(concat(" ", normalize-space(@class), " "), " article ")]')
                self.assertTrue(article)
                self.assertIn(expected, article[0].get('style'))
                self.assertEqual('o_report_layout_background' in article[0].get('class'), choice != 'Blank')
                self._pdf(action, record, 'background_' + choice.replace(' ', '_') + '_' + action.split('.')[-1])
        # Migrated literal Geometric requires an actual migration registry/data gate.
        # This test uses the supported Custom selection with exact legacy image bytes.


    def test_attachment_creation_filenames_and_no_cached_reuse(self):
        for action in ('account.account_invoices', 'account.account_invoices_without_payment'):
            invoice, unused = self._invoice(post=False)
            report = self.env.ref(action)
            draft_name = invoice._get_report_base_filename().replace('/', '_') + '.pdf'
            self.assertEqual(safe_eval(report.attachment, {'object': invoice}), draft_name)
            invoice.action_post()
            expected = invoice.name.replace('/', '_') + '.pdf'
            self.assertEqual(safe_eval(report.attachment, {'object': invoice}), expected)
            self.assertFalse(report.attachment_use)
            self.assertFalse(report.retrieve_attachment(invoice))
            service = self.env['ir.actions.report'].with_context(force_report_rendering=True)
            body, kind = service._render_qweb_pdf(action, invoice.ids)
            self.assertEqual(kind, 'pdf')
            self.assertTrue(body.startswith(b'%PDF-'))
            attachment = report.retrieve_attachment(invoice)
            self.assertTrue(attachment)
            self.assertEqual(attachment.name, expected)
            self.assertTrue(attachment.raw.startswith(b'%PDF-'))
            self._capture('attachment_' + action.split('.')[-1], action, invoice, body, 'pdf')
            invoice.narration = '<p>ATTACHMENT FRESH RENDER MARKER</p>'
            fresh, kind = service._render_qweb_pdf(action, invoice.ids)
            self.assertEqual(kind, 'pdf')
            text = ''.join(page.extract_text() if hasattr(page, 'extract_text') else page.extractText()
                           for page in PdfFileReader(io.BytesIO(fresh)).pages)
            self.assertIn('ATTACHMENT FRESH RENDER MARKER', ' '.join(text.split()))
            self._capture('attachment_fresh_' + action.split('.')[-1], action, invoice, fresh, 'pdf')
            self.assertEqual(invoice._get_invoice_report_filename(report=report),
                             safe_eval(report.print_report_name, {'object': invoice}).replace('/', '_') + '.pdf')


@tagged('post_install', '-at_install', '-standard', '-barani_reports', 'barani_reports_fullset')
class TestBaraniVatFullset(TestBaraniVatRendering):
    def test_populated_native_intrastat_transport(self):
        field = self.env['account.move']._fields.get('intrastat_transport_mode_id')
        self.assertTrue(field, 'ENVIRONMENT_PRECONDITION: native account_intrastat owner required')
        self.assertEqual(field.type, 'many2one')
        mode = self.env[field.comodel_name].search([], limit=1)
        self.assertTrue(mode, 'ENVIRONMENT_PRECONDITION: native transport reference data missing')
        invoice, unused = self._invoice(post=False)
        invoice.intrastat_transport_mode_id = mode
        document = self._html('account.account_invoices', invoice, 'native_intrastat_transport')
        node = document.xpath('//*[@name="barani_intrastat_transport_code"]')
        self.assertEqual(len(node), 1)
        self.assertIn(mode.display_name, node[0].text_content())
        self._pdf('account.account_invoices', invoice, 'native_intrastat_transport')
