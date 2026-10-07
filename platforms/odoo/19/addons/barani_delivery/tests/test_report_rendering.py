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
CONTRACTS = [('barani_delivery.action_report_delivery_note', {'role': 'Delivery Note direct', 'xmlid': None, 'label_en_US': 'Delivery Slip', 'label_source_xmlid': 'stock.action_report_delivery', 'label_languages': ['de_DE', 'en_US', 'sk_SK'], 'label_storage_md5': '9636fbb1ec6e5e0287e9f674ec9f9280', 'model': 'stock.picking', 'report_type': 'qweb-pdf', 'route': 'barani_delivery.report_delivery_note_2026', 'paperformat': 'BARANI Delivery A4 7mm', 'binding_model': 'stock.picking', 'groups': ['sales_team.group_sale_manager', 'stock.group_stock_user'], 'binding_view_types': 'list,form', 'filename_expression': 'delivery_note_numeric_first', 'filename_storage_md5': 'fcc222bf9a2ae2c82d38c633ecdf224c', 'attachment': None, 'filename': "(((object.name or '')[7:] if (object.name or '')[:7] == 'BA/OUT/' else (object.name or 'DN')).replace('/', '_')) + ' - Delivery Note'", 'filename_key': 'delivery_note_numeric_first'}), ('barani_delivery.action_report_sale_delivery_note', {'role': 'Delivery Note sale-order bridge', 'xmlid': None, 'label_en_US': 'Delivery Note', 'label_languages': ['en_US'], 'label_storage_md5': 'f448a50364f47362b4dde62c73045d05', 'model': 'sale.order', 'report_type': 'qweb-pdf', 'route': 'barani_delivery.report_sale_order_delivery_note_2026', 'paperformat': 'BARANI Delivery A4 7mm', 'binding_model': 'sale.order', 'groups': [], 'binding_view_types': 'list,form', 'filename_expression': 'sale_delivery_bridge_numeric_first', 'filename_storage_md5': 'ae2cb1870cceb69bee7aee5a04491125', 'attachment': None, 'filename': "(((((object.picking_ids.filtered_domain([('picking_type_id.code','=','outgoing'),('state','!=','cancel')])).name or '')[7:] if ((object.picking_ids.filtered_domain([('picking_type_id.code','=','outgoing'),('state','!=','cancel')])).name or '')[:7] == 'BA/OUT/' else ((object.picking_ids.filtered_domain([('picking_type_id.code','=','outgoing'),('state','!=','cancel')])).name or 'DN'))).replace('/', '_') + ' - Delivery Note') if len(object.picking_ids.filtered_domain([('picking_type_id.code','=','outgoing'),('state','!=','cancel')])) == 1 else ((((object.name or '')[3:] if (object.name or '')[:3] in ('SO/','PF/') else (object.name or '')[2:] if (object.name or '')[:2] == 'Q/' else (object.name or ''))).replace('/', '_') + (' - Delivery Notes' if len(object.picking_ids.filtered_domain([('picking_type_id.code','=','outgoing'),('state','!=','cancel')])) > 1 else ' - Delivery Note Unavailable'))", 'filename_key': 'sale_delivery_bridge_numeric_first'}), ('barani_delivery.action_report_picking_operations', {'role': 'Picking Operations 2026+', 'xmlid': None, 'label_en_US': 'Picking Operations', 'label_source_xmlid': 'stock.action_report_picking', 'label_languages': ['de_DE', 'en_US', 'sk_SK'], 'label_storage_md5': '9f27381b8769db7c092e870f5d94668d', 'model': 'stock.picking', 'report_type': 'qweb-pdf', 'route': 'barani_delivery.report_picking_operations_2026', 'paperformat': 'BARANI Picking Operations A4 7mm', 'binding_model': 'stock.picking', 'groups': ['stock.group_stock_user'], 'binding_view_types': 'list,form', 'filename_expression': 'picking_operations_numeric_first', 'filename_storage_md5': '5bcec4a2a15fc4cac8081b02db92fe63', 'attachment': None, 'filename': "(((object.name or '')[7:] if (object.name or '')[:7] == 'BA/OUT/' else (object.name or 'Picking')).replace('/', '_')) + ' - Picking Operations'", 'filename_key': 'picking_operations_numeric_first'})]


