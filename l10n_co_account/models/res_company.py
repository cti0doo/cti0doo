# -*- coding: utf-8 -*-

import logging

from odoo import models, fields

# from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


class ResCompanyTaxes(models.Model):
    _inherit = 'res.company'
    #.   vat_type = fields.CHar(related='partner_id.vat_type',mstring='VD', readonly=True)
    #    vat_vd = fields.Char(related='partner_id.vat_vd', string='VD', readonly=True)
    #company_registry = fields.Char('Company Registry', related='partner_id.vat', size=64)
    retention = fields.Boolean(string='Apply UVT rule', default=False,
                               help='this option allows to indicate if the company applies withholding to the rest of the third party')
    company_resolution_ids = fields.One2many(
        'edi.resolution',
        'company_id',
        string='Resolutions'
    )
