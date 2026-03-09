{
    "name": "Account Payment Order - Pichincha EC Export",
    "version": "17.0.1.0.0",
    "summary": "Export payment order file for Banco Pichincha Ecuador",
    "license": "AGPL-3",
    "author": "OpenLab Ecuador",
    "category": "Banking addons",
    "depends": [
        "account_payment_order",
        "l10n_ec_bank_code_compat",
    ],
    "data": [
        "data/account_payment_method_data.xml",
        "views/account_payment_mode_views.xml",
        "views/res_partner_bank_views.xml",
    ],
    "installable": True,
    "application": False,
}
