# -*- coding: utf-8 -*-
# Copyright 2021 - QUADIT, SA DE CV(https://www.quadit.mx)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models

class CountryState(models.Model):
    _inherit = "res.country.state"

    city_ids = fields.One2many("res.city", "state_id")

    def get_website_sale_cities(self, mode="billing"):
        return self.sudo().city_ids
