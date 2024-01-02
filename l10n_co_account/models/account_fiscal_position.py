# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    ei_code = fields.Selection(
        selection=[
            ('00', 'Simplificado'),
            ('02', 'Común'),
            ('03', 'No aplicable'),
            ('04', 'Simple'),
            ('05', 'Ordinario')
        ],
        string='Code DIAN',
        required=False
    )

    ei_big_contribuitor = fields.Boolean(
        string='Gran contribuyente'
    )

#class AccountFiscalPositionTemplate(models.Model):
#    _inherit = "account.fiscal.position.template"

#    ei_code = fields.Selection(
#        selection=[
#            ('00', 'Simplificado'),
#            ('02', 'Común'),
#            ('03', 'No aplicable'),
#            ('04', 'Simple'),
#            ('05', 'Ordinario')
#        ],
#        string='Code DIAN',
#        required=False
#    )

 #   ei_big_contribuitor = fields.Boolean(
 #       string='Big Contribuitor'
 #   )
