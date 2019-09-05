# -*- coding: utf-8 -*-
from odoo import http

# class NaseejProjectPos(http.Controller):
#     @http.route('/naseej_project_pos/naseej_project_pos/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/naseej_project_pos/naseej_project_pos/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('naseej_project_pos.listing', {
#             'root': '/naseej_project_pos/naseej_project_pos',
#             'objects': http.request.env['naseej_project_pos.naseej_project_pos'].search([]),
#         })

#     @http.route('/naseej_project_pos/naseej_project_pos/objects/<model("naseej_project_pos.naseej_project_pos"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('naseej_project_pos.object', {
#             'object': obj
#         })