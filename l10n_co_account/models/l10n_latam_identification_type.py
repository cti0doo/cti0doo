# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class L10nCoIdentificationType(models.Model):
    _inherit = "l10n_latam.identification.type"

    code = fields.Char("Code")
    short_name = fields.Char(string="Short Name")
