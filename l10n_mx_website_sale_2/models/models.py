# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api
from .. import exceptions

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    invoice_data = fields.Boolean(string="Do you want to invoice?",required=False,default=False)
    references= fields.Text(string="References",required=False)
