# Copyright 2021 - QUADIT, SA DE CV(https://www.quadit.mx)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.http import request
from odoo.exceptions import ValidationError, UserError
import requests
import json
import ssl
import urllib3
import base64
import re

import logging

_logger = logging.getLogger(__name__)

def normalize(s):
    replacements = (
        (" ,", " "),
        (",", " "),
    )
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
    return s

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    guia = fields.Char('Guia del envio', tracking=True, readonly=True) 
    file = fields.Binary('Pdf')

    def send_packages(self):
        url_delivery = self.env['ir.config_parameter'].search([('key','=','guaapa_url_delivery')])
        login = self.env['ir.config_parameter'].search([('key','=','guaapa_user')])
        password = self.env['ir.config_parameter'].search([('key','=','guaapa_password')])
        num_client = self.env['ir.config_parameter'].search([('key','=','guaapa_num_client')])

        for record in self:
        
            if record.guia:
                raise ValidationError('No puedes generar dos guias para el mismo pedido')

            if not login:
                raise ValidationError('[ERROR USUARIO] No puedes generar etiqueta sin antes configurar guaapa_user')

            if not password:
                raise ValidationError('[ERROR PASSWORD] No puedes generar etiqueta sin antes configurar guaapa_password')

            if record.partner_id.l10n_mx_edi_colony == False or record.partner_id.city_id == False:
                raise ValidationError('[ERROR] No puedes generar el envio, colonia y/o ciudad del usuario no ingresadas en la ficha del contacto')


            if record.location_dest_id.usage == 'customer':
                if url_delivery:
                    peso = 0
                    volumen = 0

                    for lines in record.move_line_ids:
                        peso = peso + lines.product_id.weight
                        volumen = volumen + pow(lines.product_id.volume, 3)
                    
                    ids = []

                    if not record.move_line_ids_without_package:
                        raise UserError(_('No puedes hacer un envio vacío'))

                    for measures in record.move_line_ids_without_package:
                        #if measures.result_package_id.packaging_id:
                        #    raise UserError(_('Tu paquete no contiene el tipo de paquete'))
                        if measures.result_package_id.packaging_id.height:
                            alto = measures.result_package_id.packaging_id.height
                        else: 
                            raise UserError(_('Tu paquete no contine alto'))
                        if measures.result_package_id.packaging_id.width:
                            ancho = measures.result_package_id.packaging_id.width
                        else: 
                            raise UserError(_('Tu paquete no contine ancho'))
                        if measures.result_package_id.packaging_id.packaging_length:
                            largo = measures.result_package_id.packaging_id.packaging_length    
                        else: 
                            raise UserError(_('Tu paquete no contine ancho'))
                        
                        ids.append(measures.result_package_id.id)

                    a_set = set(ids)
                    number_of_unique_values = len(a_set)

                    print(number_of_unique_values)

                    if number_of_unique_values > 1:
                        cantidad = number_of_unique_values
                        esmultiple = True

                    else:
                        cantidad = 1
                        esmultiple = False


                    contact_id = self.env['res.partner'].search([('id','=',1)])
                    address_id = self.env['res.partner'].search([('name','=', 'Ricardo Mejía')])
                    
                    if record.partner_id.parent_id:
                        public = record.partner_id.parent_id.name
                    else:
                        public = "Público en general"

                    headers = {'content-type': 'application/json'}

                    if not record.partner_id.street_number:
                        raise UserError(_('Falta la calle!'))

                    if not record.partner_id.vat:
                        raise UserError(_('Falta RFC!'))
                    if not record.partner_id.name:
                        raise UserError(_('Falta Nombre del contacto!'))
                    if not record.partner_id.phone:
                        raise UserError(_('Falta Teléfono!'))
                    if not record.partner_id.street_name:
                        raise UserError(_('Falta Calle!'))
                    if not record.partner_id.street_number:
                        raise UserError(_('Falta Número Exterior!'))

                    if not record.partner_id.zip:
                        raise UserError(_('Falta Código Postal!'))
                    if not record.partner_id.l10n_mx_edi_colony:
                        raise UserError(_('Falta Colonia!'))
                    if not record.partner_id.city and not record.partner_id.city_id:
                        raise UserError(_('Falta Ciudad!'))
                    if not record.partner_id.state_id.name:
                        raise UserError(_('Falta Estado!'))
                    if not record.partner_id.email:
                        if not record.partner_id.parent_id:
                            raise UserError(_('Falta eMail!'))
                        if not record.partner_id.parent_id.email:
                            raise UserError(_('Falta eMail!'))                    
                        else:
                            email_des = record.partner_id.parent_id.email
                    else:
                           email_des = record.partner_id.email
                    
                    if record.partner_id.city_id:
                        city = record.partner_id.city_id.name
                    else:
                        city = record.partner_id.city

                    if record.partner_id.street_number2:
                        num_int = re.sub('[^0-9a-zA-Z ]+', ' ', record.partner_id.street_number2)
                    else:
                        num_int = " "


                    body = {
                        "login" : login.value,
                        "password" : password.value,
                        "numcliente" : num_client.value,
                        "idmensajeria" : "AUTODOCWEB",
                        "idservicio" : "20",
                        "observaciones" : "OBSERVACION",
                        "referencia" : record.name,
                        "factura" : None,
                        "remitente" : {
                            "claveCliente" : None,
                            "razonsocial" : "Guaapa ventas y servicios",
                            "contacto" : "Logística Guaapa",
                            "telefono" : contact_id.phone.replace(" ", "")[-10:],
                            "calle" : address_id.street_name[:29],

                            "numinterior" : re.sub('[^0-9a-zA-Z ]+', ' ', address_id.street_number),
                            "numexterior" : re.sub('[^0-9a-zA-Z ]+', ' ', address_id.street_number2),

                            "entreCalles" : None,
                            "referencia" : None,
                            "codigoPostal" : contact_id.zip,
                            "colonia" : address_id.l10n_mx_edi_colony,
                            "ciudad" : address_id.city_id.name,
                            "estado" : address_id.state_id.name,
                            "idestado" : None,
                            "pais" : None,
                            "idpais" : None,
                            "email" : contact_id.email,
                            "convenio" : None
                        },
                        "destinatario" : {
                            "claveCliente" : None,
                            "razonsocial" : public,
                            "contacto" : normalize(record.partner_id.name),
                            "telefono" : record.partner_id.phone.replace(" ", "")[-10:],
                            "calle" : record.partner_id.street_name[:29],
                            "numinterior" : num_int,
                            "numexterior" : re.sub('[^0-9a-zA-Z ]+', ' ', record.partner_id.street_number),
                            "entreCalles" : None,
                            "referencia" : None,
                            "codigoPostal" : record.partner_id.zip,
                            "colonia" : record.partner_id.l10n_mx_edi_colony,
                            "ciudad" : city,
                            "estado" : record.partner_id.state_id.name,
                            "idestado" : None,
                            "pais" : "MEXICO",
                            "idpais" : None,
                            "email" : email_des,
                            "convenio" : None
                        },
                        "detalleEnvio" : None,
                        "paquete" : {
                            "paqueteID" : "P",
                            "cantidad" : cantidad,
                            "alto" : alto,
                            "ancho" : ancho,
                            "largo" : largo,
                            "peso" : peso,
                            "valor" : 0.0,
                            "tipoMercancia" : "MERCANCIA",
                            "tipoEmpaque" : "P",
                            "descripcionMercancia" : "CONTENIDO",
                            "factura" : None,
                            "asegurarlo" : False,
                            "esmultiple" : esmultiple,
                            "volumen" : volumen
                        }
                    }


                    _logger.warning("Body => %r" % body)


                    envio = requests.post(url_delivery.value , headers=headers, json=body)
                    _logger.warning("Estatus de la conexion")
                    _logger.warning("Status CODE => %r" % envio.status_code)
                    _logger.warning("Status JSON => %r" % envio.json)
                    _logger.warning("Status TEXT => %r" % envio.text)

                    informacion = json.loads(envio.text)

                    if informacion['codigo'] == "DATOS DE ACCESO INVALIDOS":
                        raise ValidationError('[ERROR] DATOS DE ACCESO INVALIDOS')
                    if informacion['codigo'] == "300":
                        raise ValidationError('[ERROR] ERROR EN SISTEMA')
                    if informacion['codigo'] == "400":
                        raise ValidationError('[ERROR] %r' % informacion['mensaje'])
                    if informacion['codigo'] == "0":
                        guia = informacion['guia']
                        _logger.warning("Guia => %r" % guia)
                        record.guia = guia
                        pdf = informacion['pdf']
                        record.file = pdf

                        attachment = self.env['ir.attachment'].create({
                            'name': record.name,
                            'type': 'binary',
                            'res_id': record.id,
                            'res_model': 'stock.picking',
                            'datas': record.file,
                            'mimetype': 'application/pdf',
                        })
                        id = [attachment.id]
                        self.message_post(body="Etiqueta", attachment_ids=id)
                        self.transferido = True
                else:
                    raise ValidationError('No puedes generar una guia sin definir la url destino')
            else:
                raise ValidationError('No puedes enviar por paqueteria si no existe una ubicacion del cliente')

    @api.model
    def consultar_tracking(self):
        guias = self.env['stock.picking'].search([('guia','!=',None)])
        url_consult_delivery = self.env['ir.config_parameter'].search([('key','=','guaapa_url_check_delivery')])
        login = self.env['ir.config_parameter'].search([('key','=','guaapa_user')])
        password = self.env['ir.config_parameter'].search([('key','=','guaapa_password')])
        num_client = self.env['ir.config_parameter'].search([('key','=','guaapa_num_client')])

        if not login:
            raise exceptions.ValidationError('[ERROR USUARIO] No puedes consultar etiqueta sin antes configurar guaapa_user')

        if not password:
            raise exceptions.ValidationError('[ERROR PASSWORD] No puedes consultar etiqueta sin antes configurar guaapa_password')
        
        if url_consult_delivery:
            for guia in guias:
                headers = {'content-type': 'application/json'}

                body = {
                        "login" : login.value,
                        "password" : password.value,
                        "numcliente": num_client.value,
                        "idmensajeria": "AUTODOCWEB",
                        "numeroguia": guia.guia 
                }

                _logger.warning("Body %r" % body)
                
                envio = requests.post(url_consult_delivery.value, headers=headers, json=body)
                
                _logger.warning("Estatus de la conexion")
                _logger.warning("Status CODE => %r" % envio.reason)
                _logger.warning("Status JSON => %r" % envio.json)
                _logger.warning("Status TEXT => %r" % envio.text)
                
        else:
            raise exceptions.ValidationError('No puedes generar consultas sin definir la url destino')
