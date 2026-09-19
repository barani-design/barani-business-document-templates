"""Preserve the existing native action configuration for a controlled uninstall."""
import json

from odoo.exceptions import UserError

ACTION = 'purchase.action_report_purchase_order'
ROUTE = 'barani_purchase.report_purchaseorder'
BACKUP_XMLID = 'barani_purchase.original_purchase_report_action'
BACKUP_KEY = 'barani_purchase.original_purchase_report_action'
FIELDS = ('report_name', 'report_file', 'paperformat_id', 'print_report_name')


def pre_init_hook(env):
    report = env.ref(ACTION).with_context(lang=None)
    if report.model != 'purchase.order' or report.report_type != 'qweb-pdf':
        raise UserError('BARANI Purchase: the native Purchase Order action has an unexpected model or type.')
    if report.report_name != 'purchase.report_purchaseorder':
        raise UserError('BARANI Purchase: another PO report route is already active. Review it before installation: %s' % report.report_name)
    if report.attachment_use:
        raise UserError('BARANI Purchase: cached PO attachments are enabled. Review this configuration before installation.')
    if env.ref(BACKUP_XMLID, raise_if_not_found=False) or env['ir.config_parameter'].sudo().search_count([('key', '=', BACKUP_KEY)]):
        raise UserError('BARANI Purchase: a previous report-action backup exists; review it before reinstalling.')
    values = {name: report[name] for name in FIELDS if name != 'paperformat_id'}
    values['paperformat_id'] = report.paperformat_id.id or False
    backup = env['ir.config_parameter'].sudo().create({
        'key': BACKUP_KEY, 'value': json.dumps({'action_id': report.id, 'values': values}),
    })
    env['ir.model.data'].sudo().create({
        'module': 'barani_purchase', 'name': 'original_purchase_report_action',
        'model': 'ir.config_parameter', 'res_id': backup.id, 'noupdate': True,
    })


def uninstall_hook(env):
    report = env.ref(ACTION, raise_if_not_found=False)
    backup = env.ref(BACKUP_XMLID, raise_if_not_found=False)
    # A later customization owns its own route; never overwrite it on uninstall.
    if not report or report.report_name != ROUTE:
        return
    if not backup:
        raise UserError('BARANI Purchase: original report-action backup is missing. Restore the native action before uninstalling.')
    snapshot = json.loads(backup.sudo().value)
    if snapshot['action_id'] != report.id:
        raise UserError('BARANI Purchase: report-action identity changed; review before uninstalling.')
    values = snapshot['values']
    if values['paperformat_id'] and not env['report.paperformat'].browse(values['paperformat_id']).exists():
        values['paperformat_id'] = False
    report.with_context(lang=None).write(values)
