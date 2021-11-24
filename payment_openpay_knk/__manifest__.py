# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).
{
    'name': 'Openpay Payment Gateway',
    'summary': '''
        Openpay Payment Gateway | Openpay Payment Acquirer | Openpay Payment | Online Payment
        Alipay | Alipay QR | QR code payment | QR payment | Visa Card | Master Card | American Express Card | Carnet Card
        Benamex | Santander | HSBC | Scotiabank | Inbursa | IXE | BBVA
        Store Payment | Store Cash Payment | Cahs payment via store | Paynet | Farmacias Benavides | 7-Eleven
        Walmart | Walmart Express | Farmacias del Ahorro | Sam's Club | Bodega Aurrerá | Circle K
        Asturiano | Waldo's | Extra Contigo día y noche | Kiosko | Super Farmacia | Gest Pago | A Tiendas
        Multi Recargas | Pago Rapido | Todopago Express | Energía de Pereira | MASRED S.A.S | Ser Comunicacione
        Comtel | Don Pago | icell | Elid Tel | Smartket | Cootraecor Ltda | Confemovil | Girosya | Pago Facil | One Easy Step | Coocentral | Inter Rapidísimo | 6 Baloto, Baloto6
        Bank Payment | Bank Transfer | Wire Transfer | ABC Capital | AFIRME | Banco Azteca | Ban Bajio | Citibanamex
        Banco Base | Volkswagen Bank | Ban Coppel | Banjercito | Banorte | Banregio | Bansi | CI Banco | Inbursa | MUFG
        BX+ | Invex | J.P. Morgan | J P Morgan | Multiva | Mifel | Monex
        Mexican Pesos (MXN) | Colombian Peso (COP) | United States Dollar (USD)
    ''',
    'description': """Openpay Payment Gateway""",
    'category': 'Accounting/Payment',
    'version': '1.0',
    'author': 'Kanak Infosystems LLP.',
    'website': 'https://www.kanakinfosystems.com',
    'license': 'OPL-1',
    'depends': ['payment', 'website_sale'],
    'data': [
        'views/assets.xml',
        'views/payment_views.xml',
        'views/payment_templates.xml',
        'data/payment_icons_data.xml',
        'data/payment_acquirer_data.xml',
        'data/cron_data.xml',
        'views/payment_portal_templates.xml'
    ],
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'currency': 'EUR',
    'price': 129,
    'uninstall_hook': 'uninstall_hook',
}
