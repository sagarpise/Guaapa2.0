# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

import logging
import pprint
import requests
import werkzeug

from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class OpenpayController(http.Controller):
    _return_card_url = '/payment/openpay/card/return'
    _return_alipay_url = '/payment/openpay/alipay/return'
    _webhook_store_url = '/payment/openpay/store/webhook'
    _webhook_bank_url = '/payment/openpay/bank/webhook'

    def get_openpay_tx_data(self, tx_id, cus_id, provider):
        acquirer = request.env['payment.acquirer'].sudo().search([('provider', '=', provider)], limit=1)
        if acquirer.state == 'enabled':
            if acquirer.openpay_version == 'mxn':
                url = 'https://api.openpay.mx/v1/%s/charges/%s' % (acquirer.openpay_mxn_merchant_id, tx_id)
            else:
                url = 'https://api.openpay.co/v1/%s/charges/%s' % (acquirer.openpay_cop_merchant_id, tx_id)
        else:
            if acquirer.openpay_version == 'mxn':
                url = 'https://sandbox-api.openpay.mx/v1/%s/charges/%s' % (acquirer.openpay_mxn_merchant_id, tx_id)
            else:
                url = 'https://sandbox-api.openpay.co/v1/%s/charges/%s' % (acquirer.openpay_cop_merchant_id, tx_id)
        res = requests.get(url, auth=(acquirer.openpay_mxn_secret_key if acquirer.openpay_version == 'mxn' else acquirer.openpay_cop_secret_key, ""))
        return res.json()

    @http.route(_return_card_url, type='http', auth='public', csrf=False, save_session=False)
    def openpay_card_form_feedback(self, **post):
        _logger.info('Openpay(Card): got the transaction redirect response as %s', pprint.pformat(post))
        response = self.get_openpay_tx_data(post.get('id'), post.get('cus_id'), 'openpay_card')
        _logger.info('Openpay(Card): entering form_feedback with post data %s', pprint.pformat(response))
        request.env['payment.transaction'].sudo()._handle_feedback_data('openpay_card',POST)
        return ''

    @http.route(_return_alipay_url, type='http', auth='public', csrf=False, save_session=False)
    def openpay_alipay_form_feedback(self, **post):
        _logger.info('Openpay(Alipay): got the transaction redirect response as %s', pprint.pformat(post))
        response = self.get_openpay_tx_data(post.get('id'), post.get('cus_id'), 'openpay_alipay')
        _logger.info('Openpay(Alipay): entering form_feedback with post data %s', pprint.pformat(response))
        request.env['payment.transaction'].sudo().form_feedback(response, 'openpay_alipay')
        return werkzeug.utils.redirect('/payment/process')

    @http.route('/openpay/charge/redirect', type='http', auth='public', csrf=False)
    def openpay_charge_redirect(self, **post):
        url = post.get('url')
        return werkzeug.utils.redirect(url)

    @http.route('/openpay/store/redirect', type='http', auth='public', csrf=False)
    def openpay_store_redirect(self, **post):
        _logger.info('Openpay(Store): entering form_feedback with store data %s', pprint.pformat(post))
        request.env['payment.transaction'].sudo().form_feedback(post, 'openpay_store')
        return werkzeug.utils.redirect('/shop/confirmation')

    @http.route(_webhook_store_url, type='json', auth='public', csrf=False)
    def openpay_webhook_store_feedback(self, **post):
        _logger.info('Openpay(Store): got the transaction webhook response as %s', pprint.pformat(request.jsonrequest))
        if request.jsonrequest.get("transaction"):
            return request.env['payment.transaction'].sudo().form_feedback(request.jsonrequest.get('transaction'), 'openpay_store')
        return Response(status=200)

    @http.route('/openpay/bank/redirect', type='http', auth='public', csrf=False)
    def openpay_bank_redirect(self, **post):
        _logger.info('Openpay(Bank): entering form_feedback with bank data %s', pprint.pformat(post))
        request.env['payment.transaction'].sudo().form_feedback(post, 'openpay_bank')
        return werkzeug.utils.redirect('/shop/confirmation')

    @http.route(_webhook_bank_url, type='json', auth='public', csrf=False)
    def openpay_webhook_bank_feedback(self, **post):
        _logger.info('Openpay(Bank): got the transaction webhook response as %s', pprint.pformat(request.jsonrequest))
        if request.jsonrequest.get("transaction"):
            return request.env['payment.transaction'].sudo().form_feedback(request.jsonrequest.get('transaction'), 'openpay_bank')
        return Response(status=200)
