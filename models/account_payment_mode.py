from odoo import fields, models


class AccountPaymentMode(models.Model):
    _inherit = "account.payment.mode"

    pichincha_tipo = fields.Char(
        string="Pichincha: Tipo",
        default="PA",
        help="Valor de la columna 'tipo' en el archivo exportado.",
    )
    pichincha_cta = fields.Char(
        string="Pichincha: Forma de Pago",
        default="CTA",
        help="Valor de la columna 'CTA' en el archivo exportado.",
    )
    pichincha_default_account_type = fields.Char(
        string="Pichincha: Tipo de Cuenta por Defecto",
        default="AHO",
        help=(
            "Se usa cuando no se puede inferir el tipo de cuenta desde el "
            "beneficiario."
        ),
    )
    pichincha_currency = fields.Char(
        string="Pichincha: Moneda",
        default="USD",
        help="Valor de la columna 'moneda' en el archivo exportado.",
    )
    pichincha_include_header = fields.Boolean(
        string="Pichincha: Incluir Cabecera",
        default=False,
        help="Si está activo, agrega una primera línea con los nombres de columnas.",
    )
