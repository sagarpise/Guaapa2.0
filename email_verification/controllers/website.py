# -*- coding: utf-8 -*-

from odoo import api, http, _
from odoo.http import request
from odoo.addons.portal.controllers.web import Home

class Website(Home):
    @http.route(website=True, auth="public", sitemap=False)
    def web_login(self, redirect=None, *args, **kw):
        response = super(Website, self).web_login(redirect=redirect, *args, **kw)
        if not redirect and request.params['login_success']:
            login_user = request.env['res.users'].browse(request.uid)
            if login_user.has_group('base.group_user'):
                redirect = b'/web?' + request.httprequest.query_string
            else:
                if not login_user.wk_token_verified:
                    redirect = '/web/welcome'
                else:
                    redirect = '/'
            return http.redirect_with_hash(redirect)
        return response
