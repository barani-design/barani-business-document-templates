# Content and publication notice

This public milestone contains reviewed template source and non-secret technical metadata. It contains no customer documents, customer identities, live database export, database name or UUID, backup filename or hash, restore namespace, credentials, API tokens, private keys, or production execution transcript.

The exact accepted QWeb snapshot retains BARANI's receiving-bank identifiers and default EXW dispatch location because they are public business payment/delivery instructions embedded in the operational report logic. They are not bank-login credentials. The reusable files under `platforms/odoo/16/templates/` replace those constants with:

```text
XX0000000000000000000000
YOURBICXXX
YOUR_EXW_DEFAULT_LOCATION
```

Use the portable files for reuse and future migration. Keep the exact accepted snapshot immutable as evidence of the production behavior that was verified.
