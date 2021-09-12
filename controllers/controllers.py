# -*- coding: utf-8 -*-
# from odoo import http


# class SewageTreatmentPlants(http.Controller):
#     @http.route('/sewage_treatment_plants/sewage_treatment_plants/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sewage_treatment_plants/sewage_treatment_plants/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sewage_treatment_plants.listing', {
#             'root': '/sewage_treatment_plants/sewage_treatment_plants',
#             'objects': http.request.env['sewage_treatment_plants.sewage_treatment_plants'].search([]),
#         })

#     @http.route('/sewage_treatment_plants/sewage_treatment_plants/objects/<model("sewage_treatment_plants.sewage_treatment_plants"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sewage_treatment_plants.object', {
#             'object': obj
#         })
