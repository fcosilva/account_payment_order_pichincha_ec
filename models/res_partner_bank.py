from odoo import fields, models


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    transfer_account_type = fields.Selection(
        selection=[
            ("AHO", "Ahorro (AHO)"),
            ("CTE", "Corriente (CTE)"),
            ("VIR", "Virtual (VIR)"),
        ],
        string="Tipo de Cuenta Transferencia",
        help=(
            "Tipo de cuenta para archivos de pago bancarios. "
            "Si está vacío, cada exportador puede aplicar su lógica por defecto."
        ),
    )
    pichincha_account_type = fields.Selection(
        selection=[
            ("AHO", "Ahorro (AHO)"),
            ("CTE", "Corriente (CTE)"),
            ("VIR", "Virtual (VIR)"),
        ],
        string="Pichincha: Tipo de Cuenta (legacy)",
        help="Campo legado mantenido por compatibilidad.",
    )
