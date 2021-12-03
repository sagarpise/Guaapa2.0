# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from werkzeug.exceptions import Forbidden, NotFound
from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSaleForm
_logger = logging.getLogger(__name__)

class MyWebsiteSaleForm(WebsiteSaleForm):

    def _get_mandatory_billing_fields(self):
        res = super(WebsiteSaleForm)._get_mandatory_billing_fields()
        res.push("lastname")
        res.push("lastname2")
        return res









