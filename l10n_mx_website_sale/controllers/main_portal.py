# -*- coding: utf-8 -*-
# Copyright 2021 - QUADIT, SA DE CV(https://www.quadit.mx)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.addons.portal.controllers.portal import CustomerPortal as CP
from odoo.addons.website_sale.controllers.main import WebsiteSale as WS
from odoo import http, tools, _
from odoo.http import request
from werkzeug.exceptions import Forbidden
from odoo.exceptions import AccessError, MissingError, ValidationError
import json
import logging

_logger = logging.getLogger(__name__)

class CustomerPortal(CP):

    def __init__(self, **args):
        
        self.MANDATORY_BILLING_FIELDS.extend((
            'street_name',
            'street_number',))
        self.OPTIONAL_BILLING_FIELDS.extend((
            'street_number2',
            'l10n_mx_edi_colony',
        ))
        if 'street' in self.MANDATORY_BILLING_FIELDS:
            self.MANDATORY_BILLING_FIELDS.remove('street')
        super(CustomerPortal, self).__init__(**args)


class WebsiteSale(WS):

    def checkout_check_address(self, order):
        billing_fields_required = self._get_mandatory_fields_billing(order.partner_id.country_id.id)
        billing_fields_required.remove('lastname')
        billing_fields_required.remove('name')
        if not all(order.partner_id.read(billing_fields_required)[0].values()):
            return request.redirect('/shop/address?partner_id=%d' % order.partner_id.id)

        shipping_fields_required = self._get_mandatory_fields_shipping(order.partner_shipping_id.country_id.id)
        shipping_fields_required.remove('lastname')
        shipping_fields_required.remove('name')
        if not all(order.partner_shipping_id.read(shipping_fields_required)[0].values()):
            return request.redirect('/shop/address?partner_id=%d' % order.partner_shipping_id.id)

    def _get_mandatory_fields_billing(self, country_id=False):
        req = super(WebsiteSale, self)._get_mandatory_fields_billing()
        # req.extend(('street_number', 'lastname', 'zip', 'city_id'))
        req.extend(('firstname', 'street_name','street_number', 'lastname', 'zip',))
        return req

    def _get_mandatory_fields_shipping(self, country_id=False):
        req = super(WebsiteSale, self)._get_mandatory_fields_shipping()
        # req.extend(('email', 'lastname', 'zip', 'street_number', 'city_id'))
        req.extend(('email','firstname', 'lastname', 'zip', 'street_name','street_number',))
        return req

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        mode = (False, False)
        can_edit_vat = False
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))

        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            mode = ('new', 'billing')
            can_edit_vat = True
        # IF ORDER LINKED TO A PARTNER
        else:
            if partner_id > 0:
                if partner_id == order.partner_id.id:
                    mode = ('edit', 'billing')
                    can_edit_vat = order.partner_id.can_edit_vat()
                else:
                    shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                    if order.partner_id.commercial_partner_id.id == partner_id:
                        mode = ('new', 'shipping')
                        partner_id = -1
                    elif partner_id in shippings.mapped('id'):
                        mode = ('edit', 'shipping')
                    else:
                        return Forbidden()
                if mode and partner_id != -1:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                mode = ('new', 'shipping')
            else: # no mode - refresh without post?
                return request.redirect('/shop/checkout')

        # IF POSTED
        if 'submitted' in kw:
            pre_values = self.values_preprocess(order, mode, kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)

            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                partner_id = self._checkout_form_save(mode, post, kw)
                if mode[1] == 'billing':
                    order.partner_id = partner_id
                    order.with_context(not_self_saleperson=True).onchange_partner_id()
                    # This is the *only* thing that the front end user will see/edit anyway when choosing billing address
                    order.partner_invoice_id = partner_id
                    if not kw.get('use_same'):
                        kw['callback'] = kw.get('callback') or \
                            (not order.only_services and (mode[0] == 'edit' and '/shop/checkout' or '/shop/address'))
                elif mode[1] == 'shipping':
                    order.partner_shipping_id = partner_id

                # TDE FIXME: don't ever do this
                order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
                if not errors:
                    return request.redirect(kw.get('callback') or '/shop/confirm_order')

        render_values = {
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'can_edit_vat': can_edit_vat,
            'error': errors,
            'callback': kw.get('callback'),
            'only_services': order and order.only_services,
        }
        render_values.update(self._get_country_related_render_values(kw, render_values))
        return request.render("website_sale.address", render_values)

    def checkout_form_validate(self, mode, all_form_values, data):
        # mode: tuple ('new|edit', 'billing|shipping')
        # all_form_values: all values before preprocess
        # data: values after preprocess
        error = dict()
        error_message = []
        

        # Required fields from form
        required_fields = [f for f in (all_form_values.get('field_required') or '').split(',') if f]
        # Required fields from mandatory field function
        country_id = int(data.get('country_id', False))
        required_fields += mode[1] == 'shipping' and self._get_mandatory_fields_shipping(country_id) or self._get_mandatory_fields_billing(country_id)
        if all_form_values.get('city_id', 'Unknown') != 'Unknown':
            required_fields.remove('city')
        else:
            all_form_values["city_id"] = False
        # error messagfor empty required fields
       
        required_fields.remove('name')
        required_fields.remove('street')

        for field_name in required_fields:
            if not data.get(field_name):
                error[field_name] = 'missing'
        # email validation
        if data.get('email') and not tools.single_email_re.match(data.get('email')):
            error["email"] = 'error'
            error_message.append(_('Invalid Email! Please enter a valid email address.'))

        # vat validation
        Partner = request.env['res.partner']
        if data.get("vat") and hasattr(Partner, "check_vat"):
            if country_id:
                data["vat"] = Partner.fix_eu_vat_number(country_id, data.get("vat"))
            partner_dummy = Partner.new(self._get_vat_validation_fields(data))
            try:
                partner_dummy.check_vat()
            except ValidationError as exception:
                error["vat"] = 'error'
                error_message.append(exception.args[0])

        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))

        return error, error_message

