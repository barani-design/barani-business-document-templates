"""Preserve the existing native action configuration for a controlled uninstall."""
import json

from odoo.exceptions import UserError

ACTION = 'purchase.action_report_purchase_order'
ROUTE = 'barani_purchase.report_purchaseorder'
BACKUP_XMLID = 'barani_purchase.original_purchase_report_action'
BACKUP_KEY = 'barani_purchase.original_purchase_report_action'
FIELDS = ('report_name', 'report_file', 'paperformat_id', 'print_report_name')
RFQ_ACTION = 'purchase.report_purchase_quotation'
RFQ_ROUTE = 'barani_purchase.report_purchasequotation'
RFQ_BACKUP_XMLID = 'barani_purchase.original_rfq_report_action'
RFQ_BACKUP_KEY = RFQ_BACKUP_XMLID


def _backup_action(env, action_xmlid, native_route, backup_xmlid, backup_key):
    report = env.ref(action_xmlid).with_context(lang=None)
    if report.model != 'purchase.order' or report.report_type != 'qweb-pdf':
        raise UserError('BARANI Purchase: report action %s has an unexpected model or type.' % action_xmlid)
    if report.report_name != native_route:
        raise UserError('BARANI Purchase: another report route is already active for %s. Review it before installation or upgrade: %s' % (action_xmlid, report.report_name))
    if report.attachment_use:
        raise UserError('BARANI Purchase: cached attachments are enabled for %s. Review this configuration before installation or upgrade.' % action_xmlid)
    if env.ref(backup_xmlid, raise_if_not_found=False) or env['ir.config_parameter'].sudo().search_count([('key', '=', backup_key)]):
        raise UserError('BARANI Purchase: a previous report-action backup exists for %s; review it before reinstalling.' % action_xmlid)
    values = {name: report[name] for name in FIELDS if name != 'paperformat_id'}
    values['paperformat_id'] = report.paperformat_id.id or False
    backup = env['ir.config_parameter'].sudo().create({
        'key': backup_key, 'value': json.dumps({'action_id': report.id, 'values': values}),
    })
    env['ir.model.data'].sudo().create({
        'module': 'barani_purchase', 'name': backup_xmlid.split('.', 1)[1],
        'model': 'ir.config_parameter', 'res_id': backup.id, 'noupdate': True,
    })


def backup_rfq_action(env):
    # Also used by the pre-upgrade script: pre_init_hook is not run on upgrade.
    _backup_action(env, RFQ_ACTION, 'purchase.report_purchasequotation',
                   RFQ_BACKUP_XMLID, RFQ_BACKUP_KEY)


def pre_init_hook(env):
    _backup_action(env, ACTION, 'purchase.report_purchaseorder', BACKUP_XMLID, BACKUP_KEY)
    backup_rfq_action(env)


def _restore_action(env, action_xmlid, route, backup_xmlid):
    report = env.ref(action_xmlid, raise_if_not_found=False)
    backup = env.ref(backup_xmlid, raise_if_not_found=False)
    # A later customization owns its own route; never overwrite it on uninstall.
    if not report or report.report_name != route:
        return
    if not backup:
        raise UserError('BARANI Purchase: original report-action backup is missing for %s. Restore the native action before uninstalling.' % action_xmlid)
    snapshot = json.loads(backup.sudo().value)
    if snapshot['action_id'] != report.id:
        raise UserError('BARANI Purchase: report-action identity changed; review before uninstalling.')
    values = snapshot['values']
    if values['paperformat_id'] and not env['report.paperformat'].browse(values['paperformat_id']).exists():
        values['paperformat_id'] = False
    report.with_context(lang=None).write(values)


def uninstall_hook(env):
    _restore_action(env, ACTION, ROUTE, BACKUP_XMLID)
    _restore_action(env, RFQ_ACTION, RFQ_ROUTE, RFQ_BACKUP_XMLID)
