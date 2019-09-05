# -*- coding: utf-8 -*-
from odoo import http

# class NasijProjectSaleOrder(http.Controller):
#     @http.route('/nasij_project_sale_order/nasij_project_sale_order/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/nasij_project_sale_order/nasij_project_sale_order/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('nasij_project_sale_order.listing', {
#             'root': '/nasij_project_sale_order/nasij_project_sale_order',
#             'objects': http.request.env['nasij_project_sale_order.nasij_project_sale_order'].search([]),
#         })

#     @http.route('/nasij_project_sale_order/nasij_project_sale_order/objects/<model("nasij_project_sale_order.nasij_project_sale_order"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('nasij_project_sale_order.object', {
#             'object': obj
#         })