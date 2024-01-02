# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CityPostal(models.Model):
    _name = 'res.city.zip'
    _description = 'City Zips'
   
    city_id = fields.Many2one('res.city', string='City', required=True)
    code = fields.Char(string='Postal Code', required=True)
    type = fields.Selection(
        selection=[
            ('urban', 'Urban'),
            ('rural', 'Rural')],
        string='Type',
        required=True)
    name = fields.Char(string='ZIP', required=True)
