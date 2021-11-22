# Copyright 2021 - QUADIT, SA DE CV(https://www.quadit.mx)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'guaapa_create_delivery',
    'summary': 'Guaapa Create Delivery',
    'description': 'Guaapa Create Delivery',
    'version': '14.0.0.0.1',
    'category': 'Hidden',
    'author': 'QUADIT, SA DE CV, REDBX, SA DE CV ',
    'website': 'https://www.quadit.mx',
    'license': 'LGPL-3',
    'depends': [
                'base',
                'guaapa', 
                'product', 
                'sale_management', 
                'stock', 
                'website', 
                'website_sale', 
                'delivery', 
                'website_sale_stock', 
                'website_sale_delivery'
                ],
    'sequence': 999,
    'demo': [],
    'data': [
            'security/ir.model.access.csv',
            'views/views.xml',
            'views/view_zip_list.xml',            
            'views/views_delivery_carrier.xml',
            'data/automatic_actions.xml',
            ],
    'development_status': 'Beta',
    'maintainers': [
        '@gerardomr8',
        '@kuro088'
    ],
    'installable': True,
}
