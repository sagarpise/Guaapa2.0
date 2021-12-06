# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

import json
import requests
import uuid
from werkzeug import urls

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.payment_openpay_knk.controllers.main import OpenpayController

class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['openpay_card'] = {'mode': 'unique', 'domain': [('type', '=', 'bank')]}
        return res

class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    @api.model
    def _get_providers(self):
        providers = super(PaymentAcquirer, self)._get_providers()
        providers.append([
            'openpay_card', 'Openpay(Card)',
            'openpay_store', 'Openpay(Store)',
            'openpay_bank', 'Openpay(Bank)',
            'openpay_alipay', 'Openpay(Alipay)'
        ])
        return providers

    provider = fields.Selection(selection_add=[
        ('openpay_card', 'Openpay(Card)'), ('openpay_store', 'Openpay(Store)'),
        ('openpay_bank', 'Openpay(Bank)'), ('openpay_alipay', 'Openpay(Alipay)')],
        ondelete={'openpay_card': 'set default', 'openpay_store': 'set default', 'openpay_bank': 'set default', 'openpay_alipay': 'set default'})
    openpay_version = fields.Selection([('mxn', 'México'), ('cop', 'Colombia')], 'Version', default='mxn', required_if_provider='openpay')
    openpay_mxn_merchant_id = fields.Char(required_if_provider='openpay')
    openpay_mxn_secret_key = fields.Char(required_if_provider='openpay')
    openpay_mxn_public_key = fields.Char(required_if_provider='openpay')
    openpay_cop_merchant_id = fields.Char(required_if_provider='openpay')
    openpay_cop_secret_key = fields.Char(required_if_provider='openpay')
    openpay_cop_public_key = fields.Char(required_if_provider='openpay')
    openpay_webhook_username = fields.Char('Webhook Username', copy=False)
    openpay_webhook_password = fields.Char('Webhook Password', copy=False)
    openpay_webhook_id = fields.Char('Webhook ID', copy=False, readonly=True, store=True)

    def _get_feature_support(self):
        res = super(PaymentAcquirer, self)._get_feature_support()
        res['fees'].append('openpay_card')
        res['fees'].append('openpay_store')
        res['fees'].append('openpay_bank')
        res['fees'].append('openpay_alipay')
        return res

    def openpay_card_compute_fees(self, amount, currency_id, country_id):
        if not self.fees_active:
            return 0.0
        country = self.env['res.country'].browse(country_id)
        if country and self.company_id.country_id.id == country.id:
            percentage = self.fees_dom_var
            fixed = self.fees_dom_fixed
        else:
            percentage = self.fees_int_var
            fixed = self.fees_int_fixed
        fees = (percentage / 100.0 * amount + fixed) / (1 - percentage / 100.0)
        return fees

    def openpay_store_compute_fees(self, amount, currency_id, country_id):
        if not self.fees_active:
            return 0.0
        country = self.env['res.country'].browse(country_id)
        if country and self.company_id.country_id.id == country.id:
            percentage = self.fees_dom_var
            fixed = self.fees_dom_fixed
        else:
            percentage = self.fees_int_var
            fixed = self.fees_int_fixed
        fees = (percentage / 100.0 * amount + fixed) / (1 - percentage / 100.0)
        return fees

    def openpay_bank_compute_fees(self, amount, currency_id, country_id):
        if not self.fees_active:
            return 0.0
        country = self.env['res.country'].browse(country_id)
        if country and self.company_id.country_id.id == country.id:
            percentage = self.fees_dom_var
            fixed = self.fees_dom_fixed
        else:
            percentage = self.fees_int_var
            fixed = self.fees_int_fixed
        fees = (percentage / 100.0 * amount + fixed) / (1 - percentage / 100.0)
        return fees

    def openpay_alipay_compute_fees(self, amount, currency_id, country_id):
        if not self.fees_active:
            return 0.0
        country = self.env['res.country'].browse(country_id)
        if country and self.company_id.country_id.id == country.id:
            percentage = self.fees_dom_var
            fixed = self.fees_dom_fixed
        else:
            percentage = self.fees_int_var
            fixed = self.fees_int_fixed
        fees = (percentage / 100.0 * amount + fixed) / (1 - percentage / 100.0)
        return fees

    def create_openpay_charge(self, method, values):
        base_url = self.get_base_url()
        if self.state == 'enabled':
            if self.openpay_version == 'mxn':
                url = 'https://api.openpay.mx/v1/'
            else:
                url = 'https://api.openpay.co/v1/'
        else:
            if self.openpay_version == 'mxn':
                url = 'https://sandbox-api.openpay.mx/v1/'
            else:
                url = 'https://sandbox-api.openpay.co/v1/'
        headers = {
            'content-type': 'application/json'
        }
        partner = self.env['res.partner'].search([('id','=',values['partner_id'])])
        if not partner.state_id.name :
            raise UserError("State field is missing in address !")
        if self.provider == 'openpay_alipay':
            return_url = urls.url_join(base_url, OpenpayController._return_alipay_url)
        else:
            return_url = urls.url_join(base_url, OpenpayController._return_card_url)
        currency = self.env['res.currency'].search([('id','=',values['currency_id'])])
        data = {
            "method": method,
            "amount": '%.2f' % values['amount'],
            "description": values['reference'],
            "order_id": values['reference'],
            "currency": currency or '',
            "customer": {
                "name": partner.firstname or '',
                "last_name": partner.lastname or '',
                "email": partner.email,
                "phone_number": partner.phone,
                "address": {
                    "city": partner.city,
                    "state": partner.state_id.name if partner.state_id else '',
                    "line1": partner.street,
                    "postal_code": partner.zip,
                    "country_code": partner.country_id.code  or ''
                }
            },
            "send_email": False,
            "confirm": False,
            "redirect_url": return_url
        }
        if self.openpay_version == 'mxn':
            res = requests.post(url + '%s/charges' % self.openpay_mxn_merchant_id, headers=headers, data=json.dumps(data), auth=(self.openpay_mxn_secret_key, ""))
        else:
            res = requests.post(url + '%s/charges' % self.openpay_cop_merchant_id, headers=headers, data=json.dumps(data), auth=(self.openpay_cop_secret_key, ""))
        response = res.json()
        return response

    def create_openpay_webhook(self, values):
        base_url = self.get_base_url()
        if self.state == 'enabled':
            if self.openpay_version == 'mxn':
                url = 'https://api.openpay.mx/v1/'
            else:
                url = 'https://api.openpay.co/v1/'
        else:
            if self.openpay_version == 'mxn':
                url = 'https://sandbox-api.openpay.mx/v1/'
            else:
                url = 'https://sandbox-api.openpay.co/v1/'
        headers = {
            'content-type': 'application/json'
        }
        if not values.get('partner_state'):
            raise UserError("State field is missing in address !")
        if self.provider == 'openpay_store':
            webhook_url = urls.url_join(base_url, OpenpayController._webhook_store_url)
        else:
            webhook_url = urls.url_join(base_url, OpenpayController._webhook_bank_url)
        data = {
            "url": webhook_url,
            "user": uuid.uuid4().hex,
            "password": uuid.uuid4().hex,
            "event_types": [
                "charge.succeeded"
            ]
        }
        self.openpay_webhook_username = data.get('user')
        self.openpay_webhook_password = data.get('password')
        if self.openpay_version == 'mxn':
            res = requests.post(url + '%s/webhooks' % self.openpay_mxn_merchant_id, headers=headers, data=json.dumps(data), auth=(self.openpay_mxn_secret_key, ""))
        else:
            res = requests.post(url + '%s/webhooks' % self.openpay_cop_merchant_id, headers=headers, data=json.dumps(data), auth=(self.openpay_cop_secret_key, ""))
        response = res.json()
        return response

    def openpay_card_form_generate_values(self, values):
        charge = self.create_openpay_charge('card', values)
        if charge.get('error_code'):
            raise UserError(_("%s" % charge.get('description')))
        form_url = charge.get('payment_method').get('url')
        values.update({'form_url': '/openpay/charge/redirect?url=' + form_url})
        return values

    def openpay_store_form_generate_values(self, values):
        charge = self.create_openpay_charge('store', values)
        if not self.openpay_webhook_id:
            webhook = self.create_openpay_webhook(values)
            if webhook.get('error_code'):
                raise UserError(_("%s" % webhook.get('description')))
            self.openpay_webhook_id = webhook.get('id')
        if charge.get('error_code'):
            raise UserError(_(charge.get('description')))
        form_url = "/openpay/store/redirect?%s" % (urls.url_encode(charge))
        values.update({'form_url': form_url})
        return values

    def openpay_bank_form_generate_values(self, values):
        charge = self.create_openpay_charge('bank_account', values)
        if not self.openpay_webhook_id:
            webhook = self.create_openpay_webhook(values)
            if webhook.get('error_code'):
                raise UserError(_("%s" % webhook.get('description')))
            self.openpay_webhook_id = webhook.get('id')
        if charge.get('error_code'):
            raise UserError(_(charge.get('description')))
        form_url = "/openpay/bank/redirect?%s" % (urls.url_encode(charge))
        values.update({'form_url': form_url})
        return values

    def openpay_alipay_form_generate_values(self, values):
        charge = self.create_openpay_charge('alipay', values)
        if charge.get('error_code'):
            raise UserError(_("%s" % charge.get('description')))
        form_url = charge.get('payment_method').get('url')
        values.update({'form_url': '/openpay/charge/redirect?url=' + form_url})
        return values

    def get_receipt_download_url(self):
        if self.state == 'enabled':
            if self.openpay_version == 'mxn':
                return 'https://dashboard.openpay.mx/paynet-pdf/%s' % self.openpay_mxn_merchant_id
            else:
                return 'https://dashboard.openpay.cop/paynet-pdf/%s' % self.openpay_cop_merchant_id
        else:
            if self.openpay_version == 'mxn':
                return 'https://sandbox-dashboard.openpay.mx/paynet-pdf/%s' % self.openpay_mxn_merchant_id
            else:
                return 'https://sandbox-dashboard.openpay.cop/paynet-pdf/%s' % self.openpay_cop_merchant_id

    def get_bank_receipt_download_url(self):
        if self.state == 'enabled':
            if self.openpay_version == 'mxn':
                return 'https://dashboard.openpay.mx/spei-pdf/%s' % self.openpay_mxn_merchant_id
            else:
                return 'https://dashboard.openpay.cop/spei-pdf/%s' % self.openpay_cop_merchant_id
        else:
            if self.openpay_version == 'mxn':
                return 'https://sandbox-dashboard.openpay.mx/spei-pdf/%s' % self.openpay_mxn_merchant_id
            else:
                return 'https://sandbox-dashboard.openpay.cop/spei-pdf/%s' % self.openpay_cop_merchant_id
