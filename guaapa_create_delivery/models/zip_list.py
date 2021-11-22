# Copyright 2021 - QUADIT, SA DE CV(https://www.quadit.mx)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
# -*- coding: utf-8 -*-


from odoo import models, fields, api, exceptions
import logging

_logger = logging.getLogger(__name__)


class zip_list(models.Model):
    _name = "zip.list"

    delivery_id = fields.Many2one('delivery.carrier', 'Delivery id')
    zip_code = fields.Char('Códigos postales')