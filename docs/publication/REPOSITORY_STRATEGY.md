# Repository strategy

Recommendation: use a single public repository for the business-document family, with version-specific implementations under `platforms/`.

## Recommended structure

```text
platforms/odoo/16/
platforms/odoo/19/
docs/process-flows/
docs/publication/
examples/
```

## Why one repo

- Shared business flows: RI/DPI, Q/SO/PF, delivery notes, pick lists.
- Shared accounting concepts: gross-paid down payments, VAT reconciliation, fiscal positions.
- Easier cross-version comparison when porting from Odoo 16 to Odoo 19.
- One public documentation site / README.

## When to split later

Split into separate repositories if:

- Odoo 19 becomes a packaged module with independent releases.
- The code diverges so strongly that shared docs are no longer useful.
- Different licenses or maintainers are needed.
