# -*- coding: utf-8 -*-7
##############################################################################
#
#    odoo, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from odoo import SUPERUSER_ID
from odoo import models

_logger = logging.getLogger('HR PAYROLL')


class wizard_update_hr(models.TransientModel):
    """
        Wizard update HHRR for multicompany
    """
    _name = "wizard.update.hr"
    _description = "Wizard Update HHRR"

    def _get_account_tax_code(self, company, account_tax_id):
        cr = self.cr
        uid = self.uid
        atc_id = self.pool.get('account.tax.code').search(cr, uid, [('company_id', '=', company),
                                                                    ('code', '=', account_tax_id.code)])
        if atc_id:
            return atc_id[0]
        return False

    def _get_account_account(self, company, account_id):
        cr = self._cr
        uid = self.env.user_id.id

        if account_id:
            acc_id = self.pool.get('account.account').search(cr, uid, [('company_id', '=', company),
                                                                       ('code', '=', account_id.code)])
            if acc_id:
                return acc_id[0]
            else:
                raise _logger.error("UPDATE hr.salary.rule account: %s", account_id.code)

        return False

    def _update_payroll_structure(self, company, account_id):
        cr = self._cr
        uid = self.env.user.id

        return False

    def update_contribution_register(self, context=None):
        '''
        Update salary rule, input, contribution register and payroll structure from template
        '''
        cr = self._cr
        uid = self.env.user.id
        ids = self.id
        context = self.env.context

        #        cr.execute("""
        #            -- Actualiza UVT
        #            DELETE FROM ir_model_data WHERE module LIKE '3rp_hr%'
        #            """ 
        #        )
        uid = SUPERUSER_ID
        obj_company = self.pool.get('res.company')

        obj_sr = self.pool.get('hr.salary.rule')
        obj_sr_temp = self.pool.get('hr.salary.rule.template')


        company_ids = obj_company.search(cr, uid, [])
        for company_id in obj_company.browse(cr, uid, company_ids):

            if not company_id.hr_beta:
                continue

            _logger.info("UPDATE hr.salary.rule for Company: %s", company_id.name)
            sr_ref = {}

            sr_temp_ids = obj_sr_temp.search(cr, uid, [('chart_template_id', '=', company_id.chart_template_id.id)],
                                             order='id')
            for sr_temp in obj_sr_temp.browse(cr, uid, sr_temp_ids):
                sr_id = obj_sr.search(cr, uid, [('company_id', '=', company_id.id), ('code', '=', sr_temp.code)])
                #
                # OJO CON ESTO, Aqui esta TODO
                #
                vals = {
                    'name': sr_temp.name,
                    'code': sr_temp.code,
                    'sequence': sr_temp.sequence,
                    'quantity': sr_temp.quantity,
                    'category_id': sr_temp.category_id and (
                    (sr_temp.category_id.id in src_ref) and src_ref[sr_temp.category_id.id]) or False,
                    'active': sr_temp.active,
                    'appears_on_payslip': sr_temp.appears_on_payslip,
                    'parent_rule_id': sr_ref and (
                    (sr_temp.parent_rule_id.id in sr_ref) and sr_ref[sr_temp.parent_rule_id.id]) or False,
                    'company_id': company_id.id,
                    'condition_select': sr_temp.condition_select,
                    'condition_range': sr_temp.condition_range,
                    'condition_python': sr_temp.condition_python,
                    'condition_range_min': sr_temp.condition_range_min,
                    'condition_range_max': sr_temp.condition_range_max,
                    'amount_select': sr_temp.amount_select,
                    'amount_fix': sr_temp.amount_fix,
                    'amount_percentage': sr_temp.amount_percentage,
                    'amount_python_compute': sr_temp.amount_python_compute,
                    'amount_percentage_base': sr_temp.amount_percentage_base,
                    #                    'child_ids':fields.one2many('hr.salary.rule.template', 'parent_rule_id', 'Child Salary Rule'),
                    'register_id': sr_temp.register_id and (
                    (sr_temp.register_id.id in cr_ref) and cr_ref[sr_temp.register_id.id]) or False,
                    #                    'input_ids': fields.one2many('hr.rule.input.template', 'input_id', 'Inputs'),
                    'note': sr_temp.note,
                    #                    'analytic_account_id':fields.many2one('account.analytic.account', 'Analytic Account'),
                    'account_tax_id': self._get_account_tax_code(cr, uid, company_id.id, sr_temp.account_tax_id),
                    'account_debit': self._get_account_account(cr, uid, company_id.id, sr_temp.account_debit),
                    'account_credit': self._get_account_account(cr, uid, company_id.id, sr_temp.account_credit),

                }

                if not sr_id:
                    sr_id = obj_sr.create(cr, uid, vals)
                else:
                    sr_id = sr_id[0]
                    obj_sr.write(cr, uid, sr_id, vals)

                sr_ref[sr_temp.id] = sr_id

        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
