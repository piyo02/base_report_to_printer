from odoo import models, fields, api


class PrintingReportXmlAction(models.Model):
    _name = 'printing.report.template.action'
    _description = 'Printing Report Printing Actions'

    report_id = fields.Many2one(comodel_name='mail.template',
                                string='Report',
                                required=True,
                                ondelete='cascade')
    user_id = fields.Many2one(comodel_name='res.users',
                              string='User',
                              required=True,
                              ondelete='cascade')
    action = fields.Selection(
        selection=lambda s: s.env['printing.action']._available_action_types(),
        required=True,
    )
    printer_id = fields.Many2one(comodel_name='printing.printer',
                                 string='Printer')

    @api.multi
    def behaviour(self):
        if not self:
            return {}
        return {
            'action': self.action,
            'printer': self.printer_id,
        }
