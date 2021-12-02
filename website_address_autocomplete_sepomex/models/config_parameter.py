# -*- coding: utf-8 -*-
# Copyright 2021 - QUADIT, SA DE CV(https://www.quadit.mx)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api

class ConfigParameterInherit(models.Model):
    _inherit = "ir.config_parameter"

    @api.model
    def search_parameter(self, domain=None, fields=None, offset=0, limit=None, order=None):
        return super(ConfigParameterInherit, self).search_read(domain, fields, offset, limit, order)