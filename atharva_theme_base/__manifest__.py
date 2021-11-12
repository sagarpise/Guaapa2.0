# -*- coding: utf-8 -*-
{
    'name': 'Atharva Theme Base',
    'category': 'Base',
    'summary': 'Base module for Atharva E-commerce themes',
    'version': '1.1',
    'license': 'OPL-1',
    'author': 'Atharva System',
	'support': 'support@atharvasystem.com',
    'website' : 'https://www.atharvasystem.com',
	'description': """Base module for Atharva E-commerce themes""",
    'depends': [
        'website_sale',
        'website_sale_wishlist',
        'website_sale_comparison',
        'website_blog'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/admin/faqs_views.xml',
        'views/admin/product_label.xml',
        'views/admin/product_tags.xml',
        'views/admin/product_brand.xml',
        'views/admin/product_tab.xml',
        'views/admin/menu_tag.xml',
        'views/admin/pwa.xml',
        'views/megamenus/templates.xml',
        'views/shop/product_page.xml',
        'views/shop/shop_page.xml',
        'views/shop/shop_brand.xml',
        'views/shop/shop_filter.xml',
        'views/shop/quick_view.xml',
        'views/pwa/template.xml',
        'views/header_footer/footer.xml',
        'views/header_footer/header.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'atharva_theme_base/static/src/lib/swiper-bundle.min.css',
            'atharva_theme_base/static/src/lib/swiper-bundle.min.js',
            'atharva_theme_base/static/src/lib/jquery.magnific-popup.min.js',
            'atharva_theme_base/static/src/lib/magnific-popup.css',
            'atharva_theme_base/static/src/js/pwa_config.js'
        ],
    },
    'price': 4.00,
    'currency': 'EUR',
    'images': ['static/description/as-theme-base.png'],
    'installable': True,
    'application': True
}