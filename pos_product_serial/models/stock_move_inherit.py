# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

class StockMoveInh(models.Model):
    _inherit = 'stock.move'
    pos_order_line_id = fields.Many2one('pos.order.line')

    def get_lots(self):
        source = self.picking_id.origin
        if source:
            pos_order_id = self.env['pos.order'].search([('name', '=', source)], limit=1)
            if pos_order_id:
                near_quants = self.env['stock.quant']
                remote_quants = self.env['stock.quant']
                near_pack_lot_names = self.pos_order_line_id.pack_lot_ids.filtered(
                    lambda c: c.location_id == self.location_id)
                remote_pack_lot_names = self.pos_order_line_id.pack_lot_ids.filtered(
                    lambda c: c.location_id != self.location_id)
                if near_pack_lot_names:
                    near_quants = self.env['stock.quant'].search(
                        [('location_id', '=', self.location_id.id),
                         ('lot_id.name', 'in', near_pack_lot_names.mapped('lot_name'))])
                if remote_pack_lot_names:
                    loc_id = remote_pack_lot_names.mapped('location_id')

                    remote_quants = self.env['stock.quant'].search(
                        [('location_id', '=', loc_id.id),
                         ('lot_id.name', 'in', remote_pack_lot_names.mapped('lot_name'))])

                return [near_quants, remote_quants]
        return False

    @api.multi
    def _action_assign(self):
        for rec in self:
            if rec.picking_type_id.code == 'outgoing' and rec.product_id.tracking in ['lot','serial']:
                if rec.state != 'assigned':
                    if rec.state == 'partially_available':
                        rec.move_line_ids.unlink()
                    result = rec.get_lots()
                    print(result)
                    if result:
                        if not result[1]:
                            res = result[0].mapped('lot_id')
                            super(StockMoveInh, rec.with_context(lots=res))._action_assign()
                        elif not result[0]:
                            res = result[1].mapped('lot_id')
                            super(StockMoveInh, rec.with_context(lots=res))._action_assign()
                            lott_ids = rec.pos_order_line_id.pack_lot_ids.filtered(
                                lambda f: f.location_id != rec.location_id)
                            picks = self.env['stock.picking'].search([('id','!=',rec.picking_id.id),('origin','=',rec.picking_id.origin),('picking_type_id.code','=','internal'),('state','=','done')])
                            if not picks:
                                for y in rec.move_line_ids:
                                    if y.location_id.id not in [lot.location_id.id for lot in lott_ids]:
                                        y.unlink()
                        else:

                            res = result[0].mapped('lot_id')
                            lott_names = rec.pos_order_line_id.pack_lot_ids.filtered(
                                lambda f: f.location_id != rec.location_id).mapped('lot_name')
                            lotts = self.env['stock.production.lot'].search([('name', 'in', lott_names)])
                            lotts |= res

                            super(StockMoveInh, rec.with_context(lots=lotts))._action_assign()
                            print(lotts)
                            rec.move_line_ids.filtered(lambda m: m.lot_id not in lotts).unlink()
                    else:
                        super(StockMoveInh, rec)._action_assign()
                else:
                    super(StockMoveInh, rec)._action_assign()
            else:
                super(StockMoveInh, rec)._action_assign()
        return True


class StockQuantInherit(models.Model):
    _inherit = 'stock.quant'

    def _gather(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False):
        quants = super(StockQuantInherit, self)._gather(product_id, location_id, lot_id, package_id, owner_id, strict)
        lots = self.env.context.get('lots')
        if lots:
            quants = quants.filtered(lambda x: x.lot_id in lots)
            print(quants)
        return quants