@tagged('post_install', '-at_install', 'barani_reports')
class TestBaraniDeliveryRendering(AccountTestInvoicingCommon):

    @classmethod
    def get_default_groups(cls):
        # Keep normal ACLs when constructing the sale-order bridge fixtures.
        return super().get_default_groups() | cls.env.ref('sales_team.group_sale_salesman')

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
        reports._barani_delivery_adopt_metadata()
        reports._barani_delivery_adopt_metadata()
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
            self.env['ir.actions.report']._barani_delivery_adopt_metadata()

    def _native_label_pairs(self):
        return [
            ('barani_delivery.action_report_delivery_note', 'stock.action_report_delivery'),
            ('barani_delivery.action_report_picking_operations', 'stock.action_report_picking'),
        ]

    def _metadata_xmlid(self, xmlid):
        module, name = xmlid.split('.', 1)
        return self.env['ir.model.data'].search([
            ('module', '=', module), ('name', '=', name),
        ])

    def test_metadata_fresh_native_labels_are_not_adopted(self):
        reports = self.env['ir.actions.report']
        native_before = {}
        for xmlid, native_xmlid in self._native_label_pairs():
            owned = self.env.ref(xmlid)
            self._metadata_xmlid(xmlid).unlink()
            owned.unlink()
            native = self.env.ref(native_xmlid)
            native.binding_model_id = self.env.ref('stock.model_stock_picking')
            native_before[native_xmlid] = native.read()[0]
        before = reports.search_count([])
        reports._barani_delivery_adopt_metadata()
        reports._barani_delivery_adopt_metadata()
        self.assertEqual(reports.search_count([]), before)
        for xmlid, native_xmlid in self._native_label_pairs():
            self.assertFalse(self._metadata_xmlid(xmlid))
            self.assertEqual(self.env.ref(native_xmlid).read()[0], native_before[native_xmlid])

    def test_metadata_legacy_adoption_preserves_native_actions(self):
        reports = self.env['ir.actions.report']
        owned_ids, native_before = {}, {}
        for xmlid, native_xmlid in self._native_label_pairs():
            owned_ids[xmlid] = self.env.ref(xmlid).id
            self._metadata_xmlid(xmlid).unlink()
            native_before[native_xmlid] = self.env.ref(native_xmlid).read()[0]
        before = reports.search_count([])
        reports._barani_delivery_adopt_metadata()
        reports._barani_delivery_adopt_metadata()
        self.assertEqual(reports.search_count([]), before)
        for xmlid, native_xmlid in self._native_label_pairs():
            self.assertEqual(self.env.ref(xmlid).id, owned_ids[xmlid])
            self.assertNotEqual(self.env.ref(xmlid), self.env.ref(native_xmlid))
            self.assertEqual(self.env.ref(native_xmlid).read()[0], native_before[native_xmlid])

    def test_metadata_unknown_same_label_duplicates_stop(self):
        for xmlid, _native_xmlid in self._native_label_pairs():
            with self.subTest(xmlid=xmlid):
                with self.assertRaisesRegex(ValidationError, 'Ambiguous BARANI metadata'), self.env.cr.savepoint():
                    report = self.env.ref(xmlid)
                    report.copy({'name': report.name, 'report_name': 'unknown.report'})
                    self.env['ir.actions.report']._barani_delivery_adopt_metadata()

    def test_metadata_tampered_legacy_route_stops(self):
        for xmlid, _native_xmlid in self._native_label_pairs():
            with self.subTest(xmlid=xmlid):
                with self.assertRaisesRegex(ValidationError, 'Legacy BARANI metadata mismatch'), self.env.cr.savepoint():
                    report = self.env.ref(xmlid)
                    self._metadata_xmlid(xmlid).unlink()
                    report.report_name = 'unknown.report'
                    self.env['ir.actions.report']._barani_delivery_adopt_metadata()

    def test_metadata_owned_xmlid_cannot_alias_native(self):
        for xmlid, native_xmlid in self._native_label_pairs():
            with self.subTest(xmlid=xmlid):
                with self.assertRaisesRegex(ValidationError, 'BARANI metadata XML ID collision'), self.env.cr.savepoint():
                    self._metadata_xmlid(xmlid).res_id = self.env.ref(native_xmlid).id
                    self.env['ir.actions.report']._barani_delivery_adopt_metadata()

    def test_metadata_native_identity_mismatch_stops(self):
        for _xmlid, native_xmlid in self._native_label_pairs():
            with self.subTest(xmlid=native_xmlid):
                with self.assertRaisesRegex(ValidationError, 'Native BARANI label source mismatch'), self.env.cr.savepoint():
                    self.env.ref(native_xmlid).report_name = 'unknown.report'
                    self.env['ir.actions.report']._barani_delivery_adopt_metadata()

    def _picking(self, quantities=(0, 0), sale=False, tracking='none', incoming=False, product=None):
        if product is None:
            # product.product.create returns a record with variant creation disabled.
            # Restore template variant generation before copying that fixture.
            product = self.product_a.with_context(create_product_product=True).copy({
                'name': 'REPORT STOCK PRODUCT', 'type': 'consu',
                'is_storable': True, 'tracking': tracking, 'barcode': False})
            product.barcode = 'RPT' + str(product.id)
        self.assertEqual(len(product), 1, 'The stock fixture requires one real product variant')
        self.assertTrue(product.uom_id)
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)
        if not warehouse:
            warehouse = self.env['stock.warehouse'].create({'name': 'Report Warehouse', 'code': 'RPT'})
        partner = self.partner_a
        src = self.env.ref('stock.stock_location_customers') if incoming else warehouse.lot_stock_id
        dst = warehouse.lot_stock_id if incoming else self.env.ref('stock.stock_location_customers')
        picking = self.env['stock.picking'].create({'partner_id': partner.id,
            'picking_type_id': (warehouse.in_type_id if incoming else warehouse.out_type_id).id,
            'location_id': src.id, 'location_dest_id': dst.id})
        values = {'picking_id': picking.id, 'product_id': product.id, 'product_uom': product.uom_id.id,
                  'product_uom_qty': max(sum(quantities), 10), 'location_id': src.id, 'location_dest_id': dst.id}
        if sale:
            order = self.env['sale.order'].create({'name': 'SO/260902', 'partner_id': partner.id,
                'order_line': [Command.create({'product_id': product.id, 'product_uom_qty': 10})]})
            values['sale_line_id'] = order.order_line.id
        move = self.env['stock.move'].create(values)
        move._action_confirm(merge=False)
        if incoming:
            # Customer/supplier locations bypass reservation: confirmation has
            # already generated demand-sized lines. Replace those automatic
            # lines before adding this fixture's explicitly chosen quantities.
            move._do_unreserve()
            self.assertFalse(move.move_line_ids)
        for index, quantity in enumerate(quantities):
            if quantity:
                vals = {'move_id': move.id, 'picking_id': picking.id, 'product_id': product.id,
                        'product_uom_id': product.uom_id.id, 'location_id': src.id,
                        'location_dest_id': dst.id, 'quantity': quantity, 'picked': False}
                if tracking != 'none':
                    lot = self.env['stock.lot'].create({'name': 'REPORT-LOT-' + str(index),
                        'product_id': product.id, 'company_id': self.env.company.id})
                    vals['lot_id'] = lot.id
                if not incoming:
                    self.env['stock.quant']._update_available_quantity(
                        product, src, quantity if tracking != 'none' else max(quantity, 120),
                        lot_id=lot if tracking != 'none' else False)
                self.env['stock.move.line'].create(vals)
        return picking, move

    def test_reservation_only_and_mixed_picked_lines(self):
        picking, move = self._picking((2, 7), tracking='lot')
        self.assertEqual(move.quantity, 9)
        self.assertEqual(move.barani_report_done_qty, 0)
        doc = self._html('barani_delivery.action_report_delivery_note', picking, 'reservation_only')
        self.assertIn('REPORT STOCK PRODUCT', doc.text_content())
        self.assertEqual(float(doc.xpath('//table[contains(@class, "barani_delivery_table")]//tbody/tr[td[2][contains(., "REPORT STOCK PRODUCT")]]/td[last()-1]')[0].text_content()), 0)
        move.move_line_ids[0].picked = True
        self.assertTrue(move.picked)
        self.assertEqual(move.barani_report_done_qty, 2)
        doc = self._html('barani_delivery.action_report_delivery_note', picking, 'mixed_picked')
        self.assertEqual(float(doc.xpath('//table[contains(@class, "barani_delivery_table")]//tbody/tr[td[2][contains(., "REPORT STOCK PRODUCT")]]/td[last()-1]')[0].text_content()), 2)
        ops = self._html('barani_delivery.action_report_picking_operations', picking, 'reserved_pickops')
        for marker in ('REPORT-LOT-0', 'REPORT-LOT-1', '2.00', '7.00'):
            self.assertIn(marker, ops.text_content())

    def test_picked_quantity_uom_conversion(self):
        picking, move = self._picking((1, 7))
        move.move_line_ids[0].write({'product_uom_id': self.uom_dozen.id, 'quantity': 1, 'picked': True})
        self.assertAlmostEqual(move.barani_report_done_qty, 12)
        doc = self._html('barani_delivery.action_report_delivery_note', picking, 'uom_conversion')
        self.assertEqual(float(doc.xpath('//table[contains(@class, "barani_delivery_table")]//tbody/tr[td[2][contains(., "REPORT STOCK PRODUCT")]]/td[last()-1]')[0].text_content()), 12)

    def test_partial_done_backorder_and_return(self):
        picking, move = self._picking((3, 0))
        move.move_line_ids.picked = True
        picking.with_context(skip_backorder=True).button_validate()
        self.assertEqual(picking.state, 'done')
        self.assertEqual(move.barani_report_done_qty, 3)
        backorder = self.env['stock.picking'].search([('backorder_id', '=', picking.id)])
        self.assertEqual(len(backorder), 1)
        self.assertEqual(sum(backorder.move_ids.mapped('product_uom_qty')), 7)
        self.assertEqual(sum(backorder.move_ids.mapped('barani_report_done_qty')), 0)
        self._html('barani_delivery.action_report_delivery_note', picking, 'done_partial')
        self._html('barani_delivery.action_report_delivery_note', backorder, 'backorder')
        returned, return_move = self._picking((1, 0), incoming=True, product=move.product_id)
        return_move.origin_returned_move_id = move
        self.assertEqual(return_move.quantity, 1, 'Return fixture must contain only the one selected unit')
        return_move.move_line_ids.picked = True
        returned.with_context(skip_backorder=True, picking_ids_not_to_backorder=returned.ids).button_validate()
        self.assertEqual(returned.state, 'done')
        self.assertEqual(return_move.barani_report_done_qty, 1)  # Accepted magnitude on direct return report.
        self._html('barani_delivery.action_report_delivery_note', returned, 'return')

    def test_saleless_and_sale_wrapper_zero_one_multiple(self):
        picking, move = self._picking((1, 0))
        self.assertFalse(picking.sale_id)
        self.assertFalse(move.sale_line_id)
        doc = self._html('barani_delivery.action_report_delivery_note', picking, 'true_saleless')
        self.assertIn('Not specified', doc.text_content())
        order = self.env['sale.order'].create({'name': 'SO/260903', 'partner_id': self.partner_a.id})
        doc = self._html('barani_delivery.action_report_sale_delivery_note', order, 'no_deliveries')
        self.assertIn('No outgoing delivery order', doc.text_content())
        linked, linked_move = self._picking((1, 0), sale=True)
        order = linked_move.sale_line_id.order_id
        self.assertEqual(linked.sale_id, order)
        incoterm = self.env['account.incoterms'].search([('code', '=', 'EXW')], limit=1)
        order.incoterm = incoterm
        doc = self._html('barani_delivery.action_report_sale_delivery_note', order, 'one_delivery')
        self.assertIn('EXW', doc.text_content())
        self.assertIn('SO/260902', doc.text_content())
        second = linked.copy({'move_ids': False})
        linked_move.copy({'picking_id': second.id})
        self.assertEqual(len(order.picking_ids), 2)
        doc = self._html('barani_delivery.action_report_sale_delivery_note', order, 'multiple_deliveries')
        self.assertEqual(len(doc.xpath('//div[contains(concat(" ", normalize-space(@class), " "), " page ")]')), 2)
        filename = safe_eval(self.env.ref('barani_delivery.action_report_sale_delivery_note').print_report_name, {'object': order})
        self.assertEqual(filename, '260902 - Delivery Notes')

    def test_packages_and_native_menu_contract(self):
        picking, move = self._picking((2, 0))
        package = self.env['stock.package'].create({'name': 'REPORT PACKAGE'})
        # Packing loose goods into a new destination package is not a move
        # of an entire source package. Odoo deliberately clears that flag.
        move.move_line_ids.write({'result_package_id': package.id})
        self.assertFalse(any(move.move_line_ids.mapped('is_entire_pack')))
        picking.picking_type_id.show_entire_packs = False
        self.assertIn(move, picking._barani_report_moves())
        self._html('barani_delivery.action_report_picking_operations', picking, 'ordinary_package')
        # Now put exactly the moved quantity in the source package and let
        # Odoo verify that the complete package contents are being moved.
        self.env['stock.quant']._update_available_quantity(
            move.product_id, move.location_id, 2, package_id=package)
        move.move_line_ids.write({'package_id': package.id, 'result_package_id': False})
        self.assertTrue(picking._check_move_lines_map_quant_package(package))
        picking._check_entire_pack()
        self.assertTrue(all(move.move_line_ids.mapped('is_entire_pack')))
        self.assertEqual(move.move_line_ids.package_id, package)
        self.assertEqual(move.move_line_ids.result_package_id, package)
        picking.picking_type_id.show_entire_packs = True
        self.assertNotIn(move, picking._barani_report_moves())
        self._html('barani_delivery.action_report_picking_operations', picking, 'entire_package_mode')
        for xmlid in ('stock.action_report_delivery', 'stock.action_report_picking'):
            self.assertFalse(self.env.ref(xmlid).binding_model_id)
        self.assertTrue(self.env.ref('stock.action_report_picking_packages').binding_model_id)
        self.assertEqual(self.env.ref('barani_delivery.action_report_delivery_note').name,
                         self.env.ref('stock.action_report_delivery').name)

    def test_requested_without_move_lines(self):
        picking, move = self._picking()
        self.assertFalse(move.move_line_ids)
        doc = self._html('barani_delivery.action_report_picking_operations', picking, 'requested_only')
        self.assertIn('10', doc.text_content())
        self.assertEqual(move.barani_report_done_qty, 0)

    def test_pdf_actions_and_multipage_serials(self):
        picking, move = self._picking(tuple([1] * 90), sale=True, tracking='serial')
        for xmlid, contract in CONTRACTS:
            record = move.sale_line_id.order_id if contract['model'] == 'sale.order' else picking
            self._pdf(xmlid, record, xmlid.split('.')[-1], minimum_pages=2 if 'picking_operations' in xmlid else 1)




    def test_background_selection_and_legacy_image_as_custom(self):
        record = self._picking((1, 0))[0]
        asset = Path(__file__).resolve().parents[1] / 'static/img/bg_background_template.jpg'
        legacy = base64.b64encode(asset.read_bytes())
        for choice, picture, expected in (
            ('Blank', False, 'background-image: url();'),
            ('Custom', legacy, 'data:image/png;base64,' + legacy.decode()),
            ('Demo logo', False, '/base/static/img/demo_logo_report.png'),
        ):
            record.company_id.write({'layout_background': choice, 'layout_background_image': picture})
            for action in ('barani_delivery.action_report_delivery_note', 'barani_delivery.action_report_picking_operations'):
                document = self._html(action, record, 'background_' + choice.replace(' ', '_') + '_' + action.split('.')[-1])
                article = document.xpath('//div[contains(concat(" ", normalize-space(@class), " "), " article ")]')
                self.assertTrue(article)
                self.assertIn(expected, article[0].get('style'))
                self.assertEqual('o_report_layout_background' in article[0].get('class'), choice != 'Blank')
                self._pdf(action, record, 'background_' + choice.replace(' ', '_') + '_' + action.split('.')[-1])
        # Migrated literal Geometric requires an actual migration registry/data gate.
        # This test uses the supported Custom selection with exact legacy image bytes.


    def test_native_actions_route_to_barani_documents(self):
        reports = self.env['ir.actions.report']
        contracts = dict(CONTRACTS)
        languages = self.env['res.lang'].search([('active', '=', True)]).mapped('code')
        protected = {}
        for xmlid, native_xmlid in self._native_label_pairs():
            with self.subTest(native_xmlid=native_xmlid):
                owned = self.env.ref(xmlid)
                native = self.env.ref(native_xmlid)
                contract = contracts[xmlid]
                self.assertNotEqual(native.id, owned.id)
                self.assertEqual(native.report_name, contract['route'])
                self.assertEqual(native.report_file, contract['route'])
                self.assertEqual(native.paperformat_id, owned.paperformat_id)
                self.assertEqual(native.print_report_name, owned.print_report_name)
                self.assertFalse(native.binding_model_id)
                self.assertEqual(native.report_type, 'qweb-pdf')
                self.assertEqual(native.model, 'stock.picking')
                for lang in sorted(set(languages + ['en_US'])):
                    self.assertEqual(native.with_context(lang=lang).name,
                                     owned.with_context(lang=lang).name)
                protected[native_xmlid] = native.read()[0]
        before = (reports.search_count([]), self.env['report.paperformat'].search_count([]),
                  self.env['ir.model.data'].search_count([]))
        reports._barani_delivery_adopt_metadata()
        reports._barani_delivery_adopt_metadata()
        self.assertEqual(before, (
            reports.search_count([]), self.env['report.paperformat'].search_count([]),
            self.env['ir.model.data'].search_count([]),
        ))
        for _xmlid, native_xmlid in self._native_label_pairs():
            self.assertEqual(self.env.ref(native_xmlid).read()[0], protected[native_xmlid])

    def test_native_actions_render_barani_documents(self):
        picking, move = self._picking((10, 0), sale=True)
        self.assertEqual(picking.picking_type_id.code, 'outgoing')
        move.move_line_ids.picked = True
        picking.with_context(skip_backorder=True).button_validate()
        self.assertEqual(picking.state, 'done')
        markers = {
            'stock.action_report_delivery': (
                'barani_dn_source_order_cell', 'native_delivery_route', ' - Delivery Note'),
            'stock.action_report_picking': (
                'barani_picking_operations_2026_table', 'native_picking_route', ' - Picking Operations'),
        }
        for xmlid, native_xmlid in self._native_label_pairs():
            with self.subTest(native_xmlid=native_xmlid):
                marker, label, suffix = markers[native_xmlid]
                document = self._html(native_xmlid, picking, label)
                self.assertEqual(len(document.xpath('//*[@name="%s"]' % marker)), 1)
                self.assertIn('REPORT STOCK PRODUCT', document.text_content())
                self._pdf(native_xmlid, picking, label)
                native_filename = safe_eval(
                    self.env.ref(native_xmlid).print_report_name, {'object': picking})
                owned_filename = safe_eval(
                    self.env.ref(xmlid).print_report_name, {'object': picking})
                self.assertEqual(native_filename, owned_filename)
                self.assertTrue(native_filename.endswith(suffix))


