# Configuration placeholders and public-sanitization rules

This public package intentionally replaces production-specific constants with placeholders. Before running installers on a real database, update the constants near the top of the scripts.

## Required placeholders

| Placeholder | Meaning | Example format |
|---|---|---|
| `__RECEIVING_IBAN_DISPLAY__` | Receiving account IBAN shown in PDFs | `__IBAN_PLACEHOLDER__` |
| `__RECEIVING_IBAN_COMPACT__` | Same IBAN without spaces for exact matching | `__IBAN_PLACEHOLDER__` |
| `__RECEIVING_BIC__` | Receiving bank BIC/SWIFT | `ABCDEFGHXXX` |
| `__COMPANY_NAME__` | Company name, if hard-coded in any example output | normally read from Odoo |
| `__COMPANY_REGISTRY_ID__` | Company registration ID, if hard-coded in docs | normally read from Odoo |
| `__COMPANY_TAX_ID__` | Company tax ID, if hard-coded in docs | normally read from Odoo |
| `__COMPANY_VAT_ID__` | Company VAT ID, if hard-coded in docs | normally read from Odoo |

The templates are designed to read company/customer identity from Odoo records. Hard-coded bank constants are used only to guard against accidentally printing the wrong receiving bank.

## Never publish

- customer PDFs or invoices;
- live DB exports containing customer names, addresses, emails, phone numbers, invoice numbers, or payments;
- production restore-point config-parameter dumps;
- real API keys, Odoo credentials, or banking credentials.
