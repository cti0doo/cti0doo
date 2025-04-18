#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
##############################################################################
#
#    odoo, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
{
    'name': 'Payroll Colombia',
    'version': '17.0',
    'category': 'Human Resources',
    'description': """
Register temporal allowance/deduction data in employee contract.
================================================================

    * Social Security
    * Social Security type

You can assign several contracts per employee.
    """,
    'author': 'CTI Ltda',
    'website': 'http://www.cti.com.co',
    'images': ['images/hr_contract.jpeg'],
    'license': 'OPL-1',
    'sequence': 120,
    'depends': [
        'base',
        'l10n_co_account',
 #       'hr_payroll_account',
        'hr_timesheet',
 #       'account_followup',
    ],
    'data': [
        'security/ir.model.access.csv',

        # views
        'views/hr_employee_view.xml',
        'views/hr_payroll_account_view.xml',
        'views/hr_payslip_view.xml',
#        'views/hr_apply_template_view.xml',
        'views/hr_leave_view.xml',

        # data
#        'data/hr_leave_data.xml',
#        'data/resource_calendar.xml',
        'data/res.partner.csv',
        'data/hr_contribution_register.xml',
        'data/hr.contribution.partner.register.csv',
        'data/hr.inputs.type.csv',
        'data/hr.payslip.input.type.csv',
        'data/hr.diagnosis.csv',
        'data/hr_payroll_structure.xml',
        'data/hr_salary_rule_category.xml',
        'data/hr.rule.parameter.csv',
#        'data/hr.rule.parameter.value.csv',
        'data/hr.salary.rule.csv',
#        'data/hr.salary.rule.template.csv',
    ],
    'demo': [],
    'css': ['static/src/css/partner_rules.css'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
