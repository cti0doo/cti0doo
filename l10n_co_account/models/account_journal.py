# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    payment_option_id = fields.Many2one('payment.option', string='Payment Option Default', required=False)
    city_id = fields.Many2one('res.city', string='City', required=False)
    city_mrp_id = fields.Many2one('res.city', string='City (MRP)', required=False)
#    resolution_id = fields.Many2one('edi.resolution', string='Edi Resolution', required=False)