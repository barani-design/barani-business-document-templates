# Sanitization notes

This public repository is intended to contain reusable document-template logic and sanitized example scripts.

Do not commit:

- customer PDFs or screenshots with live data;
- personal or unreviewed IBAN/BIC values;
- real customer names, phone numbers, emails, or addresses;
- live Odoo XML exports or restore-point dumps;
- POHODA exports/imports;
- API keys, credentials, or database dumps.

Use placeholders such as:

- `XX00 0000 0000 0000 0000 0000` for IBAN;
- `YOURBICXXX` for BIC;
- `Example Company Ltd.` for company identity;
- `INV-EXAMPLE`, `DPI-EXAMPLE`, and `SO-EXAMPLE` for document numbers.

Maintained reusable templates must use placeholders. A locked accepted-current snapshot may retain reviewed BARANI receiving-bank identifiers or dispatch instructions only when they are already public business-document content and the snapshot has an explicit publication notice. Such an exception never permits bank-login credentials, statements, customer data, or private production evidence.
