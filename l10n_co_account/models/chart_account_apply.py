# -*- coding: utf-8 -*-
import logging

from odoo import models
from odoo.addons.account.models.chart_template import template


_logger = logging.getLogger(__name__)

class ChartAccountApply(models.AbstractModel):
    _inherit = 'account.chart.template'

    @template('co', 'account.account.tag')
    def _get_co_account_account(self):
        return self._parse_csv('co', 'account.account.tag', module='l10n_co_account')

    @template('co', 'account.group')
    def _get_co_account_account(self):
        return self._parse_csv('co', 'account.group', module='l10n_co_account')

    @template('co', 'account.account')
    def _get_co_account_account(self):
        return self._parse_csv('co', 'account.account', module='l10n_co_account')

    @template('co', 'account.tax.group')
    def _get_co_account_tax_group(self):
        return self._parse_csv('co', 'account.tax.group', module='l10n_co_account')

    @template('co', 'account.tax')
    def _get_co_account_tax(self):
        return self._parse_csv('co', 'account.tax', module='l10n_co_account')

    @template('co', 'account.fiscal.position')
    def _get_co_account_fiscal_position(self):
        return self._parse_csv('co', 'account.fiscal.position', module='l10n_co_account')
