# C1 — Commercial Q/SO/PF 2026+ flow

## Goal

Render Quotation, Sales Order, and Pro-forma documents from `sale.order` using a standalone BARANI-owned report family. The report must not inherit from `sale.report_saleorder_document`, `web.external_layout`, or DDS/Studio-patched templates.

## Flow

```text
sale.order
  |
  +--> Print: Quotation / Order — 2026+
  |       ir.actions.report report_name=barani_commercial.report_saleorder
  |       wrapper: barani_commercial.report_saleorder
  |
  +--> Print: PRO-FORMA — 2026+
          ir.actions.report report_name=barani_commercial.report_saleorder_proforma
          wrapper: barani_commercial.report_saleorder_proforma

wrappers
  -> barani_commercial.report_saleorder_document
  -> barani_commercial.external_layout_standard_titled
  -> BARANI Commercial A4 7mm paperformat
````

## Current package artifact

Use `installers/commercial/barani_commercial_q_so_pf_report_installer_Q-SO-PF-2026v4_PUBLIC_SANITIZED_DRYRUN_SAFE.py`. This public v4 combines the production commercial installer with Tune L1:

- customer/shipping Tel + Email;
- visible `Notes` heading above `sale.order.note`;
- wider Payment Terms column;
- standalone DDS-free report chain.

## Validation cases

- draft quotation;
- confirmed sales order;
- pro-forma from draft quotation;
- customer with separate shipping address;
- long payment terms;
- notes with long HTML text;
- mixed products/services;
- discounts and multi-tax order.