class WebsiteSaleCity(WS):
    
    def values_postprocess(self, order, mode, values, errors, error_msg):
        new_values, errors, error_msg = super(WebsiteSaleCity, self).values_postprocess(
            order, mode, values, errors, error_msg
        )
        new_values["city_id"] = values.get("city_id")
        new_values["firstname"] = values.get("firstname")
        new_values["lastname"] = values.get("lastname")
        new_values["lastname2"] = values.get("lastname2")
        new_values["references"] = values.get("references")
        if new_values["city_id"]:
            city = request.env["res.city"].browse(int(values.get("city_id")))
            if city:
                new_values["city"] = city.name
        return new_values, errors, error_msg

    def checkout_form_validate(self, mode, all_form_values, data):
        error, error_message = super(WebsiteSaleCity, self).checkout_form_validate(mode, all_form_values, data)

        # Check if city_id required
        country = request.env["res.country"]
        if data.get("country_id"):
            country = country.browse(int(data.get("country_id")))
            if country.enforce_cities:
                if error.get("city") == "missing" and error.get("city_id") == "missing":
                    del error["city_id"]

        return error, error_message

class WebsiteSaleNewFields(WS): 

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        result = super(WebsiteSaleNewFields, self).address(**kw)


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

        result.qcontext['firstname']=request.website.sale_get_order().partner_id.firstname
        if kw.get('firstname') and kw.get('firstname') != '':
            request.website.sale_get_order().partner_id.firstname = kw.get('firstname')
        
        result.qcontext['lastname']=request.website.sale_get_order().partner_id.lastname
        if kw.get('lastname') and kw.get('lastname') != '':
            request.website.sale_get_order().partner_id.lastname = kw.get('lastname')
        
        result.qcontext['lastname2']=request.website.sale_get_order().partner_id.lastname2
        if kw.get('lastname2') and kw.get('lastname2') != '':
            request.website.sale_get_order().partner_id.lastname2 = kw.get('lastname2')

        return result


    def _get_mandatory_fields_billing(self, country_id=False):
        req = super(WebsiteSaleNewFields, self)._get_mandatory_fields_billing()
        return req

#class change_route_cart_Website(Website):
#    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True)
#    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
#        """This route is called when adding a product to cart (no options)."""
#        sale_order = request.website.sale_get_order(force_create=True)
#        if sale_order.state != 'draft':
#            request.session['sale_order_id'] = None
#            sale_order = request.website.sale_get_order(force_create=True)

#        product_custom_attribute_values = None
#        if kw.get('product_custom_attribute_values'):
#            product_custom_attribute_values = json.loads(kw.get('product_custom_attribute_values'))

#        no_variant_attribute_values = None
#        if kw.get('no_variant_attribute_values'):
#            no_variant_attribute_values = json.loads(kw.get('no_variant_attribute_values'))

#        sale_order._cart_update(
#            product_id=int(product_id),
#            add_qty=add_qty,
#            set_qty=set_qty,
#            product_custom_attribute_values=product_custom_attribute_values,
#            no_variant_attribute_values=no_variant_attribute_values
#        )

#        if kw.get('express'):
#            return request.redirect("/shop/checkout?express=1")
#        if request.httprequest.headers and request.httprequest.headers.get('Referer'):
#            return request.redirect(str(request.httprequest.headers.get('Referer')))
#        return request.redirect("/shop/")