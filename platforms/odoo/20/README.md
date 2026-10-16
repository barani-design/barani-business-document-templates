# Odoo 20 preparation

Purchase 20.0.1.0.3 is frozen, offline accepted and runtime HOLD. Its source and
[checkpoint](checkpoints/purchase-20261016/README.md) remain unchanged.

Three additional document source candidates, each 20.0.1.0.0, are prepared in
`addons/barani_commercial`, `addons/barani_delivery` and `addons/barani_vat`.
They include v20 adaptations and real Odoo tests, but runtime/PDF/business
acceptance is pending. See the [document checkpoint](checkpoints/documents-20261016/README.md)
and [remaining-work matrix](checkpoints/documents-20261016/V20_REMAINING_WORK.md).

This source-preparation branch does not change Odoo.sh parent gitlinks, existing
environments, Tax Rules .10 or real data. No go-live acceptance is implied.
