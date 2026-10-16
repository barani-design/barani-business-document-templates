"""Save the existing RFQ action before the upgrade changes its report route."""
from odoo import SUPERUSER_ID, api
from odoo.addons.barani_purchase.hooks import backup_rfq_action


def migrate(cr, version):
    backup_rfq_action(api.Environment(cr, SUPERUSER_ID, {}))
