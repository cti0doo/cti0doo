# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api

# from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


class res_partner(models.Model):
    _inherit = 'res.partner'

    retention = fields.Boolean(string='Apply UVT rule', default=False)

    """Document type: Lista de selección con los tipos de documento aceptados
       por la autoridad de impuestos (DIAN).
        11 - Registro civil
        12 - Tarjeta de identidad
        13 - Cédula de ciudadanía
        21 - Tarjeta de extranjería
        22 - Cédula de extranjería
        31 - NIT (Número de identificación tributaria)
        41 - Pasaporte
        42 - Tipo de documento extranjero
        43 - Para uso definido por la DIAN

        http://www.dian.gov.co/descargas/normatividad/Factura_Electronica/Anexo_001_R14465.pdf"""

    stock_holder = fields.Selection([
        ('sh', 'Stock holder'),
        ('nsh', 'No Stock holder')
    ], 'Stock holder', default='nsh', required=True)
    ciiu_id = fields.Many2one('account.ciiu', string='CIIU')
    retention_apply = fields.Selection([('na', 'Not apply'), ('fa', 'Force apply'), ('ta', 'Apply')],
                                       string='Retention apply?', default='ta', required=True)

    def write(self, vals):
        for record in self:
            if record.child_ids:
                for child in record.child_ids:
                    if vals.get('customer') is not None:
                        child.customer = vals.get('customer')
                    if vals.get('supplier') is not None:
                        child.supplier = vals.get('supplier')
                    if vals.get('stock_holder') is not None:
                        child.stock_holder = vals.get('stock_holder', child.stock_holder)
        return super(res_partner, self).write(vals)
