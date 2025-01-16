from odoo import api, fields, models

class FacebookProductFeedConfig(models.Model):
    _name = 'facebook.product.feed.config'
    _description = 'Facebook Product Feed Config per Website'

    name = fields.Char(string='Naam', required=True, help="Naam van deze feedconfiguratie")
    website_id = fields.Many2one(
        'website', 
        string='Website', 
        required=True,
        help="Website waarvoor de feed geldt."
    )
    active = fields.Boolean(default=True, string='Actief')
    feed_token = fields.Char(
        string='Feed Token', 
        help="Optionele token om de feed-URL te beveiligen."
    )

    # Voorbeeld: als je bijvoorbeeld extra parameters wilt
    # feed_currency_id = fields.Many2one('res.currency', string='Feed Currency')

    @api.model
    def create(self, vals):
        # Eventueel logica toevoegen bij aanmaken van een record
        return super().create(vals)
