# C2-edge — VAT/accounting edge-case matrix

Use this matrix after any VAT template change.

## Document cases

- draft invoice;
- posted RI;
- posted DPI;
- final RI with down-payment deduction;
- credit note;
- EU reverse charge / 0%;
- export / 0%;
- mixed VAT-rate invoice;
- foreign currency invoice;
- long customer/shipping address;
- missing phone/email;
- invoice with notes/narration.

## Checks

- title and document number;
- VAT Base / VAT columns;
- total excl. VAT / total VAT / total incl. VAT;
- balance due / amount credited;
- bank band hidden for credit notes;
- payment reference policy;
- no DDS text dependency such as `Advanced Invoice:`;
- no customer-specific data in public exports.
