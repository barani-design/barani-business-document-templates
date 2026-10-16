"""Actual native QWeb/ORM registration coverage; never a runtime result by itself."""
from lxml import html
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'barani_reports')
class TestStoredRegistrationIdentifiers(TransactionCase):
    def _partner(self, name, registry=None, vat=None):
        return self.env['res.partner'].with_context(no_vat_validation=True).create({
            'name': name, 'is_company': True, 'country_id': False, 'vat': vat,
            'additional_identifiers': {'OTHER': registry} if registry else {},
        })

    def _render(self, partner, fallback=False):
        return html.fromstring('<div>' + str(self.env['ir.qweb']._render(
            'barani_delivery.registration_identifiers', {
                'identifier_partner': partner, 'identifier_fallback': fallback,
                'identifier_name': 'registration_test',
            })) + '</div>')

    def test_stored_enterprise_number_does_not_use_vat(self):
        partner = self._partner('Identifier fixture', 'REG-2001', 'US123456789')
        before = partner.read(['additional_identifiers', 'vat', 'write_date'])[0]
        text = self._render(partner).text_content()
        self.assertIn('REG-2001', text)
        self.assertNotIn('US123456789', text)
        self.assertEqual(before, partner.read(['additional_identifiers', 'vat', 'write_date'])[0])

    def test_blank_identifier_does_not_invent_a_registration(self):
        partner = self._partner('VAT-only fixture', vat='US123456789')
        self.assertFalse(self._render(partner).xpath('//*[@name="registration_test"]'))

    def test_explicit_fallback_and_primary_precedence(self):
        primary = self._partner('Primary fixture')
        fallback = self._partner('Fallback fixture', 'REG-FALLBACK')
        self.assertIn('REG-FALLBACK', self._render(primary, fallback).text_content())
        primary.additional_identifiers = {'OTHER': 'REG-PRIMARY'}
        text = self._render(primary, fallback).text_content()
        self.assertIn('REG-PRIMARY', text)
        self.assertNotIn('REG-FALLBACK', text)

    def test_identifiers_are_escaped(self):
        partner = self._partner('Escaping fixture', '<script>REG-XSS</script>')
        rendered = self._render(partner)
        self.assertFalse(rendered.xpath('.//script'))
        self.assertIn('REG-XSS', rendered.text_content())
