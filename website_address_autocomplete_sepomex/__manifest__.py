# -*- coding: utf-8 -*-
# Copyright 2021 - QUADIT, SA DE CV(https://www.quadit.mx)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Add Zipcode for México in Website Sale",
    "summary": "",
    "version": "15.0.0.0.1",
    "category": "Localization/Mexico",
    'author': 'QUADIT, SA DE CV',
    "website": "https://www.quadit.mx",
    "license": "LGPL-3",
    "depends": ['website_sale', 
    ],
    "data": [
        'views/templates.xml',
        'views/my_details.xml',
        'views/checkout_total.xml',
        'views/shop_address.xml',
    ],
    "assets": { 
        'web.assets_frontend' : [ 
            "/website_address_autocomplete_sepomex/static/src/js/form.js", 
            "/website_address_autocomplete_sepomex/static/src/js/portal_shop.js",
            "/website_address_autocomplete_sepomex/static/src/css/style.css",
            "/website_address_autocomplete_sepomex/static/src/js/validate.js",
        ],
    },
    'maintainers': [
        'luisangel-g',
        'gerardomr8',
    ],
    "installable": True
}
