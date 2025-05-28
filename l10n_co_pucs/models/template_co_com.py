# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models
from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    @template('co_com')
    def _get_co_com_template_data(self):
        return {
            'code_digits': '6',
            'name': ('Commercial Chart of Accounts'),
            'property_account_receivable_id': 'co_puc_130505',
            'property_account_payable_id': 'co_puc_220505',
            'property_account_expense_categ_id': 'co_puc_519595',
            'property_account_income_categ_id': 'co_puc_413595',
        }

    @template('co_com', 'res.company')
    def _get_co_com_res_company(self):
        return {
            self.env.company.id: {
                'anglo_saxon_accounting': True,
                'account_fiscal_country_id': 'base.co',
                'bank_account_code_prefix': '1110',
                'cash_account_code_prefix': '1105',
                'transfer_account_code_prefix': '1115',
                'account_default_pos_receivable_account_id': 'co_puc_130595',
                'income_currency_exchange_account_id': 'co_puc_421020',
                'expense_currency_exchange_account_id': 'co_puc_530525',
                'account_journal_early_pay_discount_loss_account_id': 'co_puc_530535',
                'account_journal_early_pay_discount_gain_account_id': 'co_puc_421040',
                'account_sale_tax_id': 'co_com_tax_iva_19gt',
                'account_purchase_tax_id': 'co_com_tax_iva_19lt',
                'default_cash_difference_income_account_id': 'co_puc_429553',
                'default_cash_difference_expense_account_id': 'co_puc_532000',
             },
        }
        