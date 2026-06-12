# C1 — Domestic Slovakia gross-paid down payment

Customer pays a gross down-payment amount. Odoo splits the amount into VAT base and Slovak VAT using a price-included down-payment tax.

Example for 100.00 EUR at 23%:

- base: 81.30
- VAT: 18.70
- total: 100.00

Final RI shows full supply and a negative down-payment deduction carrying negative VAT base and negative VAT.
