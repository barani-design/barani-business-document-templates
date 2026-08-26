# Odoo 16 maintained template sources

These eleven QWeb files are the portable source mirror of the production-accepted 26 August 2026 template closeout.

| Family | Views |
|---|---:|
| VAT invoices and credit notes | 2 |
| Quotations, sales orders and pro-formas | 4 |
| Delivery Notes | 3 |
| Picking Operations | 2 |

The locked behavioral baseline, exact hashes, report-action contract, paper formats, and offline validator are in:

```text
../accepted-current/2026-08-26-production-template-closeout/
```

The maintained files intentionally substitute three portable constants:

```text
XX0000000000000000000000
YOURBICXXX
YOUR_EXW_DEFAULT_LOCATION
```

Replace or parameterize them in a controlled installer for the target tenant. Do not paste a live database export over these files without a customer-data and credential review.

The existing Odoo 16 installers predate parts of the accepted closeout. Treat this directory and the accepted-current milestone as the source of truth; revalidate any installer before using it on a clean database.
