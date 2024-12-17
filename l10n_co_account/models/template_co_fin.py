# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models
from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    @template('co_fin')
    def _get_co_fin_template_data(self):
        return {
            'property_account_receivable_id': 'co_puc_161695',
            'property_account_payable_id': 'co_puc_251105',
            'property_account_expense_categ_id': 'co_puc_510395',
            'property_account_income_categ_id': 'co_puc_410295',
        }

    @template('co_fin', 'res.company')
    def _get_co_fin_res_company(self):
        return {
            self.env.company.id: {
                'anglo_saxon_accounting': True,
                'account_fiscal_country_id': 'base.co',
                'bank_account_code_prefix': '1110',
                'cash_account_code_prefix': '1105',
                'transfer_account_code_prefix': '1115',
                'account_default_pos_receivable_account_id': 'co_puc_130507',
                'income_currency_exchange_account_id': 'co_puc_421005',
                'expense_currency_exchange_account_id': 'co_puc_530505',
                'account_journal_early_pay_discount_loss_account_id': 'co_puc_530535',
                'account_journal_early_pay_discount_gain_account_id': 'co_puc_421040',
                'account_sale_tax_id': 'l10n_co_tax_8',
                'account_purchase_tax_id': 'l10n_co_tax_1',
                'default_cash_difference_income_account_id': 'co_puc_428000',
                'default_cash_difference_expense_account_id': 'co_puc_532000',
            },
        }
    @template('co_fin', 'account.account.tag')
    def _get_co_fin_account_account(self):
        return self._parse_csv('co_fin', 'account.account.tag', module='l10n_co')

    @template('co_fin', 'account.group')
    def _get_co_fin_account_account(self):
        return self._parse_csv('co_fin', 'account.group', module='l10n_co')

    @template('co_fin', 'account.account')
    def _get_co_fin_account_account(self):
        return self._parse_csv('co_fin', 'account.account', module='l10n_co')

    @template('co_fin', 'account.tax.group')
    def _get_co_fin_account_tax_group(self):
        return self._parse_csv('co_fin', 'account.tax.group', module='l10n_co')

    @template('co_fin', 'account.tax')
    def _get_co_account_tax(self):
        return self._parse_csv('co_fin', 'account.tax', module='l10n_co')

    @template('co_fin', 'account.fiscal.position')
    def _get_co_account_fiscal_position(self):
        return self._parse_csv('co_fin', 'account.fiscal.position', module='l10n_co')
