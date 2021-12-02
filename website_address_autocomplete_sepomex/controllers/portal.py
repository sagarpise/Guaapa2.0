# -*- coding: utf-8 -*-
# Copyright 2021 - QUADIT, SA DE CV(https://www.quadit.mx)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import http
from odoo.http import request
from odoo.http import content_disposition, Controller, request, route
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)

class CustomerPortalCity(CustomerPortal):
    MANDATORY_BILLING_FIELDS = ["name", "phone", "email", "street", "city", "country_id"]
    OPTIONAL_BILLING_FIELDS = ["zip", "state_id", "vat", "company_name", "city_id", "changeInputs"]

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortalCity, self)._prepare_portal_layout_values()
        # cities = request.env['res.city'].sudo().search([])
        # values['cities'] = cities
        values["city_id"] = request.env.user.partner_id.city_id.id
        return values

    @http.route(
        ['/shop/state_infos/<model("res.country.state"):state>'],
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def country_infos(self, state, mode, **kw):
        
        return dict(
            cities=[(st.id, st.name, st.zipcode or "") for st in state.get_website_sale_cities(mode=mode)],
        )
    
    @route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()    
        partner = request.env.user.partner_id
        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            post.update({'country_id': 156})
            if post['state_id']:
                post.update({'state_id': int(post['state_id'])})
            else:
                post.update({'state_id': int(post['state_id'])})
            #post.update({'city_id': int(post['city_id'])})
            print(post)
            error, error_message = self.details_form_validate(post)

            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            
            if not error:
                values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
                
                values.update({key: post[key] for key in self.OPTIONAL_BILLING_FIELDS if key in post})
                for field in set(['country_id', 'state_id']) & set(values.keys()):
                    try:
                        values[field] = int(values[field])
                    except:
                        values[field] = False
                values.update({'zip': values.pop('zip', '')})

                partner.sudo().write(post)
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/home')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

        values.update({
            'partner': partner,
            'countries': countries,
            'states': states,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
            'page_name': 'my_details',
        })

        response = request.render("portal.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response


class CustomerWebsite(WebsiteSale):
    
    @http.route(['/shop/country_infos/<model("res.country"):country>'], type='json', auth="public", methods=['POST'], website=True)
    def country_infos(self, country, mode, **kw):
        dic = dict(
            fields=country.get_address_fields(),
            states=[(485, 'Aguascalientes', 'AGU'), (486, 'Baja California', 'BCN'), (487, 'Baja California Sur', 'BCS'), (490, 'Campeche', 'CAM'), (488, 'Chihuahua', 'CHH'), (492, 'Chiapas', 'CHP'), (491, 'Coahuila', 'COA'), (489, 'Colima', 'COL'), (493, 'Ciudad de México', 'DIF'), (494, 'Durango', 'DUR'), (1388, 'EDOMEX', 'EDOMEX'), (495, 'Guerrero', 'GRO'), (496, 'Guanajuato', 'GUA'), (497, 'Hidalgo', 'HID'), (498, 'Jalisco', 'JAL'), (501, 'México', 'MEX'), (499, 'Michoacán', 'MIC'), (500, 'Morelos', 'MOR'), (502, 'Nayarit', 'NAY'), (503, 'Nuevo León', 'NLE'), (504, 'Oaxaca', 'OAX'), (505, 'Puebla', 'PUE'), (507, 'Querétaro', 'QUE'), (506, 'Quintana Roo', 'ROO'), (508, 'Sinaloa', 'SIN'), (509, 'San Luis Potosí', 'SLP'), (510, 'Sonora', 'SON'), (511, 'Tabasco', 'TAB'), (513, 'Tamaulipas', 'TAM'), (512, 'Tlaxcala', 'TLA'), (514, 'Veracruz', 'VER'), (515, 'Yucatán', 'YUC'), (516, 'Zacatecas', 'ZAC')],
            phone_code=country.phone_code,
            zip_required=country.zip_required,
            state_required=country.state_required,
        )
        _logger.info(dic)
        return dic