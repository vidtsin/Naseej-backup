# -*- coding: utf-8 -*-
from odoo import http

# class NaseejInventory(http.Controller):
#     @http.route('/naseej_inventory/naseej_inventory/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/naseej_inventory/naseej_inventory/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('naseej_inventory.listing', {
#             'root': '/naseej_inventory/naseej_inventory',
#             'objects': http.request.env['naseej_inventory.naseej_inventory'].search([]),
#         })

#     @http.route('/naseej_inventory/naseej_inventory/objects/<model("naseej_inventory.naseej_inventory"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('naseej_inventory.object', {
#             'object': obj
#         })