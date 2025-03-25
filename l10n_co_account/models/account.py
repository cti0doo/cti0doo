# -*- coding: utf-8 -*-

import logging
from odoo.tools.safe_eval import safe_eval
from datetime import datetime
from odoo import models, fields, api
from odoo.tools.float_utils import float_compare
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ProductTemplateTaxtope(models.Model):
    _inherit = 'product.template'

    tope_retention = fields.Float(string='Retention Stop', default=0.0,
                                  help='Under UVT Stop value will not apply tax. If partner applies')


class ProductCategoryTaxtope(models.Model):
    _inherit = 'product.category'

    tope_retention = fields.Float(string='Retention Stop', default=0.0,
                                  help='Under UVT Stop value will not apply tax. If partner applies')


class accountJournal(models.Model):
    _inherit = 'account.journal'

#    edi_authorization_number = fields.Text(string='edi_authorization_number')

    city_id = fields.Many2one('res.city', string='City', required=False)
    city_mrp_id = fields.Many2one('res.country.state.city', string='City (MRP)', required=False)


#class contabilidad(models.Model):
#    _inherit = 'account.account.template'

#    group_id = fields.Many2one('account.group.template', string='Group')


class AccountMove(models.Model):
    _inherit = "account.move"

    payment_option_id = fields.Many2one('payment.option', string="Move Payment Option",
                                        default=lambda self: self.env.ref('payment_option_1',
                                                                          raise_if_not_found=False))

    def _get_tax_grouping_key_from_base_line(self, base_line, tax_vals):
        ''' Create the dictionary based on a base line that will be used as key to group taxes together.
         Must be consistent with '_get_tax_grouping_key_from_tax_line'.
        :param base_line:   An account.move.line being a base line (that could contains something in 'tax_ids').
        :param tax_vals:    An element of compute_all(...)['taxes'].
        :return:            A dictionary containing all fields on which the tax will be grouped.
        '''
        tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_vals['tax_repartition_line_id'])
        #        account = base_line._get_default_tax_account(tax_repartition_line) or base_line.account_id
        account = self.fiscal_position_id.map_account(
            base_line._get_default_tax_account(tax_repartition_line)) or self.fiscal_position_id.map_account(
            base_line.account_id)
        return {
            'tax_repartition_line_id': tax_vals['tax_repartition_line_id'],
            'account_id': account.id,
            'currency_id': base_line.currency_id.id,
            'analytic_tag_ids': [(6, 0, tax_vals['analytic'] and base_line.analytic_tag_ids.ids or [])],
            'analytic_account_id': tax_vals['analytic'] and base_line.analytic_account_id.id,
            'tax_ids': [(6, 0, tax_vals['tax_ids'])],
            'tax_tag_ids': [(6, 0, tax_vals['tag_ids'])],
        }

    def _recompute_payment_terms_lines(self):
        ''' Compute the dynamic payment term lines of the journal entry.'''
        self.ensure_one()
        in_draft_mode = self != self._origin
        today = fields.Date.context_today(self)

        def _get_payment_terms_computation_date(self):
            ''' Get the date from invoice that will be used to compute the payment terms.
            :param self:    The current account.move record.
            :return:        A datetime.date object.
            '''
            if self.invoice_payment_term_id:
                return self.invoice_date or today
            else:
                return self.invoice_date_due or self.invoice_date or today

        def _get_payment_terms_account(self, payment_terms_lines):
            ''' Get the account from invoice that will be set as receivable / payable account.
            :param self:                    The current account.move record.
            :param payment_terms_lines:     The current payment terms lines.
            :return:                        An account.account record.
            '''
            if payment_terms_lines:
                # Retrieve account from previous payment terms lines in order to allow the user to set a custom one.
                return payment_terms_lines[0].account_id
            elif self.partner_id:
                # Retrieve account from partner.
                if self.is_sale_document(include_receipts=True):
                    #return self.partner_id.property_account_receivable_id)
                    return self.fiscal_position_id.map_account(self.partner_id.property_account_receivable_id)
                else:
                    #return self.partner_id.property_account_payable_id)
                    return self.fiscal_position_id.map_account(self.partner_id.property_account_payable_id)
            else:
                # Search new account.
                domain = [
                    ('company_id', '=', self.company_id.id),
                    ('internal_type', '=', 'receivable' if self.move_type in ('out_invoice', 'out_refund', 'out_receipt') else 'payable'),
                ]
                return self.env['account.account'].search(domain, limit=1)

        def _compute_payment_terms(self, date, total_balance, total_amount_currency):
            ''' Compute the payment terms.
            :param self:                    The current account.move record.
            :param date:                    The date computed by '_get_payment_terms_computation_date'.
            :param total_balance:           The invoice's total in company's currency.
            :param total_amount_currency:   The invoice's total in invoice's currency.
            :return:                        A list <to_pay_company_currency, to_pay_invoice_currency, due_date>.
            '''
            if self.invoice_payment_term_id:
                to_compute = self.invoice_payment_term_id.compute(total_balance, date_ref=date, currency=self.currency_id)
                if self.currency_id == self.company_id.currency_id:
                    # Single-currency.
                    return [(b[0], b[1], 0.0) for b in to_compute]
                else:
                    # Multi-currencies.
                    to_compute_currency = self.invoice_payment_term_id.compute(total_amount_currency, date_ref=date,currency=self.currency_id)
                    return [(b[0], b[1], ac[1]) for b, ac in zip(to_compute, to_compute_currency)]
            else:
                return [(fields.Date.to_string(date), total_balance, total_amount_currency)]

        def _compute_diff_payment_terms_lines(self, existing_terms_lines, account, to_compute):
            ''' Process the result of the '_compute_payment_terms' method and creates/updates corresponding invoice lines.
            :param self:                    The current account.move record.
            :param existing_terms_lines:    The current payment terms lines.
            :param account:                 The account.account record returned by '_get_payment_terms_account'.
            :param to_compute:              The list returned by '_compute_payment_terms'.
            '''
            # As we try to update existing lines, sort them by due date.
            existing_terms_lines = existing_terms_lines.sorted(lambda line: line.date_maturity or today)
            existing_terms_lines_index = 0


            # change
            #mappedAccount = self.fiscal_position_id.map_account(account)


            # Recompute amls: update existin_recompute_payment_terms_linesg line or create new one for each payment term.
            new_terms_lines = self.env['account.move.line']
            for date_maturity, balance, amount_currency in to_compute:
                if self.journal_id.company_id.currency_id.is_zero(balance) and len(to_compute) > 1:
                    continue

                if existing_terms_lines_index < len(existing_terms_lines):
                    # Update existing line.
                    candidate = existing_terms_lines[existing_terms_lines_index]
                    existing_terms_lines_index += 1
                    candidate.update({
                        'date_maturity': date_maturity,
                        'amount_currency': -amount_currency,
                        'debit': balance < 0.0 and -balance or 0.0,
                        'credit': balance > 0.0 and balance or 0.0,
                    })
                else:
                    # Create new line.
                    create_method = in_draft_mode and self.env['account.move.line'].new or self.env['account.move.line'].create
                    candidate = create_method({
                        'name': self.payment_reference or '',
                        'debit': balance < 0.0 and -balance or 0.0,
                        'credit': balance > 0.0 and balance or 0.0,
                        'quantity': 1.0,
                        'amount_currency': -amount_currency,
                        'date_maturity': date_maturity,
                        'move_id': self.id,
                        'currency_id': self.currency_id.id if self.currency_id != self.company_id.currency_id else False,
                        'account_id': account.id,
                        'partner_id': self.commercial_partner_id.id,
                        'exclude_from_invoice_tab': True,
                    })
                new_terms_lines += candidate
                if in_draft_mode:
                    candidate._onchange_amount_currency()
                    candidate._onchange_balance()
            return new_terms_lines
        #existing_terms_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
        existing_terms_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable', 'receivable_off', 'payable_off'))
        #others_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
        others_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable', 'receivable_off', 'payable_off'))
        total_balance = sum(others_lines.mapped('balance'))
        total_amount_currency = sum(others_lines.mapped('amount_currency'))

        if not others_lines:
            self.line_ids -= existing_terms_lines
            return

        computation_date = _get_payment_terms_computation_date(self)
        account = _get_payment_terms_account(self, existing_terms_lines)
        to_compute = _compute_payment_terms(self, computation_date, total_balance, total_amount_currency)
        new_terms_lines = _compute_diff_payment_terms_lines(self, existing_terms_lines, account, to_compute)

        # Remove old terms lines that are no longer needed.
        self.line_ids -= existing_terms_lines - new_terms_lines

        if new_terms_lines:
            self.payment_reference = new_terms_lines[-1].name or ''
            self.invoice_date_due = new_terms_lines[-1].date_maturity



