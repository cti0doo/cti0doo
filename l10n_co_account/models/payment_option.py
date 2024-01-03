# coding: utf-8
from odoo import fields, models


class PaymentOptions(models.Model):
    _name = 'payment.option'
    _description = 'Payment Option'

    code = fields.Char(string="Code")
    name = fields.Char(string="Payment Option")
    payment_type = fields.Selection(selection=[('inbound', 'Inbound'), ('outbound', 'Outbound')], required=True)

