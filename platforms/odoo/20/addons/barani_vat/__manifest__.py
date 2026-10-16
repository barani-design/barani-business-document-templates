# -*- coding: utf-8 -*-
{
    "name": "BARANI VAT invoice documents",
    "summary": "Customer invoice and credit note layout used by BARANI",
    "version": "20.0.1.0.0",
    "category": "Accounting/Accounting",
    "license": "LGPL-3",
    "author": "BARANI DESIGN Technologies s.r.o.",
    "website": "https://www.baranidesign.com",
    "depends": ['sale_stock'],
    "data": [
        "report/registration_identifiers.xml",
        "data/report_metadata.xml",
        "report/external_layout_standard_titled.xml",
        "report/report_invoice_document_vat.xml",
        "data/core_report_overrides.xml",
        "data/legacy_preview_views.xml",
        "views/account_move_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
