# Content and publication notice

The files in this accepted-current package were inspected for:

```text
private keys
API tokens
password assignments
email addresses
customer names or customer documents
DDS business-field dependencies
compiled Python bytecode
```

No such credentials, customer records or bytecode are included.

The exact live QWeb snapshots do contain BARANI's receiving-bank identifiers
(IBAN/BIC) because those identifiers are part of the operational PDF validation
logic. They are payment instructions printed on BARANI customer documents, not
authentication credentials.

Do not describe this package as containing “no bank details.” It contains no
bank-login credentials, but it does contain the company receiving-bank
identifiers embedded in the accepted live templates.
