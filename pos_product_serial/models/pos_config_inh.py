from odoo import fields, models, exceptions, _, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    git_picking_type_id = fields.Many2one(
        'stock.picking.type', string="Second Operation Type", domain=[('code', '=', 'internal')],
        default=lambda self: self.env['stock.picking.type'].search([('code', '=', 'internal')], limit=1).id,
    )

    def _get_git_default_location(self):
        return self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)],
                                                  limit=1).lot_stock_id

    git_stock_location_id = fields.Many2one(
        'stock.location', string='Second Stock Location',
        domain=[('usage', '=', 'internal')], required=True, default=_get_git_default_location)

    @api.constrains('company_id', 'git_stock_location_id')
    def _check_company_location(self):
        if self.git_stock_location_id.company_id and self.git_stock_location_id.company_id.id != self.company_id.id:
            raise exceptions.ValidationError(
                _("The Second stock location and the point of sale must belong to the same company."))

    @api.onchange('git_picking_type_id')
    def _onchange_git_picking_type_id(self):
        if self.git_picking_type_id.default_location_src_id.usage == 'internal' and self.git_picking_type_id.default_location_dest_id.usage == 'internal':
            self.git_stock_location_id = self.git_picking_type_id.default_location_src_id.id

    def get_locations(self):
        loc1 = self.picking_type_id.default_location_src_id
        loc2 = self.git_picking_type_id.default_location_src_id
        loc_list = [
            {'id': loc1.id, "name": loc1.name_get()[0][1]},
            {'id': loc2.id, "name": loc2.name_get()[0][1]},
        ]
        print(loc_list)
        return loc_list
