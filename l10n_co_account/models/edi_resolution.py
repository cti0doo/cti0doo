# -*- coding:utf-8 -*-
import datetime
from odoo import models, api, _, fields
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class edi_resolution(models.Model):
    _name = 'edi.resolution'
    _description = 'Edi Resolution'

#    Active
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        ondelete='restrict',
        required=True
    )
    number = fields.Char(
        string="Resolution Number",
        required=True
    )
    name = fields.Char(
        string="Resolution Name",
        required=True
    )
    type = fields.Selection(
        selection=[
            ('paper', 'Paper'),
            ('by_computer', 'By computer'),
            ('electronic_invoice', 'Electronic Invoice')
        ],
        string='Type',
        required=True
    )
    seq_from = fields.Integer(
        string='From',
        required=True
    )
    seq_to = fields.Integer(
        string='To',
        required=True
    )
    date = fields.Date(
        string="Resolution Date",
        required=True
    )
    send_seq = fields.Integer(
        string='Next Sequence',
        required=True,
        default=1
    )
    start_date = fields.Date(
        string='Start Date',
        required=True
    )
    end_date = fields.Date(
        string='End Date',
        required=True
    )
    prefix = fields.Char(
#        related='journal.secure_sequence_id.prefix',
        string="Prefix")
#        store=False,
#        readonly=True
#    )
    prefix_note = fields.Char(
#        related='journal_id.refund_sequence_id.prefix',
        string="Refund Prefix")

    technical_key = fields.Char(
        string='Technical key',
    )
    state = fields.Selection(
        selection=[
            ('active', 'Active'),
            ('inactive', 'Unactive')
        ],
        string='Status',
        default='active',
        required=True
    )

    category = fields.Selection(
        selection=[
            ('invoice', 'Invoice'),
            ('credit_note', 'Credit Note'),
            ('debit-note', 'Debit Note'),
            ('contingency', 'Contingency Invoice')
        ],
        string='Category',
        default='invoice',
        required=True
    )

    _sql_constraints = [
        # (
        #     'resolution_unique',
        #     'unique(resolution, start_date, company_id, journal_id)',
        #     'company, journal, resolution start_date must be unique.'
        # ),
        (
            'seq_from_check',
            'check(seq_from > 0)',
            'Seq_from must be a positve integer'
        ),
        (
            'seq_to_check',
            'check(seq_to > 0)',
            'Sequence to must a positve integer'
        ),
        (
            'seq_from_to_check',
            'check(seq_from < seq_to)',
            'Sequence from must be less than sequence to'
        ),
        # (
        #     'consecutivo_envio_check', 
        #     'check(consecutivo_envio >= minimo AND consecutivo <= rango_hasta)',
        #     'El consecutivo debe encontrarse dentro del rango especificado.'
        # ),
        (
            'start_date_end_date_check',
            'check(start_date < end_date)',
            'Start date must be less than end date'
        )
    ]

#    @api.constrains('journal_id', 'resolution', 'start_date')
#    def _check_unique_resolution(self):
#        for record in self:

#            resolution = self.env['l10n_co.edi_resolution'].search([
#                ('company_id', '=', record.company_id.id),
#                ('journal_id', '=', record.journal_id.id),
#                ('start_date', '=', record.start_date),
#                ('state', '=', 'active'),
#                ('id', '!=', record.id),
#                ('category', '=', record.category)
#            ],
#                limit=1
#            )
#
#            if resolution:
#                raise ValidationError(
#                    "registered resolution with especific "
#                    "characteristics"
#                )

    def next_seq(self):
        current_seq = self.send_seq
        self.send_seq += 1
        return str(current_seq)

    def _check_seq(self):
        next_seq = self.journal.secure_sequence_id.next_seq
        return (
                self.seq_from <= next_seq <= self.seq_to
        )

    def check_resolution(self):
        # validates if the next number of the sequence is within the
        # valid range
        return self._check_number()
