# -*- coding: utf-8 -*-
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
import logging

from odoo import models, api, fields

_logger = logging.getLogger(__name__)

class hr_department(models.Model):
    _inherit = "hr.department"

    arl_class = fields.Selection(
        selection=[
            ('1', 'Minimun risk'),
            ('2', 'Low Risk'),
            ('3', 'Medium Risk'),
            ('4', 'High Risk'),
            ('5', 'Maximun')
        ],
        string='Arl Class',
        required=False
    )

class hr_job(models.Model):
    _inherit = "hr.job"

    arl_class = fields.Selection(
        selection=[
            ('1', 'Minimun risk'),
            ('2', 'Low Risk'),
            ('3', 'Medium Risk'),
            ('4', 'High Risk'),
            ('5', 'Maximun')
        ],
        string='Arl Class',
        required=False
    )

class hr_employee(models.Model):
    _inherit = "hr.employee"

    _defaults = {
        'vehicle_distance': 2,
    }


class HRContractRegisterExtended(models.Model):
    _inherit = "hr.contract"

    integral = fields.Boolean(string='Integral Salary?', default=False)
    pensioner = fields.Boolean(string='Pensioner?', default=False)
    register_ids = fields.One2many('hr.contract.register', 'contract_id', string='Partner')
    payslip_ids = fields.One2many('hr.payslip', 'contract_id', string='Payslips history')
    inputs_ids = fields.One2many('hr.inputs', 'contract_id', string='Inputs')

class HRContractInputs(models.Model):
    _name = "hr.inputs"
    _description = "Inputs"

    contract_id = fields.Many2one('hr.contract', string='Contract')
    type = fields.Many2one('hr.inputs.type', string='Inputs Type', required=True)
    amount = fields.Float(string='Amount', default=0.0)
    date_from = fields.Date(string='Date from')
    date_to = fields.Date(string='Date to')


class HRContractInputsType(models.Model):
    _name = "hr.inputs.type"
    _description = "Inputs Type"

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Name', required=True, translate=True)
    tope = fields.Float(string='Tope (UVT)', required=True)


class HRContractRegisterLineExtended(models.Model):
    _name = "hr.contract.register"
    _description = "Contract Register"

    @api.onchange('register_id')
#    @api.depends('register_id')
    def _get_partners(self):
        partner = []
        for x in self.register_id.partner_ids:
            partner.append(x.partner_id.id)
        return {'domain': {'partner_id': [('id', 'in', tuple(partner))]}} if partner else {}

    contract_id = fields.Many2one('hr.contract', string='Contract')
    register_id = fields.Many2one('hr.contribution.register', string='Register')
    partner_id = fields.Many2one('res.partner', string='Partner', domain=_get_partners)
    #    partner_id = fields.Many2one('hr.contribution.partner.register', string='Partner', domain='[("partner_id", "=", partner_id.id)]')
    _sql_constraints = [
        ('contract_register', 'unique (contract_id,register_id)',
         'You can not have a record of repeated contribution per contract')
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
