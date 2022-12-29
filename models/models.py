from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form
from odoo.tools.translate import _


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
            partner.bank_acc_info_short = "IBAN: {0}XX XXXX XXXX XXXX XX{1} {2}".format(
                acc_number[:2], acc_number[-4:-2], acc_number[-2:]
            )
            if bank_name:
                partner.bank_acc_info_short = (
                    partner.bank_acc_info_short + " bei der {0}.".format(bank_name)
                )


class ResPartnerBankAccMultiPartner(models.Model):
    _inherit = "res.partner.bank"
    _description = "allow the same bank account (acc) to be used on multiple partners"


    _sql_constraints = [
        ('unique_number', 'unique(sanitized_acc_number, company_id, partner_id)', 'Account Number must be unique'),
    ]


class PartnerAzvLk(models.Model):
    _inherit = "res.partner"
    _description = "Extend type selection list to add Abwasserzweckverband & Landkreis"
    type = fields.Selection(
        selection_add=[
            ("abwasserzweckverband", "Abwasserzweckverband"),
            ("landkreis", "Landkreis"),
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


class AccountMoveSTP(models.Model):
    _inherit = "account.move"
    _description = "Add partner comment to invoice"

    partner_comment = fields.Text(
        compute="_compute_partner_comment", string="Partner Comment"
    )

    @api.depends("partner_id.comment")
    def _compute_partner_comment(self):
        for invoice in self:
            invoice.partner_comment = invoice.partner_id.comment


class ContractContractSTP(models.Model):
    _inherit = "contract.contract"
    _description = "prevent setting invoice date from contracts."

    # override to disable setting of invoice date from contracts:
    def _prepare_invoice(self, date_invoice, journal=None):
        """Prepare in a Form the values for the generated invoice record.

        :return: A tuple with the vals dictionary and the Form with the
          preloaded values for being used in lines.
        """
        self.ensure_one()
        if not journal:
            journal = (
                self.journal_id
                if self.journal_id.type == self.contract_type
                else self.env["account.journal"].search(
                    [
                        ("type", "=", self.contract_type),
                        ("company_id", "=", self.company_id.id),
                    ],
                    limit=1,
                )
            )
        if not journal:
            raise ValidationError(
                _("Please define a %s journal for the company '%s'.")
                % (self.contract_type, self.company_id.name or "")
            )
        invoice_type = "out_invoice"
        if self.contract_type == "purchase":
            invoice_type = "in_invoice"
        move_form = Form(
            self.env["account.move"]
            .with_company(self.company_id)
            .with_context(default_move_type=invoice_type)
        )
        move_form.partner_id = self.invoice_partner_id
        if self.payment_term_id:
            move_form.invoice_payment_term_id = self.payment_term_id
        if self.fiscal_position_id:
            move_form.fiscal_position_id = self.fiscal_position_id
        invoice_vals = move_form._values_to_save(all_fields=True)
        invoice_vals.update(
            {
                "ref": self.code,
                "company_id": self.company_id.id,
                "currency_id": self.currency_id.id,
                # "invoice_date": date_invoice,
                "journal_id": journal.id,
                "invoice_origin": self.name,
                "invoice_user_id": self.user_id.id,
            }
        )
        return invoice_vals, move_form


class SewageTreadmentPlant(models.Model):
    _name = 'stp.stp'
    _description = 'Sewage Treadment Plant'
    # _inherit = ["mail.thread", "mail.activity.mixin"]
    name = fields.Char("Anlagentyp", required="True")
    manufacturer = fields.Char("Hersteller")
    control_unit = fields.Char("Steuerung")
    type_of_functional_unit = fields.Selection(
        [
            ("Tropfkörper", "Tropfkörper"),
            ("Festbett", "Festbett"),
            ("SBR", "SBR"),
            ("Pflanzenbeet", "Planzenbeet"),
            ("Launhardt-R.", "Launhardt-R."),
            ("Teichanlage", "Teichanlage"),
        ],
        "Art der Kleinkläranlage/Funktionseinheit"
    )
    method_of_construction = fields.Selection(
        [
            ("Beton", "Beton"),
            ("Kunststoff", "Kunststoff"),
        ],
        "Art der Kleinkläranlage/Funktionseinheit"
    )


class SewageTreatmentPlantLocation(models.Model):
    _inherit = ["fsm.location"]

    # name = fields.Char(string="Name", required="True")
    # partner_id = fields.Many2one("res.partner", string="Partner")
    ew = fields.Char('EW', help="Anzahl an Einwohnern für welche die Kläranlage ausgelegt ist.")
    stp_stp_id = fields.Many2one('stp.stp', string='Anlage')


class SewageTreatmentPlantMaintenance(models.Model):
    _inherit = ["fsm.order"]

    # name = fields.Char(string="Name", required="True")
    # partner_id = fields.Many2one("res.partner", string="Partner")

    datetime = fields.Datetime(string="Datum/Zeit")
    temperature = fields.Char('Temperatur in ℃')
    wheather = fields.Selection([
        ('sonne', 'Sonne'),
        ('regen', 'Regen'),
        ('bedeckt', 'Bedeckt'),
    ], string='Wetter')
    malfunctions = fields.Char('Mängel')

    earator_compressor_actuation_operating_hours = fields.Integer('Belüfter/Kompressor/Antrieb: Betrtiebsstunden')
    earator_compressor_actuation_interval_pause_before = fields.Char('Belüfter/Kompressor/Antrieb: Laufzeit/Pause vorher')
    earator_compressor_actuation_interval_pause_after = fields.Char('Belüfter/Kompressor/Antrieb: Laufzeit/Pause nachher')
    pl_charger_operating_hours = fields.Integer('Operating Hours')
    pl_charger_interval_pause_before = fields.Char('Laufzeit/Pause vorher')
    pl_charger_interval_pause_after = fields.Char('Laufzeit/Pause nachher')
    pl_sludge_operating_hours = fields.Integer('Operating Hours')
    pl_sludge_interval_pause_before = fields.Char('Laufzeit/Pause vorher')
    pl_sludge_interval_pause_after = fields.Char('Laufzeit/Pause nachher')
    pl_decandted_water_operating_hours = fields.Integer('Operating Hours')
    pl_decandted_water_interval_pause_before = fields.Char('Laufzeit/Pause vorher')
    pl_decandted_water_interval_pause_after = fields.Char('Laufzeit/Pause nachher')
    pl_reflux_water_operating_hours = fields.Integer('Operating Hours')
    pl_reflux_water_interval_pause_before = fields.Char('Laufzeit/Pause vorher')
    pl_reflux_water_interval_pause_after = fields.Char('Laufzeit/Pause nachher')
    pl_post_purification_operating_hours = fields.Integer('Operating Hours')
    pl_post_purification_interval_pause_before = fields.Char('Laufzeit/Pause vorher')
    pl_post_purification_interval_pause_after = fields.Char('Laufzeit/Pause nachher')

    # collected parameters table
    csb = fields.Float("CSB in mg/l")
    bsb5 = fields.Float("BSB5 in mg/l")
    o2 = fields.Float("O2 in mg/l")
    ph = fields.Float("pH")
    sludgevol = fields.Float("Schlammvol. in ml/l")
    sedimentable_materials = fields.Float("Absetzbare Stoffe in ml/l")
    layer_depth = fields.Float("Schichttiefe in cm")
    smell = fields.Selection(
        [
            ("neutral", "neutral"),
            ("leicht muffig", "leicht muffig"),
            ("jauchig", "jauchig"),
        ],
        string="Geruch",
    )
    color = fields.Selection(
        [("klar", "klar"), ("leicht trüb", "leicht trüb"), ("trüb", "trüb")],
        string="Farbe",
    )
    temperature = fields.Float("Temperatur in ℃")

    # pre-clarification / sludge storage/level
    water_depth = fields.Float("Wassertiefe in m")
    chamber1 = fields.Float("Kammer 1 in m")
    chamber2 = fields.Float("Kammer 2 in m")
    chamber3 = fields.Float("Kammer 3 in m")
    chamber4 = fields.Float("Kammer 4 in m")
    sludge_fraction = fields.Char("Schlammanteil in %")

    # order sludge removal?
    sludge_removal_chamber = fields.Selection(
        [
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
            ("4", "4"),
        ],
        string="Kammer",
    )
    sludge_removal_chamber_comment = fields.Char("sonst. Kammer")
    sludge_removal_chamber_oder = fields.Boolean("Abfuhr veranlassen")
    sludge_removal_chamber_oder_month = fields.Selection(
        [
            ("Januar", "Januar"),
            ("Februar", "Februar"),
            ("März", "März"),
            ("April", "April"),
            ("Mai", "Mai"),
            ("Juni", "Juni"),
            ("Julie", "Julie"),
            ("August", "August"),
            ("September", "September"),
            ("Oktober", "Oktober"),
            ("November", "November"),
            ("Dezember", "Dezember"),
        ],
        string="Monat",
    )

    regular_maintenance_of_the_log_book = fields.Boolean("Regelmäßige Führung des Betriebsbuches")
    service_order = fields.Boolean("Auftrag zur Mängelbeseitigung")

    poweroutage = fields.Char('Netzausfall')
    service_note = fields.Char('Bemerkung')

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
