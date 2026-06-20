# Commercial template fragments — post-L3 public baseline

These four QWeb fragments represent the audited post-L3 commercial report state.

The live tenant source contained a receiving IBAN and BIC. This public copy
replaces them with:

```text
__RECEIVING_IBAN_COMPACT__
__RECEIVING_BIC__
```

Configure or replace those placeholders before deployment. Do not commit
exports from a live database without reviewing them for bank details, customer
data, internal identifiers, and production configuration.

The current baseline intentionally precedes the next approved policy changes
for strict invoice/shipping address sourcing, EXW location, fixed ten-column
geometry, English-only rendering, and unified displayed/downloaded numbers.
