# Sanitization report — 2026-06-30 accepted-current package

Source inputs:

- `Pasted text.txt` — E02 page 1, private raw output.
- `Pasted text (2).txt` — E02 page 2, private raw output.

Parsed records:

```text
QWeb views: 14
Report actions: 5
Paperformats: 4
XML parse errors after sanitization: 0
```

XML parse status: PASS

Sensitive literal replacements applied:

```text
confirmed compact receiving-bank IBAN literal -> XX0000000000000000000000
confirmed spaced receiving-bank IBAN literal -> XX00 0000 0000 0000 0000 0000
confirmed receiving-bank BIC literal -> YOURBICXXX
confirmed tenant EXW default-location literal -> YOUR_EXW_DEFAULT_LOCATION
```

The raw private E02 output is intentionally excluded from this package.
