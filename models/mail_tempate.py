from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class MailTemplate(models.Model):
    _inherit = "mail.template"

    property_printing_action_id = fields.Many2one(
        comodel_name='printing.action',
        string='Action',
        company_dependent=True,
    )
    report_copies = fields.Integer(
        string="# Copies",
        default=1,
    )
    printing_printer_id = fields.Many2one(
        comodel_name='printing.printer',
        string='Printer'
    )
    printing_action_ids = fields.One2many(
        comodel_name='printing.report.template.action',
        inverse_name='report_id',
        string='Actions',
        help='This field allows configuring action and printer on a per '
             'user basis'
    )

    @api.model
    def print_action_for_report_name(self, report_name):
        """ Returns if the action is a direct print or pdf

        Called from js
        """
        template = self.get_email_template(report_name)
        if not template:
            return {}
        result = template.behaviour()[template.id]
        serializable_result = {
            'action': result['action'],
            'printer_name': result['printer'].name,
        }
        return serializable_result

    @api.multi
    def behaviour(self):
        result = {}
        printer_obj = self.env['printing.printer']
        printing_act_obj = self.env['printing.report.template.action']
        # Set hardcoded default action
        default_action = 'client'
        # Retrieve system wide printer
        default_printer = printer_obj.get_default()

        # Retrieve user default values
        user = self.env.user
        if user.printing_action:
            default_action = user.printing_action
        if user.printing_printer_id:
            default_printer = user.printing_printer_id

        for report in self:
            action = default_action
            printer = default_printer

            # Retrieve report default values
            report_action = report.property_printing_action_id
            if report_action and report_action.action_type != 'user_default':
                action = report_action.action_type
            if report.printing_printer_id:
                printer = report.printing_printer_id

            # Retrieve report-user specific values
            print_action = printing_act_obj.search(
                [('report_id', '=', report.id),
                 ('user_id', '=', self.env.uid),
                 ('action', '!=', 'user_default')],
                limit=1)
            if print_action:
                user_action = print_action.behaviour()
                action = user_action['action']
                if user_action['printer']:
                    printer = user_action['printer']

            result[report.id] = {'action': action,
                                 'printer': printer,
                                 }
        return result