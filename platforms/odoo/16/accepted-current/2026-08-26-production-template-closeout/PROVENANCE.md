# Provenance and reconstruction

The production closeout action was intentionally tenant-bound and is not included here. It did not embed every full QWeb body: it read a proven baseline, performed single-occurrence replacements, checked the inverse transformation, and then checked exact target hashes.

The public snapshot was reconstructed from already committed accepted-current sources:

- the 16 July VAT and commercial body snapshots;
- the 30 June layouts, wrappers, Delivery Note, bridge, and Picking Operations snapshots.

The seven authorized QWeb transformations were:

1. VAT body: shipping gutter from 18 px to 10 mm and shipping shown whenever `partner_shipping_id` exists.
2. VAT external layout: company-registration gutter from 18 px to 10 mm.
3. Commercial external layout: company-registration gutter from 18 px to 10 mm.
4. Commercial body: shipping gutter from 18 px to 10 mm.
5. Delivery Note external layout: company-registration gutter from 18 px to 10 mm.
6. Delivery Note body: L2.1 to L2.2 marker, 10 mm shipping gutter, always-shipping policy, and fixed Scheduled Date / Operation / Source Order / Incoterms information table.
7. Picking Operations external layout: company-registration gutter from 18 px to 10 mm.

The four wrapper/body guards were unchanged. Every reconstructed character length, plain MD5,
and Odoo JSONB storage MD5 matches the production final verifier. The recorded plain SHA-256
values independently authenticate these exact reconstructed bytes; the live verifier did not
print plain SHA-256 values. The report-action contract was transcribed by logical role; tenant
numeric IDs were deliberately omitted.
