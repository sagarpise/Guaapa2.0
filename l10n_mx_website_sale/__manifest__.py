# -*- coding: utf-8 -*-
# Copyright 2021 - QUADIT, SA DE CV(https://www.quadit.mx)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Ecommerce for Mexico",
    "summary": """
        Adds the fields related to the Mexico localisation to all
        frontend forms that are related to a partner creation/modification
    """,
    "version": "14.0.1.0.0",
    'author': 'QUADIT, SA DE CV, REDBX, SA DE CV ',
    "category": "Localization/Mexico",
    "website": "https://www.quadit.mx",
    "license": "LGPL-3",
    "depends": [
        'l10n_mx_edi',
        'website_sale',
    ],
    "demo": [
    ],
    "data": [
        'data/form_fields.xml',
        'views/base_config_view.xml',
        'views/res_partner.xml',
        'views/res_user.xml',
        'views/my_details.xml',
        'views/checkout_total.xml',
        'views/shop_address.xml',
        'views/checkout_templates.xml',
        #"views/assets.xml",
    ],
    'assets': {
        'web.assets_frontend': [
            "/l10n_mx_website_sale/static/src/js/form.js", 
            "/l10n_mx_website_sale/static/src/js/portal_shop.js",
            "/l10n_mx_website_sale/static/src/css/style.css",
            "/l10n_mx_website_sale/static/src/js/validate.js",
            #'l10n_mx_website_sale/static/src/js/portal.js',
            'l10n_mx_website_sale/static/src/js/website_profile_extended.js',
        ],
    },
    "installable": True,
    "auto_install": False,
}
