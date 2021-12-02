# -*- coding: utf-8 -*-
# Copyright 2021 - QUADIT, SA DE CV(https://www.quadit.mx)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api

class ResCityInherit(models.Model):
    _inherit = "res.city"

    @api.model
    def search_cities(self, domain=None, fields=None, offset=0, limit=None, order=None):
        return super(ResCityInherit, self).sudo().search_read(domain, fields, offset, limit, order)