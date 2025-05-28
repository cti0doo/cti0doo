# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models
from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    @template('co_sol')
    def _get_co_template_data(self):
        return {
            'name': ('Solidary Chart of Accounts'),
            'property_account_receivable_id': 'co_puc_160505',
            'property_account_payable_id': 'co_puc_240595',
            'property_account_expense_categ_id': 'co_puc_511095',
            'property_account_income_categ_id': 'co_puc_414710',
        }

    @template('co_sol', 'res.company')
    def _get_co_res_company(self):
        return {
            self.env.company.id: {
                'anglo_saxon_accounting': True,
                'account_fiscal_country_id': 'base.co',
                'bank_account_code_prefix': '1110',
                'cash_account_code_prefix': '1105',
                'transfer_account_code_prefix': '1115',
                'account_default_pos_receivable_account_id': 'co_puc_130507',
                'income_currency_exchange_account_id': 'co_puc_425505',
                'expense_currency_exchange_account_id': 'co_puc_617505',
                'account_journal_early_pay_discount_loss_account_id': 'co_puc_521025',
                'account_journal_early_pay_discount_gain_account_id': 'co_puc_417505',
                'account_sale_tax_id': 'co_sol_tax_iva_19gt',
                'account_purchase_tax_id': 'o_sol_tax_iva_19lt',
                'default_cash_difference_income_account_id': 'co_puc_423095',
                'default_cash_difference_expense_account_id': 'co_puc_511095',
            },
        }
