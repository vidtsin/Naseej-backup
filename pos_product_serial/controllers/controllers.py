# -*- coding: utf-8 -*-
from odoo import http

# class PosProductSerial(http.Controller):
#     @http.route('/pos_product_serial/pos_product_serial/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_product_serial/pos_product_serial/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_product_serial.listing', {
#             'root': '/pos_product_serial/pos_product_serial',
#             'objects': http.request.env['pos_product_serial.pos_product_serial'].search([]),
#         })

#     @http.route('/pos_product_serial/pos_product_serial/objects/<model("pos_product_serial.pos_product_serial"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_product_serial.object', {
#             'object': obj
#         })