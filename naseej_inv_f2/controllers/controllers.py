# -*- coding: utf-8 -*-
from odoo import http

# class NaseejInvF2(http.Controller):
#     @http.route('/naseej_inv_f2/naseej_inv_f2/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/naseej_inv_f2/naseej_inv_f2/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('naseej_inv_f2.listing', {
#             'root': '/naseej_inv_f2/naseej_inv_f2',
#             'objects': http.request.env['naseej_inv_f2.naseej_inv_f2'].search([]),
#         })

#     @http.route('/naseej_inv_f2/naseej_inv_f2/objects/<model("naseej_inv_f2.naseej_inv_f2"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('naseej_inv_f2.object', {
#             'object': obj
#         })