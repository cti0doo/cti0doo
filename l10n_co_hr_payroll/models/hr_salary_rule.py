from odoo import models, fields

class HrContributionRegister(models.Model):	
    _name = 'hr.contribution.register'	
    _description = 'Contribution Register'	

    partner_id = fields.Many2one('res.partner', string='Partner')	
    name = fields.Char(required=True,translate=True)	
    register_line_ids = fields.One2many('hr.payslip.line', 'register_id',	
        string='Register Line', readonly=True)	
    note = fields.Text(string='Description')

    partner_ids = fields.One2many('hr.contribution.partner.register', 'register_id', string='Partners')

