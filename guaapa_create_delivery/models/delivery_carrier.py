# Copyright 2021 - QUADIT, SA DE CV(https://www.quadit.mx)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

import logging

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    validate = fields.Boolean('Validar desde una lista con C.P.?')
    list_zip = fields.One2many(
        comodel_name='zip.list', 
        inverse_name='delivery_id',
        string='Lista de códigos postales')
    zip_list_count = fields.Integer(string='Destinos', compute='_compute_zip_list_count')

    def _compute_zip_list_count(self):
        self.ensure_one()
        self.zip_list_count = len(self.list_zip.mapped('id'))

    def _match_address(self, partner):
        res = super()._match_address(partner)
        self.ensure_one()
        if self.validate:
            if partner.zip not in self.list_zip.mapped('zip_code'):
                return False
            else:
                return True

        return res