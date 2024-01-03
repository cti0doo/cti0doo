# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CountryStateCity(models.Model):
    _name = 'res.country.state.city'
    _description = 'State Cities'
   
    state_id = fields.Many2one('res.country.state', string='State', required=True)
    name = fields.Char(required=True)
    code = fields.Char(string='City code', required=True)


class CityZip(models.Model):
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


class Partner(models.Model):
    _inherit = 'res.partner'

    city_id = fields.Many2one('res.city', string='City Ref', ondelete='restrict', required=False)
    zip_id = fields.Many2one('res.city.zip', string='Zip Ref', ondelete='restrict', required=False)

    @api.onchange('city_id')
    def onchange_city(self):
        return {'value': {'state_id': self.city_id.state_id.id,
                          'city': self.city_id.name,
                          'country_id': self.city_id.state_id.country_id.id}}

    @api.onchange('zip_id')
    def onchange_zip(self):
        return {'value': {'city_id': self.zip_id.city_id.id,
                          'zip': self.zip_id.code,
                          'city': self.zip_id.city_id.name,
                          'state_id': self.zip_id.city_id.state_id.id,
                          'country_id': self.zip_id.city_id.state_id.country_id.id}}


class Bank(models.Model):
    _inherit = 'res.bank'

    city_id = fields.Many2one('res.city', string='City Ref', ondelete='restrict')
    zip_id = fields.Many2one('res.city.zip', string='Zip Ref', ondelete='restrict', required=False)
    
    @api.onchange('city_id')
    def onchange_city(self):
        return {'value': {'state': self.city_id.state_id.id,
                          'city': self.city_id.name,
                          'country_id': self.city_id.state_id.country_id.id}}

    @api.onchange('zip_id')
    def onchange_zip(self):
        return {'value': {'city_id': self.zip_id.city_id.id,
                          'zip': self.zip_id.code,
                          'city': self.zip_id.city_id.name,
                          'state_id': self.zip_id.city_id.state_id.id,
                          'country_id': self.zip_id.city_id.state_id.country_id.id}}


class Company(models.Model):
    _inherit = 'res.company'

    city_id = fields.Many2one('res.city', string='City Ref', ondelete='restrict')
    zip_id = fields.Many2one('res.city.zip', string='Zip Ref', ondelete='restrict', required=False)
    
    @api.onchange('city_id')
    def onchange_city(self):
        return {'value': {'state_id': self.city_id.state_id.id,
                          'city': self.city_id.name,
                          'country_id': self.city_id.state_id.country_id.id}}

    @api.onchange('zip_id')
    def onchange_zip(self):
        return {'value': {'city_id': self.zip_id.city_id.id,
                          'zip': self.zip_id.code,
                          'city': self.zip_id.city_id.name,
                          'state_id': self.zip_id.city_id.state_id.id,
                          'country_id': self.zip_id.city_id.state_id.country_id.id}}