class NewModule(models.Model):
    _inherit = 'pos.order'

    def get_lot(self, move):
        if move.pos_order_line_id:
            near_quants=self.env['stock.quant']
            remote_quants=self.env['stock.quant']
            near_pack_lot_names = move.pos_order_line_id.pack_lot_ids.filtered(lambda c:c.location_id==self.location_id)
            remote_pack_lot_names = move.pos_order_line_id.pack_lot_ids.filtered(lambda c:c.location_id != self.location_id)
            if near_pack_lot_names:
                near_quants = self.env['stock.quant'].search(
                        [('location_id', '=', self.location_id.id), ('lot_id.name', 'in', near_pack_lot_names.mapped('lot_name'))])
            if remote_pack_lot_names:
                loc_id = remote_pack_lot_names.mapped('location_id')
                remote_quants = self.env['stock.quant'].search(
                        [('location_id', '=', loc_id.id), ('lot_id.name', 'in', remote_pack_lot_names.mapped('lot_name'))])
            return [near_quants, remote_quants]
        return False

    def _force_picking_done(self, picking):
        """Force picking in order to be set as done."""
        self.ensure_one()
        remote_lots = self.env['stock.production.lot']
        for order in self:
            picking_moves = []
            for move in order.picking_id.move_lines:
                if move.product_id.tracking in ['lot','serial']:
                    result = order.get_lot(move)
                    print("result",result)
                    if result[1]:
                        available_qty = 0
                        if result[0]:
                            for quant in result[0]:
                                available_qty += quant.quantity - quant.reserved_quantity
                        else:
                            available_qty =0
                        if available_qty >= 0:
                            required_qty = move.product_uom_qty - available_qty
                            if required_qty > 0:
                                picking_moves.append((move, required_qty))
                        for lo in result[1]:
                            remote_lots |= lo.lot_id

            if picking_moves:
                picking_type_id = order.session_id.config_id.git_picking_type_id
                picking_vals = {
                    'origin': order.name,
                    'date_done': self.date_order,
                    'picking_type_id': picking_type_id.id,
                    'company_id': self.company_id.id,
                    'move_type': 'direct',
                    'note': self.note or "",
                    'location_id': picking_type_id.default_location_src_id.id,
                    'location_dest_id': picking_type_id.default_location_dest_id.id,
                }
                picking_obj = self.env['stock.picking'].create(picking_vals)
                for line in picking_moves:
                    move_vals = {
                        'name': line[0].name,
                        'product_uom': line[0].product_uom.id,
                        'picking_id': picking_obj.id,
                        'picking_type_id': picking_type_id.id,
                        'product_id': line[0].product_id.id,
                        'product_uom_qty': line[1],
                        'state': 'draft',
                        'location_id': picking_type_id.default_location_src_id.id,
                        'location_dest_id': picking_type_id.default_location_dest_id.id,
                    }
                    self.env['stock.move'].create(move_vals)

                picking_obj.action_confirm()

                picking_obj.with_context(lots=remote_lots).action_assign()
                picking.action_assign()
            else:
                picking.action_assign()
                for move in picking.move_lines:
                    # if move.product_id.tracking in ['lot','serial']:
                    for move_line in move.move_line_ids:
                        move_line.write({'qty_done': move_line.product_uom_qty})
                picking.action_done()
        # wrong_lots = self.set_pack_operation_lot(picking)
        # if not wrong_lots:
        #     picking.action_done()

    def create_picking(self):
        """Create a picking for each order and validate it."""
        Picking = self.env['stock.picking']
        Move = self.env['stock.move']
        StockWarehouse = self.env['stock.warehouse']
        for order in self:
            if not order.lines.filtered(lambda l: l.product_id.type in ['product', 'consu']):
                continue
            address = order.partner_id.address_get(['delivery']) or {}
            picking_type = order.picking_type_id
            return_pick_type = order.picking_type_id.return_picking_type_id or order.picking_type_id
            order_picking = Picking
            return_picking = Picking
            moves = Move
            location_id = order.location_id.id
            if order.partner_id:
                destination_id = order.partner_id.property_stock_customer.id
            else:
                if (not picking_type) or (not picking_type.default_location_dest_id):
                    customerloc, supplierloc = StockWarehouse._get_partner_locations()
                    destination_id = customerloc.id
                else:
                    destination_id = picking_type.default_location_dest_id.id

            if picking_type:
                message = _(
                    "This transfer has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (
                              order.id, order.name)
                picking_vals = {
                    'origin': order.name,
                    'partner_id': address.get('delivery', False),
                    'date_done': order.date_order,
                    'picking_type_id': picking_type.id,
                    'company_id': order.company_id.id,
                    'move_type': 'direct',
                    'note': order.note or "",
                    'location_id': location_id,
                    'location_dest_id': destination_id,
                }
                pos_qty = any([x.qty > 0 for x in order.lines if x.product_id.type in ['product', 'consu']])
                if pos_qty:
                    order_picking = Picking.create(picking_vals.copy())
                    order_picking.message_post(body=message)
                neg_qty = any([x.qty < 0 for x in order.lines if x.product_id.type in ['product', 'consu']])
                if neg_qty:
                    return_vals = picking_vals.copy()
                    return_vals.update({
                        'location_id': destination_id,
                        'location_dest_id': return_pick_type != picking_type and return_pick_type.default_location_dest_id.id or location_id,
                        'picking_type_id': return_pick_type.id
                    })
                    return_picking = Picking.create(return_vals)
                    return_picking.message_post(body=message)

            for line in order.lines.filtered(
                    lambda l: l.product_id.type in ['product', 'consu'] and not float_is_zero(l.qty,
                                                                                              precision_rounding=l.product_id.uom_id.rounding)):
                moves |= Move.create({
                    'name': line.name,
                    'product_uom': line.product_id.uom_id.id,
                    'picking_id': order_picking.id if line.qty >= 0 else return_picking.id,
                    'picking_type_id': picking_type.id if line.qty >= 0 else return_pick_type.id,
                    'product_id': line.product_id.id,
                    'product_uom_qty': abs(line.qty),
                    'state': 'draft',
                    'pos_order_line_id': line.id,
                    'location_id': location_id if line.qty >= 0 else destination_id,
                    'location_dest_id': destination_id if line.qty >= 0 else return_pick_type != picking_type and return_pick_type.default_location_dest_id.id or location_id,
                })

            # prefer associating the regular order picking, not the return
            order.write({'picking_id': order_picking.id or return_picking.id})

            if return_picking:
                order._force_picking_done(return_picking)
            if order_picking:
                order._force_picking_done(order_picking)

            # when the pos.config has no picking_type_id set only the moves will be created
            if moves and not return_picking and not order_picking:
                moves._action_assign()
                moves.filtered(lambda m: m.product_id.tracking == 'none')._action_done()

        return True
