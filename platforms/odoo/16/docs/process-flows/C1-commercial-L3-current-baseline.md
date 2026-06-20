# C1 — Commercial Q/SO/PF post-L3 current baseline

## Status

This is the public-sanitized representation of the tested Odoo 16 commercial
report state after Tune L2.4 and Tune L3.

## Implemented and validated

- standalone BARANI QWeb body, layout, and wrappers;
- no stock sale-body, DDS, Studio, or patched tax-total template calls;
- right-side-only document title and number;
- red `Customer:` and `Shipping Address:` headings;
- customer/shipping telephone, email, ID, and VAT display;
- visible Notes heading and wider Payment Terms area;
- cancelled sale orders remain Quotations;
- downloaded Q/SO action classifies cancelled records as Quotations;
- bank-transfer band appears only on Pro-Forma;
- tax description falls back safely to tax name;
- unit price uses the document currency's monetary formatting;
- global VAT-rounding warning uses the currency's `is_zero()` logic.

## Rendering evidence

The private deployment was tested with:

- ordinary Quotations;
- confirmed Sales Orders;
- Pro-Forma documents;
- cancelled Quotations using compact and slash-based references;
- 0%, 19%, 20%, and 23% taxes;
- discounts and down-payment sections;
- separate shipping addresses;
- a real EUR global-rounding difference.

No customer PDFs or production record identifiers are included in this public
repository.

## Public sanitization

Receiving-bank identifiers are placeholders. Tenant-specific EORI and numbering
assumptions remain documented limitations pending the next policy release.

## Deliberately deferred to the next release

- `partner_invoice_id` / `partner_shipping_id` as strict address sources;
- fail-loud required-address validation;
- Incoterm location and configurable EXW default;
- one always-visible ten-column line table;
- explicit English-only report context;
- one shared transformation for visible and downloaded Q/SO/PF numbers;
- configurable bank, EORI, numbering, and payment-band policy.
