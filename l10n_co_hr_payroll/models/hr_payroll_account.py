# -*- coding:utf-8 -*-
##############################################################################
#
#    odoo, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging

from odoo import models, fields, api
#from odoo.exceptions import warnings
from odoo.tools.translate import _

class HrContributionRegisterPartnerExtended(models.Model):
    _name = 'hr.contribution.partner.register'
    _description = 'HR Contribution Partner Register'

    register_id = fields.Many2one('hr.contribution.register', string='Register')
    partner_id = fields.Many2one('res.partner', string='Partner')
    code = fields.Char(string='Code')
    code2 = fields.Char(string='Other code')


class AccountJournalAdvance(models.Model):
    _inherit = 'account.journal'

    account_advance_id = fields.Many2one('account.account', string='Advance account')

class PaymentJournalAdvance(models.Model):
    _inherit = 'hr.payslip.run'

    journal_id = fields.Many2one('account.journal', string='Advance journal', domain='[("type", "=", "bank")]')
    advance_batch_payment_id = fields.Many2one('account.batch.payment', string='Advance payment')
