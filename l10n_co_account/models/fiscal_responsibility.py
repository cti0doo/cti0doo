# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class Fiscalresponsibility(models.Model):
    _name = 'fiscal.responsibility'
    _description = 'Fiscal Responsibilities'
    _rec_name = 'description'

    code = fields.Char(string='Edi Code')
    description = fields.Char(string='Description')

#    ei_accredited_company = fields.Boolean(
#        string='Edi Company',
#        compute='compute_ei_accredited_company',
#        store=False,
#        copy=False
#    )

#   @api.depends('code')
#    def compute_ei_accredited_company(self):
#        for record in self:
#            record.ei_accredited_company = self.env.company.ei_invoice_enable

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.description))
        return result
