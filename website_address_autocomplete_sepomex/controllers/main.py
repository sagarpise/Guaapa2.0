# -*- coding: utf-8 -*-
# Copyright 2021 - QUADIT, SA DE CV(https://www.quadit.mx)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import logging

from odoo import http, SUPERUSER_ID
from odoo.http import request
import requests
import json

_logger = logging.getLogger(__name__)

class WebsiteAddress(http.Controller):

    @http.route('/sepomex', auth='public', method=['GET'], cors='*')
    def search_info(self, **kw):
        
        url_sepomex = request.env['ir.config_parameter'].sudo().search([('key','=','url_sepomex')]).value
        key_sepomex = request.env['ir.config_parameter'].sudo().search([('key','=','key_sepomex')]).value
        url_copomex = request.env['ir.config_parameter'].sudo().search([('key','=','url_copomex')]).value
        key_copomex = request.env['ir.config_parameter'].sudo().search([('key','=','key_copomex')]).value
        
        if url_sepomex and key_sepomex:
            _logger.info("{0}/zipcode?zipcode={1}&token={2}".format(url_sepomex, kw.get('zipcode'), key_sepomex))
            data = requests.post("{0}/zipcode?zipcode={1}&token={2}".format(url_sepomex, kw.get('zipcode'), key_sepomex))
            _logger.info(data.text)
            res_data = (json.loads(data.text)[0])
        else: 
            if url_copomex and key_copomex:
                _logger.info("{0}/info_cp/{1}?type=simplified&token={2}".format(url_copomex, kw.get('zipcode'), key_copomex))
                data = requests.post("{0}/info_cp/{1}?type=simplified&token={2}".format(url_copomex, kw.get('zipcode'), key_copomex))
                _logger.info(data.text)
                res_data = (json.loads(data.text))
        _logger.info(res_data)
        return json.dumps(res_data)

    @http.route('/get-cities', auth='public', method=['GET'], cors='*')
    def get_cities(self, **kw):
        cities = request.env['res.city'].sudo().search_read([('name','ilike',kw.get('municipio')),('state_id','=',int(kw.get('state_id')))])
        d = dict()
        d['id'] = cities[0]['id']
        d['name'] = cities[0]['name']
        return json.dumps(d)