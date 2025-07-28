from dateutil.relativedelta import relativedelta

from odoo import models, fields, _, api
from odoo.tools.misc import format_date
from odoo.exceptions import ValidationError

from ..lib import pylandb


class AccountLoanComputeWizard(models.TransientModel):
    _inherit = 'account.loan.compute.wizard'
    _description = 'Loan Compute Wizard'

    loan_term_unit = fields.Selection(
        string='Loan Term Unit',
        selection=[
            ('year', 'Year(s)'),
            ('month', 'Month(s)'),
        ],
        default='month',
        required=True,
    )

    # Onchange
    @api.onchange('loan_amount', 'interest_rate', 'loan_term', 'loan_term_unit', 'start_date', 'first_payment_date')
    def _onchange_preview(self):
        if self.loan_amount < 0:
            raise ValidationError(_("Loan Amount must be positive"))
        if self.interest_rate < 0 or self.interest_rate > 100:
            raise ValidationError(_("Interest Rate must be between 0 and 100"))
        if self.loan_term < 0:
            raise ValidationError(_("Loan Term must be positive"))
        if self.loan_term_unit == 'year':
            grace = self.loan_term * 12
        else:
            grace = self.loan_term

        if self.first_payment_date and self.start_date + relativedelta(months=grace) < self.first_payment_date:
            raise ValidationError(_("The First Payment Date must be before the end of the loan."))

    # Compute
    def _get_loan_payment_schedule(self):
        self.ensure_one()
        loan = pylandb.Loan(
            loan_amount=self.loan_amount,
            interest_rate=self.interest_rate,
            loan_term=self.loan_term,
            loan_term_unit=self.loan_term_unit,
            start_date=format_date(self.env, self.start_date, date_format='yyyy-MM-dd'),
            first_payment_date=format_date(self.env, self.first_payment_date, date_format='yyyy-MM-dd') if self.first_payment_date and self.payment_end_of_month == 'at_anniversary' else None,
            payment_end_of_month=self.payment_end_of_month == 'end_of_month',
            compounding_method=self.compounding_method,
        )
        if schedule := loan.get_payment_schedule():
            return schedule[1:]  # Skip first line which is always 0 (simply the start of the loan)
        return []
