# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp
import json


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def get_serials(self, location_id, product_id):
        if location_id and product_id:
            domain = [('product_id', '=', int(product_id)), ('location_id', '=', int(location_id))]
            res = self.env['stock.quant'].search(domain)
            result = []
            for line in res:
                if (line.quantity - line.reserved_quantity) > 0:
                    result.append(
                        {"cid": 0, "quantity": (line.quantity - line.reserved_quantity), "lot_name": line.lot_id.name,
                         "location_id": location_id,
                         "lot_id": line.lot_id.id, "reserved_qty": line.reserved_quantity,
                         "onhand_qty": line.quantity, })

            return result
