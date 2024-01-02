from odoo import models, api, fields
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class Tax(models.Model):
    _inherit = 'account.tax'

    code_edi = fields.Char(
        string='Code',
        compute = 'compute_codes'
    )
    @api.depends('tax_group_id')
    def compute_codes(self):
        for tax in self:
            tax.code_edi = ''
            tax.description = ''
            if tax.tax_group_id:
                tax.code_edi = tax.tax_group_id.code_edi
                tax.description = tax.tax_group_id.description