@tagged('post_install', '-at_install', '-standard', '-barani_reports', 'barani_reports_fullset')
class TestBaraniDeliveryFullset(TestBaraniDeliveryRendering):
    # Only selected on a separately provisioned tenant/full-addon test database.
    def test_kit_and_optional_customs_fields(self):
        self.assertIn('bom_line_id', self.env['stock.move']._fields,
                      'ENVIRONMENT_PRECONDITION: requires installed sale_mrp')
        self.assertIn('hs_code', self.env['product.product']._fields,
                      'ENVIRONMENT_PRECONDITION: tenant HS-code owner missing')
        self.assertIn('country_of_origin', self.env['product.product']._fields,
                      'ENVIRONMENT_PRECONDITION: tenant origin-country owner missing')
        picking, move = self._picking((1, 0), sale=True)
        kit = self.product_a.with_context(create_product_product=True).copy({
            'name': 'REPORT KIT', 'type': 'consu',
            'hs_code': '90258040', 'country_of_origin': self.env.ref('base.sk').id})
        self.assertEqual(len(kit), 1, 'The kit fixture requires one real product variant')
        move.sale_line_id.product_id = kit
        bom = self.env['mrp.bom'].create({'product_tmpl_id': kit.product_tmpl_id.id,
            'type': 'phantom', 'product_qty': 1, 'bom_line_ids': [Command.create({
                'product_id': move.product_id.id, 'product_qty': 1})]})
        move.bom_line_id = bom.bom_line_ids
        move.move_line_ids.picked = True
        doc = self._html('barani_delivery.action_report_delivery_note', picking, 'kit_customs')
        for marker in ('90258040', 'SK'):
            self.assertIn(marker, doc.text_content())
        self._pdf('barani_delivery.action_report_delivery_note', picking, 'kit_customs')
