from odoo import models, fields


class Website(models.Model):
    _inherit = "website"

    hotjar_active = fields.Boolean()
    hotjar_script = fields.Text()


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    hotjar_active = fields.Boolean(related='website_id.hotjar_active', readonly=False)
    hotjar_script = fields.Text(related='website_id.hotjar_script', readonly=False)
