# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.exceptions import UserError, ValidationError


class NasijSaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('waiting_approve', 'Waiting Approve'),
        ('sale', 'Sales Order'),
        ('approved', 'Approved'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ('waiting', 'A Waiting Raw Material'),
        ('waiting_pro', 'A Waiting Production'),
        ('start', 'In Production'),
        ('finish', 'In Finishing Production'),
        ('done_pro', 'Complete')
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3,
        default='draft')

    not_available_lines = fields.Integer(string='Not Available', compute='compute_not_available')
    vendor = fields.Many2one('res.partner', string='Vendor',
                             index=True, track_visibility='always')

    po_ids = fields.One2many('purchase.order', 'sale_id', string='Purchase Orders')
    po_count = fields.Integer(string='Purchase Orders NO', compute='_compute_po_ids')

    app_checked = fields.Boolean('app Checked', default=False)
    po_checked = fields.Boolean('Checked', default=False)
    po_btn_checked = fields.Boolean('PO Checked', default=False)
    rec_name = fields.Char(default='PO')

    @api.multi
    @api.depends('order_line')
    def compute_not_available(self):
        order_lines = 0
        for line in self.order_line:
            if line._onchange_product_id_check_availability():
                order_lines += 1
        self.not_available_lines = order_lines

    @api.multi
    def check_availability(self):
        all_lines = len(self.order_line)
        if self.not_available_lines == 0:
            self.app_checked = True

        elif self.not_available_lines == all_lines:
            self.state = 'waiting_approve'

        else:
            raise Warning(_('you have to delete product not available first.'))

    @api.multi
    def approve(self):
        return self.write({'state': 'approved'})

    @api.multi
    def action_with_delivery(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm()))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'confirmation_date': fields.Datetime.now()
        })
        self._action_confirm()
        self.write({'state': 'waiting'})

        return True

    @api.multi
    def action_without_delivery(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm()))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'confirmation_date': fields.Datetime.now()
        })
        if self.env.context.get('send_email'):
            self.force_quotation_send()

        # create an analytic account if at least an expense product
        if any([expense_policy != 'no' for expense_policy in self.order_line.mapped('product_id.expense_policy')]):
            if not self.analytic_account_id:
                self._create_analytic_account()

        self.write({'state': 'waiting'})
        return True

    @api.multi
    def action_create_po(self):
        if not self.vendor:
            raise Warning(_('Please choose vendor '))

        else:
            self.write({'po_checked': False})
            self.write({'po_btn_checked': True})
            order_lines = []
            for rec in self.order_line:
                order_lines.append((0, 0, {
                    'name': rec.name,
                    'sequence': rec.sequence,
                    'price_subtotal': rec.price_subtotal,
                    'product_qty': rec.product_uom_qty,
                    'product_id': rec.product_id.id,
                    'price_unit': rec.price_unit,
                    'date_planned': self.date_order,
                    'product_uom': rec.product_uom.id,
                }))
            po_object = self.po_ids.create({
                # 'name': self.name,
                # 'origin': self.name,
                'partner_id': self.vendor.id,
                'order_line': order_lines,
            })
            # this if we want to automatic confirm po
            # po_object.button_confirm()
            return po_object

    @api.multi
    def action_waiting_pro(self):
        return self.write({'state': 'waiting_pro'})

    @api.multi
    def action_waiting_back(self):
        return self.write({'state': 'waiting'})

    @api.multi
    def action_waiting_pro_back(self):
        return self.write({'state': 'waiting_pro'})

    @api.multi
    def action_start(self):
        return self.write({'state': 'start'})

    @api.multi
    def action_start_back(self):
        return self.write({'state': 'start'})

    @api.multi
    def action_finish(self):
        return self.write({'state': 'finish'})

    @api.multi
    def action_done_production(self):
        self.write({'po_checked': True})
        return self.write({'state': 'done_pro'})

    @api.multi
    def action_confirm(self):
        all_lines = len(self.order_line)

        if self.not_available_lines == 0:
            if self._get_forbidden_state_confirm() & set(self.mapped('state')):
                raise UserError(_(
                    'It is not allowed to confirm an order in the following states: %s'
                ) % (', '.join(self._get_forbidden_state_confirm())))

            for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
                order.message_subscribe([order.partner_id.id])
            self.write({
                'state': 'sale',
                'confirmation_date': fields.Datetime.now()
            })
            self._action_confirm()
            if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
                self.action_done()
            return True
        elif self.not_available_lines == all_lines:
            self.state = 'waiting_approve'

        else:
            raise Warning(_('you have to delete product not available first.'))

    @api.depends('po_ids')
    def _compute_po_ids(self):
        for order in self:
            order.po_count = len(order.po_ids)

    @api.multi
    def action_view_po(self):

        action = self.env.ref('purchase.purchase_rfq').read()[0]

        po_s = self.mapped('po_ids')
        if len(po_s) > 1:
            action['domain'] = [('id', 'in', po_s.id)]
        elif po_s:
            action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
            action['res_id'] = po_s.id
        return action


class PurchaseEditing(models.Model):
    _inherit = 'purchase.order'

    sale_id = fields.Many2one('sale.order', string="Sales Order", store=True, readonly=False)
