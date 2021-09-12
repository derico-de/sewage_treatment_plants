from odoo import models, fields


class PartnerRouteFields(models.Model):
    _inherit = 'res.partner'
    _description = 'Route fields to sort partner on routes and order in route'

    route_name = fields.Char(string='Route')
    route_position = fields.Integer(string='Route Position', default=10)


# class sewage_treatment_plants(models.Model):
#     _name = 'sewage_treatment_plants.sewage_treatment_plants'
#     _description = 'sewage_treatment_plants.sewage_treatment_plants'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()

#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
