# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountInvoiceLineDistribution(models.Model):
    _name = 'account.invoice.line.distribution'
    _description = "Distribution Line of Vendor Bill Line"
    _rec_name = 'company_id'

    @api.model
    def _get_default_company_id(self):
        company_id = self.env.context.get('company_id')
        return (company_id or
                self.invoice_line_id.company_id.id or
                self.invoice_line_id.invoice_id.company_id.id or
                self.env.user.company_id.id)

    percent = fields.Float(string="Percentage", default=0.00)
    amount = fields.Float(string="Amount", default=0.00)
    invoice_line_id = fields.Many2one('account.invoice.line',
                                      string="Bill Line", readonly=True,
                                      required=True, ondelete="cascade")
    company_id = fields.Many2one('res.company', string="Company",
                                 required=True,
                                 default=_get_default_company_id)

    _sql_constraints = \
        [('line_company_uniq', 'UNIQUE (invoice_line_id, company_id)',
          'You cannot have the same company twice in a distribution!')]

    @api.onchange('percent', 'invoice_line_id.price_subtotal')
    def onchange_percent_total(self):
        for dist_id in self:
            dist_id.amount = dist_id.invoice_line_id.\
                price_subtotal*dist_id.percent/100

    @api.onchange('amount', 'invoice_line_id.price_subtotal')
    def onchange_amount_total(self):
        for dist_id in self:
            if dist_id.invoice_line_id.price_subtotal != 0.00:
                dist_id.percent = dist_id.amount/dist_id.\
                    invoice_line_id.price_subtotal*100
            else:
                dist_id.percent = 0.00
