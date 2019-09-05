# -*- coding: utf-8 -*-

from odoo import models, fields, api


class NaseejInventory(models.Model):
    _inherit = 'stock.picking.type'

    internal_loc = fields.Boolean('Is Internal?')
    internal_location = fields.Many2one('stock.location', string='Destination Transfer Location')
    internal_operation_type = fields.Many2one('stock.picking.type', string='Internal Operation Type')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    pack_picking_id = fields.Many2one('stock.picking', 'Pack Picking')
    show_button_generate = fields.Boolean(string="show click", compute='show_generate_btn', copy=False)
    after_click_button_generate = fields.Boolean(string="after click", copy=False)
    check_operation_type = fields.Boolean(string="check click", compute='_check_operation_type', copy=False)
    p_code = fields.Selection(related='picking_type_id.code')

    @api.onchange('p_code')
    def _check_operation_type(self):
        for pick in self:
            if pick.p_code == 'internal':
                self.check_operation_type = True

    @api.multi
    @api.onchange('picking_type_id')
    def show_generate_btn(self):
        for pick in self:
            if not pick.picking_type_id.internal_loc:
                pick.show_button_generate = False
            else:
                pick.show_button_generate = True


    @api.multi
    def generate_receipt_order(self):
        for p in self:
            pick = p.copy()
            internal_picking_type = p.picking_type_id.internal_operation_type
            pick_dest_location = p.picking_type_id.internal_location
            pick.write({'picking_type_id': internal_picking_type.id,
                        'location_id': p.location_dest_id.id,
                        'location_dest_id': pick_dest_location.id, })
            for line in pick.move_lines:
                line.write({
                    'picking_type_id': internal_picking_type.id,
                    'picking_id': pick.id,
                    'location_id': p.location_dest_id.id,
                    'location_dest_id': pick_dest_location.id

                })

            pick.action_confirm()
            pick.action_assign()
            pick.show_button_generate = False
            p.after_click_button_generate = True
            p.pack_picking_id = pick.id
