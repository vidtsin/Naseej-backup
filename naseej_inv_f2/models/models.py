# -*- coding: utf-8 -*-

from odoo import models, fields, api


class NaseejInventoryF2(models.Model):
    _inherit = 'stock.picking.type'

    for_pos = fields.Boolean('For POS?')
    pos_operation_type = fields.Many2one('stock.picking.type', string='POS Operation Type')


class StockPickingF2(models.Model):
    _inherit = 'stock.picking'

    ch_update_button = fields.Boolean(string="Update Data", copy=False)
    pos_ref = fields.Char(related='picking_type_id.pos_operation_type.name')
    pick_ref = fields.Char(related='picking_type_id.name')
    pos_ch = fields.Boolean(related='picking_type_id.for_pos')
    after_click_button_generate = fields.Boolean(string="after click", copy=False)

    @api.multi
    def update_button(self):
        for pick in self:
            pos_pick = self.env['stock.picking'].search([
                ('pick_ref', '=', pick.pos_ref),
                ('origin', '=', pick.origin)])

            pos_pick.action_assign()
            # pos_pick.button_validate()
            pick.after_click_button_generate = True
