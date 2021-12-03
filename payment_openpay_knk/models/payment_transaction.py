# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).
import base64
import logging
import requests
import json

from odoo import api, fields, models
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.tools.float_utils import float_compare

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    openpay_authorization_code = fields.Char('Bank Authorization Code')
    openpay_card_type = fields.Selection([
        ('mastercard', 'MasterCard'), ('visa', 'Visa'),
        ('american_express', 'American Express'), ('carnet', 'Carnet')], string='Card Type')
    openpay_card_detail = fields.Char('Card Detail')

    openpay_store_barcode_url = fields.Char('Store Barcode URL')
    openpay_store_reference = fields.Char('Store Reference')
    openpay_store_receipt_filename = fields.Char(
        compute='compute_openpay_store_receipt_filename', string='Store Receipt Filename')
    openpay_store_receipt = fields.Binary('Store Receipt', attachment=True)
    openpay_store_receipt_download_url = fields.Char(
        'Store Receipt Download URL')

    openpay_bank = fields.Char('Bank')
    openpay_bank_name = fields.Char('Bank Name')
    openpay_bank_agreement = fields.Char('Bank Agreement')
    openpay_bank_clabe = fields.Char('Bank Clabe')
    openpay_bank_receipt_filename = fields.Char(
        compute='compute_openpay_bank_receipt_filename', string='Bank Receipt Filename')
    openpay_bank_receipt = fields.Binary('Bank Receipt', attachment=True)
    openpay_bank_receipt_download_url = fields.Char(
        'Bank Receipt Download URL')

    @api.depends('openpay_store_reference')
    def compute_openpay_store_receipt_filename(self):
        for rec in self:
            rec.openpay_store_receipt_filename = False
            if rec.openpay_store_reference:
                rec.openpay_store_receipt_filename = rec.openpay_store_reference + '.pdf'

    @api.depends('openpay_bank_name')
    def compute_openpay_bank_receipt_filename(self):
        for rec in self:
            rec.openpay_bank_receipt_filename = False
            if rec.openpay_bank_name:
                rec.openpay_bank_receipt_filename = rec.openpay_bank_name + '.pdf'

    @api.model
    def _openpay_card_form_get_tx_from_data(self, data):
        reference = data.get('order_id')
        if not reference:
            error_msg = 'Openpay(Card): received data with missing order reference (%s)' % (
                reference)
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        tx = self.env['payment.transaction'].search(
            [('reference', '=', reference)])
        if not tx or len(tx) > 1:
            error_msg = 'Openpay(Card): received data for reference %s' % (
                reference)
            if not tx:
                error_msg += ': no order found'
            else:
                error_msg += ': multiple order found'
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return tx

    @api.model
    def _openpay_store_form_get_tx_from_data(self, data):
        reference = data.get('order_id')
        if not reference:
            error_msg = 'Openpay(Store): received data with missing order reference (%s)' % (
                reference)
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        tx = self.env['payment.transaction'].search(
            [('reference', '=', reference)])
        if not tx or len(tx) > 1:
            error_msg = 'Openpay(Store): received data for reference %s' % (
                reference)
            if not tx:
                error_msg += ': no order found'
            else:
                error_msg += ': multiple order found'
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return tx

    @api.model
    def _openpay_bank_form_get_tx_from_data(self, data):
        reference = data.get('order_id')
        if not reference:
            error_msg = 'Openpay(Bank): received data with missing order reference (%s)' % (
                reference)
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        tx = self.env['payment.transaction'].search(
            [('reference', '=', reference)])
        if not tx or len(tx) > 1:
            error_msg = 'Openpay(Bank): received data for reference %s' % (
                reference)
            if not tx:
                error_msg += ': no order found'
            else:
                error_msg += ': multiple order found'
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return tx

    @api.model
    def _openpay_alipay_form_get_tx_from_data(self, data):
        reference = data.get('order_id')
        if not reference:
            error_msg = 'Openpay(Alipay): received data with missing order reference (%s)' % (
                reference)
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        tx = self.env['payment.transaction'].search(
            [('reference', '=', reference)])
        if not tx or len(tx) > 1:
            error_msg = 'Openpay(Alipay): received data for reference %s' % (
                reference)
            if not tx:
                error_msg += ': no order found'
            else:
                error_msg += ': multiple order found'
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return tx

    def _openpay_card_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        # Check Amount
        if float_compare(float(data.get('amount', '0.0')), (self.amount), 2) != 0:
            invalid_parameters.append(
                ('amount', data.get('amount'), '%.2f' % (self.amount)))
        # Check Currency
        if data.get('currency') != self.currency_id.name:
            invalid_parameters.append(
                ('currency', data.get('currency'), self.currency_id.name))
        return invalid_parameters

    def _openpay_store_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        # Check Amount
        if float_compare(float(data.get('amount', '0.0')), (self.amount), 2) != 0:
            invalid_parameters.append(
                ('amount', data.get('amount'), '%.2f' % (self.amount)))
        # Check Currency
        if data.get('currency') != self.currency_id.name:
            invalid_parameters.append(
                ('currency', data.get('currency'), self.currency_id.name))
        return invalid_parameters

    def _openpay_bank_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        # Check Amount
        if float_compare(float(data.get('amount', '0.0')), (self.amount), 2) != 0:
            invalid_parameters.append(
                ('amount', data.get('amount'), '%.2f' % (self.amount)))
        # Check Currency
        if data.get('currency') != self.currency_id.name:
            invalid_parameters.append(
                ('currency', data.get('currency'), self.currency_id.name))
        return invalid_parameters

    def _openpay_alipay_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        # Check Amount
        if float_compare(float(data.get('amount', '0.0')), (self.amount), 2) != 0:
            invalid_parameters.append(
                ('amount', data.get('amount'), '%.2f' % (self.amount)))
        # Check Currency
        if data.get('currency') != self.currency_id.name:
            invalid_parameters.append(
                ('currency', data.get('currency'), self.currency_id.name))
        return invalid_parameters

    def get_openpay_store_receipt(self, reference):
        acquirer = self.acquirer_id
        if acquirer.state == 'enabled':
            if acquirer.openpay_version == 'mxn':
                url = 'https://dashboard.openpay.mx/paynet-pdf/'
            else:
                url = 'https://dashboard.openpay.co/paynet-pdf/'
        else:
            if acquirer.openpay_version == 'mxn':
                url = 'https://sandbox-dashboard.openpay.mx/paynet-pdf/'
            else:
                url = 'https://sandbox-dashboard.openpay.co/paynet-pdf/'
        if acquirer.openpay_version == 'mxn':
            res = requests.get(url + '%s/%s' %
                               (acquirer.openpay_mxn_merchant_id, reference))
        else:
            res = requests.get(url + '%s/%s' %
                               (acquirer.openpay_mxn_merchant_id, reference))
        if res.status_code == 200:
            pdf_data = base64.b64encode(res.content)
            return pdf_data
        return False

    def get_openpay_bank_receipt(self, reference):
        acquirer = self.acquirer_id
        if acquirer.state == 'enabled':
            if acquirer.openpay_version == 'mxn':
                url = 'https://dashboard.openpay.mx/spei-pdf/'
            else:
                url = 'https://dashboard.openpay.co/spei-pdf/'
        else:
            if acquirer.openpay_version == 'mxn':
                url = 'https://sandbox-dashboard.openpay.mx/spei-pdf/'
            else:
                url = 'https://sandbox-dashboard.openpay.co/spei-pdf/'
        if acquirer.openpay_version == 'mxn':
            res = requests.get(url + '%s/%s' %
                               (acquirer.openpay_mxn_merchant_id, reference))
        else:
            res = requests.get(url + '%s/%s' %
                               (acquirer.openpay_mxn_merchant_id, reference))
        if res.status_code == 200:
            pdf_data = base64.b64encode(res.content)
            return pdf_data
        return False

    def _openpay_card_form_validate(self, data):
        status = data.get('status')
        vals = {
            'acquirer_reference': data.get('id'),
            'date': fields.Datetime.now(),
            'openpay_authorization_code': data.get('authorization') or False,
        }
        vals.update({
            'openpay_card_type': data.get('card').get('brand'),
            'openpay_card_detail': data.get('card').get('card_number')
        })
        self.write(vals)

        if status == 'completed':
            _logger.info(
                'Openpay(Card) payment for tx %s: set as DONE' % (self.reference))
            self._set_transaction_done()
        elif status in ('charge_pending', 'in_progress'):
            _logger.info(
                'Openpay(Card) payment for tx %s: set as PENDING' % (self.reference))
            self._set_transaction_pending()
        elif status == 'cancelled':
            _logger.info(
                'Openpay(Card) payment for tx %s: set as CANCELLED' % (self.reference))
            self._set_transaction_cancel()
        else:
            if data.get('error_message'):
                error = data.get('error_message')
            else:
                error = 'Received unrecognized response for Openpay(Card) Payment %s, set as error' % (
                    self.reference)
            _logger.info(error)
            self.write({
                'state_message': error
            })
            self._set_transaction_error(error)

    def _openpay_store_form_validate(self, data):
        status = data.get('status')
        vals = {
            'acquirer_reference': data.get('id'),
            'date': fields.Datetime.now(),
            'openpay_authorization_code': data.get('authorization') or False,
        }
        payment_method = json.loads(data.get('payment_method').replace("'", '"')) if not isinstance(
            data.get('payment_method'), dict) else data.get('payment_method')
        vals.update({
            'openpay_store_receipt_download_url': self.acquirer_id.get_receipt_download_url() + '/' + payment_method.get('reference'),
            'openpay_store_barcode_url': payment_method.get('barcode_url'),
            'openpay_store_reference': payment_method.get('reference'),
            'openpay_store_receipt': self.get_openpay_store_receipt(payment_method.get('reference'))
        })
        self.write(vals)

        if status == 'completed':
            _logger.info(
                'Openpay(Store) payment for tx %s: set as DONE' % (self.reference))
            self._set_transaction_done()
        elif status in ('charge_pending', 'in_progress'):
            _logger.info(
                'Openpay(Store) payment for tx %s: set as PENDING' % (self.reference))
            self._set_transaction_pending()
        elif status == 'cancelled':
            _logger.info(
                'Openpay(Store) payment for tx %s: set as CANCELLED' % (self.reference))
            self._set_transaction_cancel()
        else:
            if data.get('error_message'):
                error = data.get('error_message')
            else:
                error = 'Received unrecognized response for Openpay(Store) Payment %s, set as error' % (
                    self.reference)
            _logger.info(error)
            self.write({
                'state_message': error
            })
            self._set_transaction_error(error)

    def _openpay_bank_form_validate(self, data):
        status = data.get('status')
        vals = {
            'acquirer_reference': data.get('id'),
            'date': fields.Datetime.now(),
            'openpay_authorization_code': data.get('authorization') or False,
        }
        payment_method = json.loads(data.get('payment_method').replace("'", '"')) if not isinstance(
            data.get('payment_method'), dict) else data.get('payment_method')
        vals.update({
            'openpay_bank_receipt_download_url': self.acquirer_id.get_bank_receipt_download_url() + '/' + data.get('id'),
            'openpay_bank_agreement': payment_method.get('agreement'),
            'openpay_bank': payment_method.get('bank'),
            'openpay_bank_clabe': payment_method.get('clabe'),
            'openpay_bank_name': payment_method.get('name'),
            'openpay_bank_receipt': self.get_openpay_bank_receipt(data.get('id'))
        })
        self.write(vals)

        if status == 'completed':
            _logger.info('Openpay payment for tx %s: set as DONE' %
                         (self.reference))
            self._set_transaction_done()
        elif status in ('charge_pending', 'in_progress'):
            _logger.info('Openpay payment for tx %s: set as PENDING' %
                         (self.reference))
            self._set_transaction_pending()
        elif status == 'cancelled':
            _logger.info('Openpay payment for tx %s: set as CANCELLED' %
                         (self.reference))
            self._set_transaction_cancel()
        else:
            if data.get('error_message'):
                error = data.get('error_message')
            else:
                error = 'Received unrecognized response for Openpay Payment %s, set as error' % (
                    self.reference)
            _logger.info(error)
            self.write({
                'state_message': error
            })
            self._set_transaction_error(error)

    def _openpay_alipay_form_validate(self, data):
        status = data.get('status')
        vals = {
            'acquirer_reference': data.get('id'),
            'date': fields.Datetime.now(),
            'openpay_authorization_code': data.get('authorization') or False,
        }
        self.write(vals)

        if status == 'completed':
            _logger.info(
                'Openpay(Alipay) payment for tx %s: set as DONE' % (self.reference))
            self._set_transaction_done()
        elif status in ('charge_pending', 'in_progress'):
            _logger.info(
                'Openpay(Alipay) payment for tx %s: set as PENDING' % (self.reference))
            self._set_transaction_pending()
        elif status == 'cancelled':
            _logger.info(
                'Openpay(Alipay) payment for tx %s: set as CANCELLED' % (self.reference))
            self._set_transaction_cancel()
        else:
            if data.get('error_message'):
                error = data.get('error_message')
            else:
                error = 'Received unrecognized response for Openpay(Alipay) Payment %s, set as error' % (
                    self.reference)
            _logger.info(error)
            self.write({
                'state_message': error
            })
            self._set_transaction_error(error)

    def _cron_get_openpay_charge_status(self):
        self = self.search([
            ('acquirer_reference', '!=', False),
            ('state', 'in', ['pending', 'authorized']),
            ('provider', 'in', ['openpay_card', 'openpay_store', 'openpay_bank', 'openpay_alipay'])])
        for tx in self:
            if tx.acquirer_id.state == 'enabled':
                if tx.acquirer_id.openpay_version == 'mxn':
                    url = 'https://api.openpay.mx/v1/'
                else:
                    url = 'https://api.openpay.co/v1/'
            else:
                if tx.acquirer_id.openpay_version == 'mxn':
                    url = 'https://sandbox-api.openpay.mx/v1/'
                else:
                    url = 'https://sandbox-api.openpay.co/v1/'
            if tx.acquirer_id.openpay_version == 'mxn':
                res = requests.get(url + '%s/charges/%s' % (tx.acquirer_id.openpay_mxn_merchant_id,
                                                            tx.acquirer_reference), auth=(tx.acquirer_id.openpay_mxn_secret_key, ""))
            else:
                res = requests.get(url + '%s/charges/%s' % (tx.acquirer_id.openpay_cop_merchant_id,
                                                            tx.acquirer_reference), auth=(tx.acquirer_id.openpay_cop_secret_key, ""))
            response = res.json()
            tx.form_feedback(response, tx.acquirer_id.provider)
