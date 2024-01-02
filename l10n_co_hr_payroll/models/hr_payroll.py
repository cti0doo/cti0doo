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

from odoo import models, fields

class hr_salary_rule_extended(models.Model):
    _inherit = 'hr.salary.rule'

    register_id = fields.Many2one('hr.contribution.register', string='Register')

#class hr_salary_rule_template(models.Model):
#    _name = 'hr.salary.rule.template'
#    _description = 'HR Salary Rule Template'#

#    name = fields.Char('Name', required=True, readonly=False, translate=True)
#    code = fields.Char('Code', required=True,
#                       help="The code of salary rules can be used as reference in computation of other rules. In that case, it is case sensitive.")
#    chart_template_id = fields.Many2one('account.chart.template', 'Chart Template')
#    account_debit = fields.Many2one('account.account.template', 'Debit Account')
#    account_credit = fields.Many2one('account.account.template', 'Credit Account')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
