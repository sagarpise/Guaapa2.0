# -*- coding: utf-8 -*-
# Copyright 2021 - QUADIT, SA DE CV(https://www.quadit.mx)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import http
from odoo.http import request
from odoo.http import content_disposition, Controller, request, route
from odoo.addons.portal.controllers.portal import CustomerPortal

class CustomerPortalCity(CustomerPortal):
    MANDATORY_BILLING_FIELDS = ["name", "phone", "email", "street", "city", "country_id"]
    OPTIONAL_BILLING_FIELDS = ["zip", "state_id", "vat", "company_name", "city_id"]

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
            post.update({'state_id': int(post['state_id'])})
            #only sepomex
            post.update({'city_id': int(post['city_id'])})
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

