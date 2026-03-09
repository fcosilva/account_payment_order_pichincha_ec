from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _prepare_payment_line_vals(self, payment_order):
        vals = super()._prepare_payment_line_vals(payment_order)
        if self.move_id.is_invoice():
            move = self.move_id
            vals["communication"] = (
                move.l10n_latam_document_number
                or move.name
                or move.ref
                or move.payment_reference
                or vals.get("communication")
            )
        return vals
