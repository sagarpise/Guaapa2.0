# Copyright 2021 - QUADIT, SA DE CV(https://www.quadit.mx)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Guaapa Gateway',
    'summary': 'Guaapa gateway integration',
    'description': 'Guaapa gateway integration with custom delivery',
    'version': '14.0.0.0.1',
    'category': 'Hidden',
    'author': 'QUADIT, SA DE CV, REDBX, SA DE CV ',
    'website': 'https://www.quadit.mx',
    'license': 'LGPL-3',
    'depends': ['base', 'account', 'stock'],
    'sequence': 999,
    'demo': [],
    'data': [
            'security/ir.model.access.csv',
            'views/views.xml',
            ],
    'development_status': 'Beta',
    'maintainers': [
        '@gerardomr8',
        '@kuro088'

    ],
    'installable': True,
}
