from odoo import _, fields, models
from odoo.exceptions import UserError


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    def _pichincha_sanitize_text(self, value):
        text = (value or "").strip()
        return text.replace("\t", " ").replace("\n", " ").replace("\r", " ")

    def _pichincha_digits_only(self, value):
        return "".join(ch for ch in (value or "") if ch.isdigit())

    def _pichincha_amount_to_cents(self, amount):
        amount = amount or 0.0
        cents = int(round(amount * 100))
        return str(cents)

    def _pichincha_partner_identification_type(self, partner):
        if hasattr(partner, "_l10n_ec_get_identification_type"):
            id_type = partner._l10n_ec_get_identification_type()
            if id_type == "cedula":
                return "C"
            if id_type == "ruc":
                return "R"
            if id_type in {"passport", "foreign"}:
                return "P"
        vat_digits = self._pichincha_digits_only(partner.vat)
        if len(vat_digits) == 13:
            return "R"
        if len(vat_digits) == 10:
            return "C"
        return "P"

    def _pichincha_account_type(self, partner_bank, payment_mode):
        if partner_bank.transfer_account_type:
            return partner_bank.transfer_account_type
        if partner_bank.pichincha_account_type:
            return partner_bank.pichincha_account_type
        acc_type = (partner_bank.acc_type or "").lower()
        if acc_type in {"current", "checking", "corriente"}:
            return "CTE"
        if acc_type in {"savings", "ahorros", "saving", "savings_account"}:
            return "AHO"
        if acc_type in {"virtual", "wallet"}:
            return "VIR"
        return payment_mode.pichincha_default_account_type or "AHO"

    def _pichincha_get_partner_bank(self, partner, fallback_bank=False):
        bank_accounts = partner.bank_ids.filtered(lambda b: b.acc_number)
        if bank_accounts:
            if "sequence" in bank_accounts._fields:
                bank_accounts = bank_accounts.sorted(
                    key=lambda b: (b.sequence or 0, b.id)
                )
            else:
                bank_accounts = bank_accounts.sorted("id")
            return bank_accounts[0]
        return fallback_bank

    def draft2open(self):
        # account_payment_order requires partner_bank_id on each payment line.
        # For Pichincha mode, auto-fill it from the beneficiary main bank account.
        for order in self:
            if order.payment_method_id.code == "ec_pichincha_tab":
                for line in order.payment_line_ids.filtered(lambda l: not l.partner_bank_id):
                    partner = line.partner_id.commercial_partner_id
                    partner_bank = order._pichincha_get_partner_bank(partner)
                    if partner_bank:
                        line.partner_bank_id = partner_bank.id
            # Ensure payment communication uses invoice document number.
            for line in order.payment_line_ids.filtered(
                lambda l: l.move_line_id and l.move_line_id.move_id.is_invoice()
            ):
                move = line.move_line_id.move_id
                line.communication = (
                    move.l10n_latam_document_number
                    or move.name
                    or move.ref
                    or move.payment_reference
                )
        return super().draft2open()

    def generate_payment_file(self):
        self.ensure_one()
        if self.payment_method_id.code != "ec_pichincha_tab":
            return super().generate_payment_file()

        if not self.payment_ids:
            raise UserError(_("No hay transacciones de pago para exportar."))

        payment_mode = self.payment_mode_id
        cta_value = self._pichincha_sanitize_text(payment_mode.pichincha_cta or "CTA")
        file_tipo = self._pichincha_sanitize_text(payment_mode.pichincha_tipo or "PA")
        file_currency = self._pichincha_sanitize_text(
            payment_mode.pichincha_currency or "USD"
        )

        lines = []
        if payment_mode.pichincha_include_header:
            lines.append(
                "\t".join(
                    [
                        "tipo",
                        "referencia",
                        "moneda",
                        "valor",
                        "CTA",
                        "tipo de cuenta",
                        "numero de cuenta",
                        "descripcion",
                        "tipo de identificacion",
                        "numero de identificacion",
                        "nombre",
                        "codigo ecuatoriano de banco",
                    ]
                )
            )

        for payment in self.payment_ids.sorted("id"):
            partner = payment.partner_id.commercial_partner_id
            line_communications = payment.payment_line_ids.mapped("communication")
            reference = " - ".join([c for c in line_communications if c])
            partner_bank = self._pichincha_get_partner_bank(
                partner, fallback_bank=payment.partner_bank_id
            )
            if not partner_bank:
                raise UserError(
                    _(
                        "El pago %(payment)s no tiene cuenta bancaria de "
                        "beneficiario.",
                        payment=payment.display_name,
                    )
                )

            bank_code = self._pichincha_sanitize_text(
                partner_bank.bank_id.l10n_ec_bank_code or partner_bank.bank_id.bic
            )
            if not bank_code:
                raise UserError(
                    _(
                        "Falta el código de banco en la cuenta %(bank)s del "
                        "beneficiario %(partner)s.",
                        bank=partner_bank.acc_number,
                        partner=partner.display_name,
                    )
                )

            ident_number = self._pichincha_digits_only(partner.vat)
            if not ident_number:
                raise UserError(
                    _(
                        "El beneficiario %(partner)s no tiene identificación "
                        "(RUC/Cédula) configurada.",
                        partner=partner.display_name,
                    )
                )

            account_number = self._pichincha_digits_only(partner_bank.acc_number)
            if not account_number:
                raise UserError(
                    _(
                        "La cuenta bancaria del beneficiario %(partner)s no "
                        "tiene número válido.",
                        partner=partner.display_name,
                    )
                )

            row = [
                file_tipo,
                self._pichincha_sanitize_text(
                    reference or payment.payment_reference or payment.ref or self.name
                ),
                file_currency,
                self._pichincha_amount_to_cents(payment.amount),
                cta_value,
                self._pichincha_sanitize_text(
                    self._pichincha_account_type(partner_bank, payment_mode)
                ),
                account_number,
                self._pichincha_sanitize_text(self.description or self.name),
                self._pichincha_sanitize_text(
                    self._pichincha_partner_identification_type(partner)
                ),
                ident_number,
                self._pichincha_sanitize_text(partner.name),
                bank_code,
            ]
            lines.append("\t".join(row))

        today = fields.Date.context_today(self)
        filename = "%s_pichincha_%s.txt" % (
            today.strftime("%Y-%m"),
            self.name or "payment_order",
        )
        return ("\n".join(lines).encode("utf-8"), filename)
