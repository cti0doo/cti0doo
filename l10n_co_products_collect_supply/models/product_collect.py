# -*- coding: utf-8 -*-

import logging

from odoo.exceptions import UserError

from odoo import models, fields, api, SUPERUSER_ID, _

# Get the logger
_logger = logging.getLogger(__name__)


class ProductCollect(models.Model):
    _name = 'product.collect'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Product Collect"
    _order = 'name asc'

    def _get_date(self):
        return fields.Datetime.now()

    name = fields.Char(string='Number', default='New', readonly=True, copy=False)
    picking_type_id = fields.Many2one('stock.picking.type', string='Picking type',
                                      index=True)
    product_id = fields.Many2one('product.product', string='Product',
                                 domain="[('purchase_ok','=',True)]",
                                 required=True, index=True)
    purchase_id = fields.Many2one('purchase.order', string='Transport order',
                                  index=True, copy=False,
                                  readonly=True)
    line_ids = fields.One2many('product.collect.lines', 'product_collect_id',
                               string="Lines", copy=True)
    date = fields.Date(string='Date', readonly=False, required=True,
                           copy=False, default=_get_date)
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm'), ('closed', 'Closed'),
         ('cancel', 'Cancel')], default='draft', string='State'
    )
    transport_id = fields.Many2one('res.partner', string='Transport', index=True, required=True)
    product_transport_id = fields.Many2one('product.product', string='Product transport',
                                           domain="[('landed_cost_ok','=',True)]", index=True,
                                           required=True)
    fare = fields.Float(string='Fare', required=True, default=0)
    description = fields.Text(string='Description')
    average = fields.Float(compute='_get_average', string='Average', store=True)
    price_total = fields.Float(compute='_get_average', string='Price Total', store=True)
    quantity = fields.Float(compute='_get_average', string='Quantity', store=True)

    @api.onchange('product_transport_id')
    def onchange_product_transport_id(self):
        self.fare = self.product_transport_id.standard_price

    
    @api.depends('line_ids')
    def _get_average(self):
        quantity = 0
        total = 0
        for x in self.line_ids:
            x.quantity = x.qty_po * x.factor + x.qty
            quantity += x.quantity
            x.price_total = x.quantity * x.price_unit
            total += x.price_total
        self.average = total / (quantity or 1)
        self.quantity = quantity
        self.price_total = total

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') != 'New':
            vals['name'] = 'New'
        vals['name'] = self.env['ir.sequence'].next_by_code('product.collect') or '/'
        return super().create(vals)

    def create_po(self, product, lines, order_id, transport):
        po = self.env['purchase.order']
        purchase_order = True
        if not product.landed_cost_ok:
            picking_batch = self.env['stock.picking.batch'].create({'name': self.name})
        for line in lines:
            if not transport:
                partner = line.partner_id
                quantity = line.quantity
            else:
                partner = line
                quantity = 1
            if quantity >= 1:
                product_lang = product.with_context({
                    'lang': partner.lang,
                    'partner_id': partner.id,
                })
                product_name = product_lang.display_name
                if product_lang.description_purchase:
                    product_name += '\n' + product_lang.description_purchase
                fpos = partner.property_account_position_id
                taxes = None
                if self.env.uid == SUPERUSER_ID:
                    company_id = self.env.user.company_id.id
                    taxes = fpos.map_tax(
                        product.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
                else:
                    taxes = fpos.map_tax(product.supplier_taxes_id)

                products = product.seller_ids.filtered(
                    lambda r: r.name.id == partner.id and r.price)
                if products:
                    if products[0].product_name:
                        product_name = products[0].product_name

                # price = products[0].price if products else product.standard_price
                if transport:
                    price = self.fare
                else:
                    price = line.price_unit or product.standard_price

                # Purchase order per line
                purchase_order = po.create({
                    'partner_id': partner.id,
                    'date_order': order_id.date,
                    'picking_type_id': self.picking_type_id.id,
                    'origin': self.name,
                    'order_line': [(0, 0, {
                        'product_id': product.id,
                        'name': product_name,
                        'date_planned': order_id.date,
                        'product_qty': quantity,
                        'product_uom': product.uom_id.id or product.uom_po_id.id,
                        'price_unit': price,
                        'taxes_id': [(4, x.id) for x in taxes],
                    })]
                })
                order = order_id if transport else line
                order.write({'purchase_id': purchase_order.id})
                purchase_order.button_confirm()
                if not product.landed_cost_ok:
                    for picking in purchase_order.picking_ids:
                        bacth_id = self.env['stock.picking.to.batch'].create(
                            {'batch_id': picking_batch.id}
                        )
                        bacth_id.with_context({'active_ids': picking.id}).attach_pickings()
        return purchase_order

    def generate_po(self):
        # Purchase order lines
        self.create_po(self.product_id, self.line_ids, self, False)
        # Purchase order transport
        self.create_po(self.product_transport_id, [self.transport_id], self, True)
        self.state = 'closed'
        return True

    
    def unlink(self):
        for purchase in self:
            if not purchase.state == 'draft':
                raise UserError(
                    _('In order to delete a product collect, you must draft it first.')
                )
        return super(ProductCollect, self).unlink()

    def confirm(self):
        self.state = 'confirm'
        return True

    def cancel(self):
        self.state = 'cancel'
        return True

    def to_draft(self):
        self.state = 'draft'
        return True

    def batch_confirm(self):
        active_ids = self.env.context.get('active_ids', [])
        for item in self.browse(active_ids):
            if item.state == 'draft':
                item.state = 'confirm'
            if item.state == 'confirm':
                item.state = 'draft'

    def batch_generate_po(self):
        active_ids = self.env.context.get('active_ids', [])
        for item in self.browse(active_ids):
            if item.state == 'confirm':
                item.generate_po()

class ProductCollectLines(models.Model):
    _name = 'product.collect.lines'
    _description = 'Product Collect Lines'

    product_collect_id = fields.Many2one('product.collect',
                                          string='Product Collect',
                                          required=True,
                                          index=True,
                                          ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Partner',
                                 required=True, index=True)
    purchase_id = fields.Many2one('purchase.order', string='Purchase order',
                                  required=False, index=True, copy=False,
                                  readonly=True)
    qty_po = fields.Integer(string='Tinas', default=0.0, required=True, copy=False)
    factor = fields.Float(string='Factor')
    qty = fields.Integer(string='Liters',  default=0.0, required=True, copy=False)
    quantity = fields.Integer(compute='_get_quantity', string='Quantity', store=True)
    description = fields.Text(string='Description')
    price_unit = fields.Float(string='Price unit')
    price_total = fields.Float(compute='_get_total', string='Price total', store=True)

    @api.depends('price_unit', 'quantity')
    def _get_quantity(self):
        for line in self:
            line.quantity = line.qty_po * line.factor + line.qty

    @api.depends('price_unit', 'quantity')
    def _get_total(self):
        for line in self:
            line.price_total = line.price_unit * line.quantity

    @api.onchange('partner_id')
    def onchange_partner(self):
        products = self.product_collect_id.product_id.seller_ids.filtered(
            lambda r: r.name.id == self.partner_id.id and r.price
        )
        price = products[0].price if products else self.product_collect_id.product_id.standard_price
        if not price:
            price = self.product_collect_id.product_id.standard_price
        self.price_unit = price
        factor = products[0].product_uom.factor_inv if products else self.product_collect_id.product_id.uom_po_id.factor_inv
        if not factor:
            factor = self.product_collect_id.product_id.uom_po_id.factor_inv
        self.factor = factor

    @api.onchange('qty_po', 'qty')
    def onchange_quantity(self):
        quantity = self.qty_po * self.factor + self.qty
        self.quantity = quantity
        price_total = self.quantity * self.price_unit
        self.price_total = price_total


class StockPickingToBatch(models.TransientModel):
    _inherit = 'stock.picking.to.batch'

    
    def attach_pickings(self):
        # use active_ids to add picking line to the selected batch
        # self.ensure_one()
        picking_ids = self.env.context.get('active_ids')
        return self.env['stock.picking'].browse(picking_ids).write({'batch_id': self.batch_id.id})


class PurchaseOrderLineExtended(models.Model):
    _inherit = 'purchase.order.line'

    picking_type_id = fields.Many2one('stock.picking.type', string='Picking type', index=True)
    stock_holder = fields.Selection([('sh', 'Stock holder'), ('nsh', 'Not Stock holder')],
                                    'Stock holder', default='nsh', required=True)

    @api.model
    def create(self, vals):
        if vals.get('order_id'):
            order_id = self.env['purchase.order'].browse(vals.get('order_id'))
            vals['picking_type_id'] = order_id.picking_type_id.id
            vals['stock_holder'] = order_id.partner_id.stock_holder
        return super(PurchaseOrderLineExtended, self).create(vals)

    
    def write(self, vals):
        for record in self:
            if record.order_id:
                order_id = record.order_id
                vals['picking_type_id'] = order_id.picking_type_id.id
                vals['stock_holder'] = order_id.partner_id.stock_holder
        return super(PurchaseOrderLineExtended, self).write(vals)

class PartnerSupplies(models.Model):
    _inherit = 'res.partner'

    supply = fields.Boolean(string='Supplies')


class OrdersSupplies(models.Model):
    _inherit = 'sale.order'

    supplies = fields.Boolean(string='Supplies')

    @api.model
    def create(self, vals):
        if vals.get('supplies', False):
            vals['name'] = self.env['ir.sequence'].next_by_code('supplies.order') or _('New')
            _logger.debug(vals['name'])
        res = super(OrdersSupplies, self).create(vals)
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        context = self._context or {}
        res = super(OrdersSupplies, self).fields_view_get(view_id=view_id, view_type=view_type,
                                                          toolbar=toolbar, submenu=False)
        if context.get('supplies'):
            if res.get('fields').get('partner_id'):
                res.get('fields').get('partner_id')['string'] = 'Applicant'
            if res.get('fields').get('state'):
                res.get('fields').get('state').get('selection')[0] = ('draft', 'Draft')
                res.get('fields').get('state').get('selection')[1] = ('sent', 'Sent')
                res.get('fields').get('state').get('selection')[2] = ('sale', 'Confirmed')
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='partner_id']"):
                node.set('domain', "[('supply', '=', True)]")
            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res


class OrdersSuppliesLines(models.Model):
    _inherit = 'sale.order.line'

    def _get_domain(self):
        domain = "[('sale_ok','=',True)]"
        if self.env.context.get('supplies'):
            domain = "[('purchase_ok','=',True),('can_be_expensed','=',True),('type','=','product')]"
        _logger.info(domain)
        return domain

    product_id = fields.Many2one('product.product', string='Producto', domain=_get_domain)
