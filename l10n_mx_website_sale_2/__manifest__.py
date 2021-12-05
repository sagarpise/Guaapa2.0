# -*- coding: utf-8 -*-
{
    'name': "Ecommerce for Mexico,Update",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['l10n_mx_website_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/checkout_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            "/l10n_mx_website_sale_2/static/src/js/validate.js",
        ]
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
