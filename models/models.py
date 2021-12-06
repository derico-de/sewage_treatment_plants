from odoo import models, fields, api


class PartnerRouteFields(models.Model):
    _inherit = "res.partner"
    _description = "Route fields to sort partner on routes and order in route"

    route_name = fields.Char(string="Route")
    route_position = fields.Integer(string="Route Position", default=10)


class PartnerBankAccountInfo(models.Model):
    _inherit = "res.partner"
    _description = "Shortened partner bank account info"

    bank_acc_info_short = fields.Char(
        compute="_compute_bank_acc_info_short", string="Bank account info short"
    )

    @api.depends("bank_ids.acc_number")
    def _compute_bank_acc_info_short(self):
        # import pdb; pdb.set_trace()  # NOQA: E702
        for partner in self:
            if not partner.bank_ids:
                partner.bank_acc_info_short = ""
                return
            bank = partner.bank_ids[0]
            acc_number = bank.acc_number.replace(" ", "")
            # short info is only the last 4 digits
            partner.bank_acc_info_short = "{0} / IBAN: {1}XX XXXX XXXX XXXX XX{2} {3}".format(
                bank.bank_name, acc_number[:2], acc_number[-4:-2], acc_number[-2:]
            )


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
