from dateutil.relativedelta import relativedelta

from odoo import fields, models, api, _, Command
from odoo.tools import float_compare
from odoo.tools.misc import format_date
from odoo.exceptions import UserError, ValidationError


class loan(models.Model):
    _inherit = "account.loan"
    
    loan_type = fields.Selection(
        string="Type",
        selection=[
            ('lend', 'Lend'),
            ('borrow', 'Borrow'),
        ],
        default='lend',
        required=True,
        tracking=True,
    )
