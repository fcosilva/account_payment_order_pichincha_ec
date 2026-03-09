from odoo import models


class AccountPaymentLine(models.Model):
    _inherit = "account.payment.line"

    def _pichincha_pick_bank_account(self):
        self.ensure_one()
        candidate_partners = self.partner_id | self.partner_id.commercial_partner_id
        for partner in candidate_partners:
            bank_accounts = partner.bank_ids.filtered(lambda b: b.acc_number)
            if not bank_accounts:
                continue
            if "sequence" in bank_accounts._fields:
                bank_accounts = bank_accounts.sorted(key=lambda b: (b.sequence or 0, b.id))
            else:
                bank_accounts = bank_accounts.sorted("id")
            return bank_accounts[0]
        return False

    def draft2open_payment_line_check(self):
        self.ensure_one()
        if (
            not self.partner_bank_id
            and self.order_id.payment_method_id.code == "ec_pichincha_tab"
        ):
            partner_bank = self._pichincha_pick_bank_account()
            if partner_bank:
                self.partner_bank_id = partner_bank.id
        return super().draft2open_payment_line_check()
