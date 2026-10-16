"""Real-record checks for retirement of migrated, conflicting Preview views."""

from lxml import etree

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestBaraniLegacyPreviewViews(TransactionCase):
    def setUp(self):
        super().setUp()
        self.views = self.env["ir.ui.view"].sudo()
        self.form = self.env.ref("account.view_move_form")
        self.preview = self.env.ref("barani_vat.action_invoice_preview")
        self.module_view = self.env.ref("barani_vat.view_move_form_barani_preview")

    def _legacy_fixture(self, *, xmlid=False):
        # ORM validation correctly rejects a NEW active conflicting view.
        # Create our own record inactive, then reproduce the historical state
        # left by the upgrade on this record alone. No validation method is
        # mocked; the production retirement method runs with normal validation.
        # TransactionCase rolls back this row and the optional XML ID.
        view = self.views.create({
            "name": "BARANI TEST legacy invoice Preview",
            "model": "account.move",
            "type": "form",
            "mode": "extension",
            "inherit_id": self.form.id,
            "priority": 999,
            "active": False,
            "arch": (
                '<data><xpath expr="//button[@name=\'preview_invoice\' and '
                '@type=\'object\']" position="attributes">'
                '<attribute name="name">%s</attribute>'
                '<attribute name="type">action</attribute>'
                '<attribute name="title">Preview BARANI 2026+ invoice</attribute>'
                '</xpath></data>'
            ) % self.preview.id,
        })
        if xmlid:
            self.env["ir.model.data"].sudo().create({
                "module": "studio_customization",
                "name": "barani_test_legacy_preview_%s" % view.id,
                "model": "ir.ui.view",
                "res_id": view.id,
            })
        view.flush_recordset(["active"])
        self.env.cr.execute(
            "UPDATE ir_ui_view SET active = TRUE WHERE id = %s AND active = FALSE",
            [view.id],
        )
        self.assertEqual(self.env.cr.rowcount, 1)
        view.invalidate_recordset(["active"])
        view.modified(["active"])
        self.env.registry.clear_cache("templates")
        self.assertTrue(view.active)
        self.assertEqual(bool(self.env["ir.model.data"].sudo().search_count([
            ("model", "=", "ir.ui.view"), ("res_id", "=", view.id),
        ])), xmlid)
        return view

    def test_retires_xmlid_less_preview_view(self):
        view = self._legacy_fixture()
        before = (view.arch, view.name, view.priority, view.inherit_id.id)
        self.views._barani_vat_retire_legacy_preview_views()
        self.assertTrue(view.exists())
        self.assertFalse(view.active)
        self.assertEqual(
            (view.arch, view.name, view.priority, view.inherit_id.id), before,
        )

    def test_keeps_module_and_xmlid_views(self):
        view = self._legacy_fixture(xmlid=True)
        before = (view.arch, view.name, view.priority, view.inherit_id.id)
        self.assertTrue(self.module_view.active)
        self.views._barani_vat_retire_legacy_preview_views()
        self.assertTrue(self.module_view.active)
        self.assertTrue(view.exists())
        self.assertTrue(view.active)
        self.assertEqual(
            (view.arch, view.name, view.priority, view.inherit_id.id), before,
        )

    def test_ignores_unrelated_custom_views(self):
        view = self.views.create({
            "name": "BARANI TEST unrelated invoice form extension",
            "model": "account.move",
            "type": "form",
            "mode": "extension",
            "inherit_id": self.form.id,
            "arch": (
                '<xpath expr="//sheet" position="attributes">'
                '<attribute name="string">BARANI unrelated fixture</attribute>'
                '</xpath>'
            ),
        })
        before = view.arch
        self.views._barani_vat_retire_legacy_preview_views()
        self.assertTrue(view.exists())
        self.assertTrue(view.active)
        self.assertEqual(view.arch, before)

    def test_idempotent_and_form_renders(self):
        view = self._legacy_fixture()
        self.views._barani_vat_retire_legacy_preview_views()
        self.assertFalse(view.active)
        before = view.read(["active", "arch", "write_date", "write_uid"])
        self.views._barani_vat_retire_legacy_preview_views()
        self.assertTrue(view.exists())
        self.assertEqual(view.read(["active", "arch", "write_date", "write_uid"]), before)
        result = self.env["account.move"].get_views([(False, "form")])
        arch = etree.fromstring(result["views"]["form"]["arch"].encode())
        buttons = arch.xpath('//button[@name="%s"]' % self.preview.id)
        self.assertEqual(len(buttons), 1)
        self.assertEqual(buttons[0].get("type"), "action")
        self.assertEqual(self.preview.report_type, "qweb-html")
        self.assertTrue(self.module_view.active)
