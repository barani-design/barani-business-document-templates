# Audit — BARANI_DELIVERY_NOTE_2026_BASELINE_KIT update to DN L1 QR-only DDS-free

## Baseline audit findings

1. **Good baseline architecture:** standalone body view, standalone custom layout, dedicated paperformat, and separate `stock.picking` report action. This matches the isolated BARANI invoice-report pattern.
2. **QR placement was already delivery-note scoped:** the baseline used product QR codes in the delivery-note line table from `product_id.barcode`.
3. **EORI issue fixed:** the baseline printed `EORI` by reusing `company.vat`. That is not a safe legal/data assumption. DN L1 removes EORI entirely until a real source field is confirmed.
4. **Optional field guard issue fixed:** the baseline used QWeb expressions such as `'sale_id' in o`, `'carrier_id' in o`, and `'user_id' in o`. These are brittle in QWeb. DN L1 removes those membership tests, requires `sale_id` in the installer field preflight, and drops optional carrier display for L1.
5. **DDS bypass strengthened:** DN L1 adds explicit self-checks that no `dds_` or `brn_` strings exist in the body/layout templates.
6. **Invoice-only content remains excluded:** no unit price, VAT, totals, payment reference, IBAN, due date, or bank-transfer band is present in the delivery note.
7. **Kit grouping deliberately deferred:** the delivery note prints native picking moves flat in L1. Parent kit + indented components remains DN L2 after real picking samples are tested.

## Latest plan encoded in package

- Use **DN** as the English report-family acronym for Delivery Note.
- Use **DL** only as a Slovak-language synonym for *Dodací list* if we later add bilingual title text.
- QR codes are used only on the Delivery Note, not on Q/SO/PF.
- Do not rebuild DDS Update Delivered Quantity.
- Keep the delivery report read-only/presentation-only.
- Preserve DDS/brn historical data separately before DDS uninstall, but do not read it in the report.

## Open DN L2 items

- Test real phantom-kit pickings and inspect whether `stock.move.sale_line_id`, BoM line, or related origin fields can reliably group components under the kit sale-order line.
- Decide whether customers need a parent kit row on the DN or whether the flat component list is sufficient.
- Add carrier/incoterm fields only after confirming exact installed fields and customer-facing usefulness.
- Add EORI only after confirming the real source field; never derive it from VAT by display convention.

## Package hygiene update

- Historical VAT reference removed from the kit to keep DN L1 clean and avoid accidental reuse of invoice-only logic such as IBAN/payment bands, VAT totals, or EORI-from-VAT display.
