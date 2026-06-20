# Commercial Q/SO/PF tune sequence

The public Odoo 16 baseline installer is followed by these audited, dry-run-first
server actions:

1. `barani_commercial_q_so_pf_tune_L1_NOTES_CONTACT_EMAIL_TERMS_WIDTH_SAFE.py`
   — already present in the repository.
2. `barani_commercial_q_so_pf_tune_L2_4_HEADER_ADDRESS_UNIFY_RECONCILED_SAFE.py`
   — removes the duplicate centered title and aligns address-heading display.
3. `barani_commercial_q_so_pf_tune_L3_CORE_HARDENING_SAFE.py`
   — classifies cancelled orders as Quotations, makes the bank band PF-only,
   safely falls back from empty tax descriptions to tax names, and uses
   currency-aware unit-price/rounding logic.

Run every write-capable action first with its apply flag disabled and review the
full dry-run output. The extracted XML under `templates/commercial/` represents
the public-sanitized post-L3 state.

The next planned policy release is intentionally separate; see
`C1-commercial-policy-decisions-next.md`.
