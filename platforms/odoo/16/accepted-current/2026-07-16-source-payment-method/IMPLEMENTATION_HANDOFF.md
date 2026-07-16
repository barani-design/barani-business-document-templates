# Implementation handoff

## Live records

```text
Commercial QWeb:
  view id: 2856
  key: barani_commercial.report_saleorder_document
  live characters: 25108
  UTF-8 bytes: 25112
  SHA-256: 1036d19c08a8e43d51757f436a127be1c7f59fcc01e7b057b4b9448b65d43840
  SHA-1: f232aefa8a0de53d95444b9b17f81d93fc5ebd86

VAT QWeb:
  view id: 2853
  key: barani_vat.report_invoice_document_vat
  live characters: 41872
  UTF-8 bytes: 41879
  SHA-256: 3bfa5ce69361a3bace52a9bd9ae1e13c75f389916a45c6c57261161b73b72636
  SHA-1: ac8c9602a0b50cfdae7d7d0396ad5a9892825f08
```

## Applied sequence

```text
S00  Captured exact pre-change QWeb and routing restore signatures.
S01  Added Q/SO/PF Source and compact Payment Method on one row.
S01A Allowed unrestricted Customer Ref. values to wrap in their own cell.
S01B Restored metadata typography to 10 pt and standardized Document Date.
S02  Aligned RI/DPI/Credit Note Source and Payment Method display.
S03  Read-only final verifier v5.
```

## Final marker state

```text
S00: PASS
S01: PASS
S01A: PASS
S01B: PASS
S02: PASS
```

## Rollback

`S99_RESTORE_BARANI_SOURCE_PAYMENT_METHOD_FROM_S00_SAFE.py` restores the exact
pre-S01/S02 commercial and VAT QWeb bytes captured by S00. It is emergency
rollback tooling only.

S99 does not rewrite business documents or stored references.
