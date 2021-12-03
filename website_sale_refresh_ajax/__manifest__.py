# -*- coding: utf-8 -*-
# Copyright 2021 - QUADIT, SA DE CV(https://www.quadit.mx)
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Website sale refresh with ajax',
    'summary': 'Add refresh action on my cart icon when press button back on browser',
    'version': '15.0.0.0.1',
    'category': 'ecommerce',
    'author': 'QUADIT, SA DE CV ',
    'website': 'https://www.quadit.mx',
    'license': 'LGPL-3',
    'depends': ['website'],
    'data': [
             ],
    'demo': [],
    "assets": { 
        'web.assets_frontend' : [ 
            "/website_sale_refresh_ajax/static/src/js/navbar.js",
        ],
    },
    'development_status': 'alpha',
    'maintainers': [
        'luisangel-g',
        'gerardomr8',
    ],
    'installable': True,
}
