# Copyright 2021 - QUADIT, SA DE CV(https://www.quadit.mx)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)

class res_partner(models.Model):
    _inherit = "res.partner"

    @api.model
    def create(self, vals):
        _logger.info("Vals %r" % vals)
        if 'vat' in vals:
            if vals['vat']:
                _logger.info("vat %r" % vals['vat'])
            else:
                vals['vat'] = 'XAXX010101000'
        rec = super(res_partner, self).create(vals)
	    
        return rec