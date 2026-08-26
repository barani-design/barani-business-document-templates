# Commercial template fragments — 2026-08-26 portable baseline

These four QWeb fragments represent the production-accepted commercial report state from the 26 August 2026 closeout.

The accepted tenant source contained a receiving IBAN/BIC and default EXW location. This portable copy replaces them with:

```text
XX0000000000000000000000
YOURBICXXX
YOUR_EXW_DEFAULT_LOCATION
```

Configure or parameterize those placeholders before deployment. Do not commit exports from a live database without reviewing them for bank details, customer data, internal identifiers, and production configuration.

The locked source and its hashes are in `../../accepted-current/2026-08-26-production-template-closeout/`. Existing installers may predate this source and must be reconciled before clean-database use.
