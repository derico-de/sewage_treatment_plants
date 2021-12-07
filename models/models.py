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
        for partner in self:
            if not partner.bank_ids:
                partner.bank_acc_info_short = ""
                return
            bank = partner.bank_ids[0]
            bank_name = bank.bank_name or ""
            acc_number = bank.acc_number.replace(" ", "")
            # short info is only parts of the IBAN with optinal bank name
            partner.bank_acc_info_short = (
                "IBAN: {0}XX XXXX XXXX XXXX XX{1} {2}".format(
                    acc_number[:2], acc_number[-4:-2], acc_number[-2:]
                )
            )
            if bank_name:
                partner.bank_acc_info_short = partner.bank_acc_info_short + " bei der {0}.".format(bank_name)


class PartnerAzvLk(models.Model):
    _inherit = "res.partner"
    type = fields.Selection(
        [
            ("contact", "Contact"),
            ("abwasserzweckverband", "Abwasserzweckverband"),
            ("landkreis", "Landkreis"),
            ("invoice", "Invoice Address"),
            ("delivery", "Delivery Address"),
            ("other", "Other Address"),
            ("private", "Private Address"),
        ],
        string="Address Type",
        default="contact",
        help="Invoice & Delivery addresses are used in sales orders. Private addresses are only visible by authorized users.",
    )
    azv = fields.Many2one(
        "res.partner",
        string="Abwasserzweckverband",
        context={"default_type": "abwasserzweckverband"},
        domain="[('type','=','abwasserzweckverband')]",
        index=True,
    )
    landkreis = fields.Many2one(
        "res.partner",
        string="Landkreis",
        context={"default_type": "landkreis"},
        domain="[('type','=','landkreis')]",
        index=True,
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
