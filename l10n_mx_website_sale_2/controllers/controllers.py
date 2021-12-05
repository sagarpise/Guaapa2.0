# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
import werkzeug
import logging

_logger = logging.getLogger(__name__)
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSalePayment(WebsiteSale):

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        result = super(WebsiteSalePayment, self).address(**kw)


        result.qcontext['references'] = request.website.sale_get_order().partner_id.references

        if kw.get('references') and kw.get('references') != '':
            result.qcontext['references'] = kw.get('references')
            request.website.sale_get_order().partner_id.references = kw.get('references')


        result.qcontext['invoice_data'] = request.website.sale_get_order().partner_id.invoice_data
        if kw.get('invoice_data') and kw.get('invoice_data') != '':
            result.qcontext['invoice_data'] = kw.get('invoice_data')
            request.website.sale_get_order().partner_id.invoice_data = True


        result.qcontext['vat'] = request.website.sale_get_order().partner_id.vat
        if kw.get('vat') and kw.get('vat') != '':
            request.website.sale_get_order().partner_id.vat = kw.get('vat')


        result.qcontext['company_name'] = request.website.sale_get_order().partner_id.company_name
        if kw.get('company_name') and kw.get('company_name') != '':
            request.website.sale_get_order().partner_id.company_name = kw.get('company_name')

        return result

    # def checkout_check_address(self, order):
    #     result = super(WebsiteSalePayment, self).checkout_check_address(order)
    #     a=1

    def _get_mandatory_fields_billing(self, country_id=False):
        req = super(WebsiteSalePayment, self)._get_mandatory_fields_billing()
        req.extend(('references',))
        return req