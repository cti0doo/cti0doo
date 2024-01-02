# -*- coding:utf-8 -*-


import logging
from datetime import datetime
from datetime import time as datetime_time, timedelta
#from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips
from dateutil.relativedelta import *
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero
from odoo import models, fields, api, _

class HrPayslipWorkedDaysHolidays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    leave_ids = fields.Many2many('hr.leave', string='Holidays')


class HrPayrollStructureExtended(models.Model):
    _inherit = 'hr.payroll.structure'

    name = fields.Char(translate=False)

class HrSalaryRuleExtended(models.Model):
    _inherit = 'hr.salary.rule'

    name = fields.Char(required=True, translate=True)


class HrSalaryRuleCategoryExtended(models.Model):
    _inherit = 'hr.salary.rule.category'

    name = fields.Char(required=True, translate=True)

class HRPayslipExtended(models.Model):
    _inherit = 'hr.payslip'

    line_ids = fields.One2many('hr.payslip.line', 'slip_id', string='Payslip Lines', readonly=True,
#                               states={'draft': [('readonly', False)]},
                               domain=[('appears_on_payslip', '=', True)])
    details_by_salary_rule = fields.One2many('hr.payslip.line', 'slip_id',
                                             string='Details by Salary Rule', readonly=True)
#                                             states={'draft': [('readonly', False)]})
    move_advance_id = fields.Many2one('account.move', string='Advance move')
    payment_advance_id = fields.Many2one('account.batch.payment', string='Downpayment')

    def _prepare_line_values(self, line, account_id, date, debit, credit):
        return {
            'name': line.name,
            'partner_id': line._get_partner_id(credit_account=True if credit > 0 else False),  # line.partner_id.id,
            'account_id': account_id,
            'journal_id': line.slip_id.struct_id.journal_id.id,
            'date': date,
            'debit': debit,
            'credit': credit,
   #         'analytic_account_id': line.salary_rule_id.analytic_account_id.id or line.slip_id.contract_id.analytic_account_id.id,
            'analytic_distribution': (line.salary_rule_id.analytic_account_id and {line.salary_rule_id.analytic_account_id.id: 100}) or
                                     (line.slip_id.contract_id.analytic_account_id.id and {line.slip_id.contract_id.analytic_account_id.id: 100})
        }

    def _get_existing_lines(self, line_ids, line, account_id, debit, credit):
        existing_lines = (
            line_id for line_id in line_ids if
            line_id['name'] == line.name
            and line_id['account_id'] == account_id
            and line_id['partner_id'] == line._get_partner_id(credit_account=True if credit > 0 else False)
            and line_id['analytic_account_id'] == (line.salary_rule_id.analytic_account_id.id or line.slip_id.contract_id.analytic_account_id.id)
            and ((line_id['debit'] > 0 and credit <= 0) or (line_id['credit'] > 0 and debit <= 0)))
        return next(existing_lines, False)

    def action_payslip_paid(self):
        if any(slip.state != 'done' for slip in self):
            raise UserError(_('Cannot mark payslip as paid if not confirmed.'))
        if self.date_to.day < 28:
            self.write({'state': 'verify'})
        else:
            self.write({'state': 'paid'})
    
    def action_payslip_payment(self):
        for obj in self:
#            credit_account_id, debit_account_id = False, False
            line_ids = []
            for line in obj.line_ids:
                if line.salary_rule_id.code == 'TOT_PAY' and not obj.payment_advance_id:
                    amount = line.total or 0.0

                    if amount:
                        payment_line = (0, 0, {
                            'payment_type': 'outbound',
                            'partner_type': 'supplier',
                            'payment_method_id': line._get_payment_method_id(), # 2
                            'partner_id': line._get_partner_id(credit_account=False),
                            'journal_id': obj.journal_id,
                            'date': obj.date_to,
                            'amount': amount,
#                            'state': 'posted',
                        })
                        line_ids.append(payment_line)
                        payslip_input = {
                            'payslip_id': self.id,
                            'sequence': 10,
                            'input_type_id': self._get_input_type_id('ADV_DIS'), # 7 search for input_type.code = 'ADV_DIS'
                            'amount': amount,
                        }
                        line = self.env['hr.payslip.input'].create(payslip_input)
            if obj.date_to.day < 28:
                endmonth = obj.date_to
                endmonth = endmonth + relativedelta(days=30)
                endmonth = endmonth - relativedelta(days=int(endmonth.day))
                advance = 'ADV_DIS'
                value = amount
                return self.write({'date_to' : endmonth})
            else:
                return True


    def _get_payslip_lines(self):
        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
            localdict['categories'].dict[category.code] = localdict['categories'].dict.get(category.code, 0) + amount
            return localdict

        self.ensure_one()
        result = {}
        rules_dict = {}
        worked_days_dict = {line.code: line for line in self.worked_days_line_ids if line.code}
        inputs_dict = {line.code: line for line in self.input_line_ids if line.code}

        employee = self.employee_id
        contract = self.contract_id

        localdict = {
            **self._get_base_local_dict(),
            **{
                'categories': BrowsableObject(employee.id, {}, self.env),
                'rules': BrowsableObject(employee.id, rules_dict, self.env),
                'payslip': Payslips(employee.id, self, self.env),
                'worked_days': WorkedDays(employee.id, worked_days_dict, self.env),
                'inputs': InputLine(employee.id, inputs_dict, self.env),
                'employee': employee,
                'contract': contract,
                #Safe_Eval modules:
                'timedelta': timedelta,
                'strptime': datetime.strptime,
                'relativedelta': relativedelta
            }
        }
        for rule in sorted(self.struct_id.rule_ids, key=lambda x: x.sequence):
            localdict.update({
                'result': None,
                'result_qty': 1.0,
                'result_rate': 100})
            if rule._satisfy_condition(localdict):
                amount, qty, rate = rule._compute_rule(localdict)
                #check if there is already a rule computed with that code
                previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                #set/overwrite the amount computed for this rule in the localdict
                tot_rule = amount * qty * rate / 100.0
                localdict[rule.code] = tot_rule
                rules_dict[rule.code] = rule
                # sum the amount for its salary category
                localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
                # create/overwrite the rule in the temporary results
                result[rule.code] = {
                    'sequence': rule.sequence,
                    'code': rule.code,
                    'name': rule.name,
                    'note': rule.note,
                    'salary_rule_id': rule.id,
                    'contract_id': contract.id,
                    'employee_id': employee.id,
                    'amount': amount,
                    'quantity': qty,
                    'rate': rate,
                    'slip_id': self.id,
                }
        return result.values()

    def hr_verify_sheet(self):
        cr = self._cr
        uid = self.env.user.id
        ids = self.id
        context = self.env.context
        for payroll in self.browse(cr, uid, ids, context=context):
            if not payroll.employee_id.address_home_id:
                raise except_orm(_('Warning'), _('This employee don´t have a home address'))
            if not payroll.contract_id.working_hours:
                raise except_orm(_('Warning'), _('This employee don´t have a working hours'))
        return super(hr_payslip, self).hr_verify_sheet(cr, uid, ids)

    def _get_input_type_id(self, input_code):
        """
        Get input_type_id of payment_type to use in account_payment
        """
        input_type_id = self.env['hr.payslip.input.type'].search([
            ('code', '=', input_code)], limit=1)
        if input_type_id:
            return input_type_id.id
        return False


