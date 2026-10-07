# -*- coding: utf-8 -*-
{
    "name": "BARANI delivery note and picking documents",
    "summary": "Delivery note and picking operations layout used by BARANI",
    "version": "19.0.1.0.6",
    "category": "Accounting/Accounting",
    "license": "LGPL-3",
    "author": "BARANI DESIGN Technologies s.r.o.",
    "website": "https://www.baranidesign.com",
    "depends": ['sale_stock'],
    "data": [
        "data/report_metadata.xml",
        "report/external_layout_delivery_2026.xml",
        "report/external_layout_picking_operations_2026.xml",
        "report/report_delivery_note_2026.xml",
        "report/report_picking_operations_2026.xml",
        "report/report_sale_order_delivery_note_2026.xml",
        "data/core_report_overrides.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
