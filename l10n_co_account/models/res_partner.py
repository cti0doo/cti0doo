# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api

# from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


class res_partner(models.Model):
    _inherit = 'res.partner'

    firstname = fields.Char(string='Firstname')
    other_name = fields.Char(string='Other name')
    lastname = fields.Char(string='Lastname')
    other_lastname = fields.Char(string='Other lastname')

    retention = fields.Boolean(string='Apply UVT rule', default=False)

    """Document type: Lista de selección con los tipos de documento aceptados
       por la autoridad de impuestos (DIAN).
        11 - Registro civil
        12 - Tarjeta de identidad
        13 - Cédula de ciudadanía
        21 - Tarjeta de extranjería
        22 - Cédula de extranjería
        31 - NIT (Número de identificación tributaria)
        41 - Pasaporte
        42 - Tipo de documento extranjero
        43 - Para uso definido por la DIAN

        http://www.dian.gov.co/descargas/normatividad/Factura_Electronica/Anexo_001_R14465.pdf"""

#    vat_type = fields.Selection([
#        ('12', u'12 - Tarjeta de identidad'),
#        ('13', u'13 - Cédula de ciudadanía'),
#        ('21', u'21 - Tarjeta de extranjería'),
#        ('22', u'22 - Cédula de extranjería'),
#        ('31', u'31 - NIT (Número de identificación tributaria)'),
#        ('41', u'41 - Pasaporte'),
#        ('42', u'42 - Documento de identificación extranjero'),
#        ('43', u'43 - Sin identificación del exterior o para uso definido por la DIAN')
#    ], string='TaxId type',
#        help='''Customer identifier, according to types given by the DIAN.
#                If it is a natural person and has RUT use NIT''',
#        required=True, default='13'
#    )
    vat_vd = fields.Char('vd', size=1, help='VD')
    zip_id = fields.Many2one('res.city.zip', string='Zip Ref', ondelete='restrict', required=False)
    stock_holder = fields.Selection([
        ('sh', 'Stock holder'),
        ('nsh', 'No Stock holder')
    ], 'Stock holder', default='nsh', required=True)
    ciiu_id = fields.Many2one('account.ciiu', string='CIIU')
    retention_apply = fields.Selection([('na', 'Not apply'), ('fa', 'Force apply'), ('ta', 'Apply')],
                                       string='Retention apply?', default='ta', required=True)
    industry_id = fields.Many2one('res.partner.industry', string='Industry', required=False)

    ei_enabled = fields.Boolean(
        string='Enabled',
        default=True
    )

    ei_mercantil_register = fields.Char(
        string='Mercantil Register',
        default='0'
    )

    ei_fiscal_responsibility_ids = fields.Many2many(
        'fiscal.responsibility',
        'partner_fiscal_responsibility',
        'partner_id', 'responsibility_id',
        string='Fiscal Responsibility'
    )


    def write(self, vals):
        for record in self:
            if record.child_ids:
                for child in record.child_ids:
                    if vals.get('customer') is not None:
                        child.customer = vals.get('customer')
                    if vals.get('supplier') is not None:
                        child.supplier = vals.get('supplier')
                    if vals.get('stock_holder') is not None:
                        child.stock_holder = vals.get('stock_holder', child.stock_holder)
        return super(res_partner, self).write(vals)

    def check_vat_co(self, vat):

        if self.l10n_latam_identification_type_id.code != '31':
            return True

        if not self.vat_vd or len(self.vat_vd) != 1:
            return False

        factor = [71, 67, 59, 53, 47, 43, 41, 37, 29, 23, 19, 17, 13, 7, 3]
        factor = factor[-len(self.vat):]
        csum = sum([int(self.vat[i]) * factor[i] for i in range(len(self.vat))])
        check = csum % 11
        if check > 1:
            check = 11 - check
        return check == int(self.vat_vd)

    def _onerror_msg(self, msg):
        return {'warning': {'title': _('Error!'), 'message': _(msg)}}

    @api.onchange('l10n_latam_identification_type_id')
    def onchange_l10n_latam_identification_type_id(self):

        return {'value': {'is_company': self.l10n_latam_identification_type_id.code == '31'}}

    @api.onchange('vat')
    def onchange_vat(self):
        # Validaciones
        if not self.l10n_latam_identification_type_id:
            return {'value': {'vat_vd': ''}}

        if self.vat:
            if len(self.vat) < 6:
                return self._onerror_msg(
                    u'VAT must have at least six digits.'
                )

            if not self.vat.isdigit() and self.l10n_latam_identification_type_id != 'it_pass':
                return self._onerror_msg(u'VAT must have only numbers')

            if self.l10n_latam_identification_type_id != 'rut':
                return {'value': {'vat_vd': ''}}

        return {'value': {'vat_vd': ''}}

    @api.onchange('vat_vd')
    def onchange_vat_vd(self):

        if self.l10n_latam_identification_type_id == 'rut':
            if not self.vat_vd:
                return self._onerror_msg(
                    u"VD is required"
                )

            if not self.check_vat_co(self.l10n_latam_identification_type_id, self.vat, self.vat_vd):
                return self._onerror_msg(
                    u'Given NIT is not valid!'
                )

        return False

    def _commercial_fields(self):
        """
        Return the list of fields that are managed by the commercial entity
        to which a partner belongs.

        These fields are meant to be hidden on partners that aren't
        `commercial entities` themselves, and will be delegated to
        the parent `commercial entity`. The list is meant to be
        extended by inheriting classes.
        """
        return ['website']

    def copy(self):
        [partner_dic] = self.read(['name', 'vat'])
        default = {}
        default.update({
            'name': '(copy) ' + partner_dic.get('name'),
            'vat': '(copy) ' + partner_dic.get('vat'),
        })
        return super(res_partner, self).copy(default)

    def _check_vat(self):
        if self.company_id and self.vat and self.search(
                [('company_id', '=', self.company_id.id), ('vat', '=ilike', self.vat),
                 ('parent_id', '=', None)]).id != self.id:
            return False
        return True

    def _check_vat_vd(self):
        if self.l10n_latam_identification_type_id == 'rut' and not self.check_vat_co(self.l10n_latam_identification_type_id, self.vat, self.vat_vd):
            return False
        return True

# _constraints = [
#     # TODO: Validar que ya existe el VAT
#     # (_check_vat, 'NIT already exist!', ["vat", ]),
#     (_check_vat_vd,
#      u"Given NIT did't pass the validation!",
#      ["vat_vd", ]),
# ]

# TODO: Restricción de codigo unico por compañía
# _sql_constraints = [
#     ('code_name_uniq',
#      'unique (company_id,name)',
#      u'Customer/Provider must be uniq per company!')
# ]
