# Validation summary

## Automated production acceptance

The independent read-only final verifier passed on 26 August 2026. Its sanitized result was:

- all eleven QWeb views were exact `TARGET` or intentionally `UNCHANGED_GUARD` values;
- all eleven report actions matched the accepted labels, routes, paper formats, bindings, groups, and filename expressions;
- the stock Print menu matched the three-item target;
- all six report-route sets and Invoice Preview resolution passed;
- invoice, credit-note, commercial, pro-forma, Delivery Note, delivery bridge, and Picking Operations HTML renders passed;
- the Delivery Note controls passed for same-address, Incoterms, and sale-less cases;
- no writes were made by the verifier and rollback was not authorized.

Private database identity, record IDs, restore evidence, backup evidence, and document numbers are intentionally omitted here.

## Manual PDF acceptance

Production PDFs were reviewed for two complementary sales scenarios:

- billing and shipping represented distinct contacts at the same physical location;
- shipping used a different company and address from billing.

For each scenario, Invoice, Sales Order, Pro-Forma Invoice, Delivery Note, and Picking Operations output was visually checked. The PDFs contained live customer data and are not included in this repository.

## Offline repository acceptance

Run from this milestone directory:

```bash
python3 validate_snapshot.py
sha256sum -c MANIFEST_SHA256.txt
```

The validator checks XML parsing, exact production hashes, metadata structure, required semantic tokens, and the deterministic portable-source substitutions.