class AccountMoveLines(models.Model):
    _inherit = "account.move.line"

    def update_taxes(self,set_taxes):
        partner_retention = self.partner_id.retention
        date_line = self.move_id.invoice_date
        fdy = datetime(date_line.year, 1,1).date()

        move_parameter = self.env['hr.rule.parameter'].search([
            ('code', '=', 'UVT')
        ])
        if not move_parameter:
            raise UserError('Unable to get parameter for code UVT{}'.format(date_line))
        uvt = move_parameter.parameter_version_ids.filtered(lambda x: x.date_from == fdy).parameter_value

        value_wuvt = (self.product_id.tope_retention or self.product_id.categ_id.tope_retention) * float(uvt)

        taxes = set_taxes
        if taxes and self.move_id.fiscal_position_id:
            taxes = self.move_id.fiscal_position_id.map_tax(taxes, partner=self.partner_id)

        if partner_retention and self.price_subtotal > 0.0 and (self.product_id.tope_retention  > 0.0 or self.product_id.categ_id.tope_retention  > 0.0):
            for tax in set_taxes:
                if tax.limit and self.price_subtotal < value_wuvt:
                    taxes = taxes - tax

        return taxes

#    @api.onchange('quantity', 'discount', 'price_unit', 'tax_ids')
#    def _onchange_price_subtotal(self):
#        super(AccountMoveLines, self)._onchange_price_subtotal()
#
#        for line in self:
#            line.tax_ids = line.update_taxes(line._get_computed_taxes())
#            line.tax_ids = line.update_taxes(line._onchange_account_id())

    @api.constrains('account_id', 'tax_ids', 'tax_line_id', 'reconciled')
    def _check_off_balance(self):
        for line in self:
            if line.account_id.internal_group == 'off_balance':
                if any(a.internal_group != line.account_id.internal_group for a in line.move_id.line_ids.account_id):
                    raise UserError(_('If you want to use "Off-Balance Sheet" accounts, all the accounts of the journal entry must be of this type'))
#                if line.tax_ids or line.tax_line_id:
#                    raise UserError(_('You cannot use taxes on lines with an Off-Balance account'))
#                if line.reconciled:
#                    raise UserError(_('Lines from "Off-Balance Sheet" accounts cannot be reconciled'))


#class AccountTaxTemplate(models.Model):
#    _inherit = 'account.tax.template'
#
#    limit = fields.Boolean(string='Limit', default=False,
#                           help='This option allows to indicate that this tax has a cap indicated in the product category.')


class AccountTaxUVT(models.Model):
    _inherit = 'account.tax'

    limit = fields.Boolean(string='Limit', default=False,
                           help='This option allows to indicate that this tax has a cap indicated in the product category.')

