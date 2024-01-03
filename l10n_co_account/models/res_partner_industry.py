# -*- coding: utf-8 -*-

from odoo import models, fields

class resPartnerApply(models.Model):
    _inherit = 'res.partner.industry'

    ciiu_ids = fields.One2many('account.ciiu', 'industry_id', string='CIIU')
    line_ids = fields.One2many('account.ciiu.lines', 'industry_id', string='lines')
    default_tax_id = fields.Many2one('account.tax', string='Default Tax', required=False)
    type = fields.Selection([('mrp', 'Producer'), ('srv', 'Services'), ('mrk', 'Marketer')],
                            string='Type', default='mrk', required=True)
