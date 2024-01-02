from odoo.exceptions import UserError

from odoo import models, api

class HRApplyTemplate(models.TransientModel):
    _inherit = 'res.config.settings'

#    def create_translation(self, model, register, reg):
#        translations = self.env['ir.translation'].search(
#            [('name', '=', model + ',name'), ('res_id', '=', register.id)])
#        for translate in translations:
#            self.env['ir.translation'].create({'display_name': translate.display_name,
#                                               'lang': translate.lang,
#                                               'module': translate.module,
#                                               'name': translate.name.replace('.template', ''),
#                                               'res_id': reg.id,
#                                               'source': translate.source,
#                                               'src': translate.src,
#                                               'state': translate.state,
#                                               'type': translate.type,
#                                               'value': translate.value,
#                                               })
#        return True

    def apply_hr_template(self):
        if not self.env.user.company_id.chart_template_id:
            raise UserError('You must define a chart of accounts for the company')
        hsrt = self.env['hr.salary.rule.template'].search(
            [('chart_template_id', '=', self.env.companies.chart_template_id.id)])
        for register in hsrt:
            register_contribution = self.env['hr.contribution.register'].search(
                [('name', '=', register.name)])
            parent = self.env['hr.salary.rule'].search(
                [('code', '=', register.code)])
#            category = self.env['hr.salary.rule.category'].search(
#                [('name', '=', register.category_id.name)])
            account_credit = self.env['account.account'].search([('code', '=', register.account_credit.code or False)])
            account_debit = self.env['account.account'].search(
                [('code', '=', register.account_debit.code or False)])
            parent.update({
                        'account_debit':  account_debit.id,
                        'account_credit': account_credit.id
                    })
 #           reg = self.env['hr.salary.rule'].write({'id': parent,
 #                                                    'name': register.name,
 #                                                    'code': register.code,
 #                                                    'account_credit': account_credit.id,
 #                                                    'account_debit': account_debit.id
 #                                                     'analytic_account': '001',
 #                                                    })
            self.create_translation('hr.salary.rule.template', register, True)

        return True