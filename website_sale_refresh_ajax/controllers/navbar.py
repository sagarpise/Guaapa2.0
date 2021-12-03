# -*- coding: utf-8 -*-
# Copyright 2021 - QUADIT, SA DE CV(https://www.quadit.mx)
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import http
from odoo.http import request
from datetime import datetime
from odoo import fields, http, SUPERUSER_ID, tools, _

_logger = logging.getLogger(__name__)


class NavbarShopCart(http.Controller):

    @http.route(['/navbar/shop/cart/update'], type='json', auth="public", website=True, csrf=False)
    def cart_update(self, **kw):
        order = []
        order.append(request.website.sale_get_order().cart_quantity)
        order.append(request.website.sale_get_order().amount_total)
        order.append(request.env['ir.ui.view']._render_template("website_sale.cart", {
            'website_sale_order': request.website.sale_get_order(),
            'date': fields.Date.today(),
            'suggested_products': request.website.sale_get_order()._cart_accessories()
        }))
        order.append(request.env['ir.ui.view']._render_template("website_sale.short_cart_summary", {
            'website_sale_order': request.website.sale_get_order(),
        }))
        return order
