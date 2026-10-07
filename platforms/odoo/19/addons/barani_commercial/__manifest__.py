# -*- coding: utf-8 -*-
{
    "name": "BARANI quotation and pro-forma documents",
    "summary": "Quotation, sales order and pro-forma layout used by BARANI",
    "version": "19.0.1.0.2",
    "category": "Accounting/Accounting",
    "license": "LGPL-3",
    "author": "BARANI DESIGN Technologies s.r.o.",
    "website": "https://www.baranidesign.com",
    "depends": ['sale_stock'],
    "data": [
        "data/report_metadata.xml",
        "report/external_layout_standard_titled.xml",
        "report/report_saleorder.xml",
        "report/report_saleorder_document.xml",
        "report/report_saleorder_proforma.xml",
        "data/core_report_overrides.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
