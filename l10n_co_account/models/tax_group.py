from odoo import models, api, fields
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class TaxGroup(models.Model):
    _inherit = 'account.tax.group'

    code_edi = fields.Char(
        string='Code',
        required = False
    )
    technical_name = fields.Char(
        string='Tecnical Name',
        required = False
    )
    description = fields.Char(
        string='Description',
        required = False
    )
    retention = fields.Boolean(
        string=u'Retention',
        required = False
    )