class HRPayslipExtendedRun(models.Model):
    _inherit = 'hr.payslip.run'

    def action_validate(self):
        for slip in self.slip_ids:
            payslip_done_result = self.mapped('slip_ids').filtered(lambda slip: slip.state not in ['draft', 'cancel']).action_payslip_done()
            self.action_close()
        return payslip_done_result

    def compute_payslips(self):
        for pay in self.slip_ids:
            pay.compute_sheet()
        return True

    def action_paid(self):
#        self.mapped('slip_ids').action_payslip_paid()
        if self.date_end.day < 28:
            self.write({'state': 'verify'})
        else:
            self.write({'state': 'paid'})
    def action_payslips_payment(self):
        line_ids = []
        bank = self.journal_id.id
        payment_date = self.date_end
        name_run = self.name
        for payslip in self.slip_ids:
            payslip.action_payslip_paid(bank, line_ids)
        name = _('Advance Payslip of %s') % (name_run)
        batch_payment_dict = {
            'batch_type': 'outbound',
            'journal_id': bank,
            'payment_method_id': 2, # search method = 'batch'
            'date': payment_date,
        }
        batch_payment_dict['payment_ids'] = line_ids
        batch = self.env['account.batch.payment'].create(batch_payment_dict)
        self.write({'advance_batch_payment_id': batch.id})
#        batch.validate_batch()
#        _logger.info(batch)

#        return True
        if self.date_end.day < 28:
            endmonth = self.date_end
            endmonth = endmonth + relativedelta(days=30)
            endmonth = endmonth - relativedelta(days=int(endmonth.day))
            return self.write({'date_end': endmonth})
        else:
            return True

#        return self.write({'state': 'draft'})

    def confirm_payslip_run(self):
        for run in self:
            if run.state == 'draft':
                for slip in run.slip_ids:
                    if slip.state == 'draft':
                        slip.action_payslip_done()
                self.action_close()
        return True

    def draft_payslip_run(self):
        for run in self:
            if run.state == 'close':
                for slip in run.slip_ids:
                    if slip.state == 'done':
                        slip.action_payslip_cancel()
                        slip.action_payslip_draft()
                self.action_draft()
        return True

class HrPayslipLineExtended(models.Model):
    _inherit = 'hr.payslip.line'

    payslip_run_id = fields.Many2one('hr.payslip.run', string='Pay Slip Run', required=False)
    date_from = fields.Date(string='Date from')
    date_to = fields.Date(string='Date to')
    register_id = fields.Many2one(related='salary_rule_id.register_id', readonly=True, store=True, string='Register')

    def _get_partner_id(self, credit_account):
        """
        Get partner_id of slip line to use in account_move_line
        """
        register = self.salary_rule_id.register_id
        partner_id = self.slip_id.employee_id.address_home_id.id
        register_id = self.partner_id.id or self.slip_id.employee_id.address_home_id.id
        for rg in self.slip_id.contract_id.register_ids:
            if rg.register_id.id == register.id:
                register_id = rg.partner_id.id
        if not partner_id:
            raise Warning('The contract %s has no defined contribution registry for %s' % (
                self.slip_id.contract_id.name, register.name))
        if credit_account:
            if partner_id or self.salary_rule_id.account_credit.internal_type in ('receivable', 'payable'):
                return register_id
            else:
                return partner_id
        else:
            if partner_id or self.salary_rule_id.account_debit.internal_type in ('receivable', 'payable'):
                return partner_id
        return False

    def _get_payment_method_id(self):
        """
        Get payment_method_id of payment_type to use in account_payment
        """
        journal = self.slip_id.payslip_run_id.journal_id
        for method in journal.outbound_payment_method_line_ids:
            if method.name == 'Batch Deposit':
                payment_id = method.id
                return payment_id
        return False
