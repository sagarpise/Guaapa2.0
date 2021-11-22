# -*- coding: utf-8 -*-


from odoo import models, fields, api, exceptions
import logging
import time
import datetime

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
	_inherit = 'stock.picking'

	flag_validation = fields.Boolean('Validación')
	transferido = fields.Boolean('Transferido')
	sends_ids = fields.One2many('reg.stock', 'user_id', 'Movimientos')
	
	@api.model
	def exportar_pedidos_pendientes(self):
		pickings_ids = self.env['stock.picking'].search([('flag_validation','=',True),('transferido','!=',True)])
		_logger.info("pickings_ids => %r" % pickings_ids)
		
		data = []

		for picking in pickings_ids:
			products_move_list = [{'Nombre_del_producto': p.product_id.name, 'Cantidad': p.product_qty, 'Tamanio': p.product_id.weight, 'Volumen': p.product_id.volume, 'Material': p.product_id.material} for p in picking.move_ids_without_package]
			
			data.append({
				"Cliente": picking.partner_id.name,
				"Fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
				"Documento": picking.origin,
				"Productos": products_move_list})

			_logger.info("informacion que viaja atraves de POST => %r" % data)
			_logger.info("Entra")
			
			create_reg = self.env['reg.stock'].create({
				'user_id': self.env.user.id,
				'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
				'id_albaran': picking.id
			})

		_logger.info("Se creo el registro => %r" % create_reg)

		return data

class reg_stock(models.Model):
	_name = 'reg.stock'
	_description = "Module for stock movements"

	user_id = fields.Many2one('res.users','Resposable')
	date = fields.Char('Fecha')
	id_albaran = fields.Many2one('stock.picking', 'Albaran')