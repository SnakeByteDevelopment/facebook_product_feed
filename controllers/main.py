import csv
import io
from odoo import http
from odoo.http import request, Response

class FacebookProductFeedController(http.Controller):

    @http.route(['/facebook_feed/<int:website_id>'], type='http', auth='public', website=True)
    def facebook_product_feed(self, website_id, **kwargs):
        """
        CSV-feed voor Facebook met onder meer 'image_link' en 'condition'.
        Route: /facebook_feed/<website_id>?token=<jouw_token>
        """
        # 1. Ophalen van de feedconfig
        feed_config = request.env['facebook.product.feed.config'].sudo().search([
            ('website_id', '=', website_id),
            ('active', '=', True),
        ], limit=1)

        if not feed_config:
            return "Geen actieve Facebook-feedconfig gevonden voor deze website.", 404

        # 2. (Optioneel) token-check
        token = kwargs.get('token')
        if feed_config.feed_token and feed_config.feed_token != token:
            return "Ongeldige token of geen toegang tot deze feed.", 403

        # 3. Producten ophalen

        # Uitgaand van Odoo 15 (voorbeeldcode in controllers/main.py)

        # Uitgaand van Odoo 15 (voorbeeldcode in controllers/main.py)
        
        products = request.env['product.product'].sudo().search([
            ('product_tmpl_id.website_id', '=', website_id),  # of ('product_tmpl_id.website_ids', 'in', website_id)
            ('sale_ok', '=', True),('product_tmpl_id.website_published', '=', True),
        ])
        
        header = [
            'id', 
            'item_group_id',
            'title', 
            'description', 
            'link', 
            'image_link', 
            'availability', 
            'price',
            'condition',
            'color'
            # plus evt. extra kolommen voor variant attributen
        ]

        # 4. CSV genereren
        output = io.StringIO()
        writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        
        writer.writerow(header)
        
        for product in products:
            # 'id' = de unieke variant ID
            product_id = product.id
            
            # 'item_group_id' = het template ID (of een custom code)
            item_group_id = product.product_tmpl_id.id
        
            title = product.product_tmpl_id.name
            description = product.product_tmpl_id.description_sale or ''
        
            # Link naar de productvariantpagina (als actief)
            link = '%s/shop/product/%s' % (feed_config.website_id.domain, product_id)
            
            # Afbeelding: je kunt variantafbeelding pakken (als die er is),
            # anders fallback naar de template-afbeelding.
            image_link = ''
            if product.image_1920:
                image_link = f'{feed_config.website_id.domain}/web/image/product.product/{product.id}/image_1920'
            elif product.product_tmpl_id.image_1920:
                image_link = f'{feed_config.website_id.domain}/web/image/product.template/{product.product_tmpl_id.id}/image_1920'
        
            availability = 'in stock' if product.qty_available > 0 else 'out of stock'

            # Prijs afronden op 2 decimalen
            # Bijvoorbeeld 12.3456 -> 12.35
            price_value = round(product.lst_price, 2)
            # Zorg dat er altijd 2 decimalen getoond worden, ook als het .00 is
            price_str = f"{price_value:.2f} {product.currency_id.name}"
            
            condition = 'new'
        
            # Eventueel extra kolommen voor variant attributen
            # Je zou product.attribute_value_ids kunnen uitlezen:
            # vb.: color, size = None, None
            for value in product.attribute_value_ids:
                if value.attribute_id.name.lower() == 'kleur':
                    color = value.name
            #     if value.attribute_id.name.lower() == 'size':
            #         size = value.name
            # ... en dan ook meeschrijven
        
            writer.writerow([
                product_id,
                item_group_id,
                title,
                description,
                link,
                image_link,
                availability,
                price_str,
                condition,
                color,
                # plus je extra attributen...
            ])
        
        header = [
            'id', 
            'item_group_id',
            'title', 
            'description', 
            'link', 
            'image_link', 
            'availability', 
            'price',
            'condition',
            'color',
            # plus evt. extra kolommen voor variant attributen
        ]
        
        writer.writerow(header)
        
        for product in products:
            # 'id' = de unieke variant ID
            product_id = product.id
            
            # 'item_group_id' = het template ID (of een custom code)
            item_group_id = product.product_tmpl_id.id
        
            title = product.product_tmpl_id.name
            description = product.product_tmpl_id.description_sale or ''
        
            # Link naar de productvariantpagina (als actief)
            link = '%s/shop/product/%s' % (feed_config.website_id.domain, product_id)
            
            # Afbeelding: je kunt variantafbeelding pakken (als die er is),
            # anders fallback naar de template-afbeelding.
            image_link = ''
            if product.image_1920:
                image_link = f'/web/image/product.product/{product.id}/image_1920'
            elif product.product_tmpl_id.image_1920:
                image_link = f'/web/image/product.template/{product.product_tmpl_id.id}/image_1920'
        
            availability = 'in stock' if product.qty_available > 0 else 'out of stock'
            price = f"{product.lst_price} {product.currency_id.name}"
            condition = 'new'
        
            # Eventueel extra kolommen voor variant attributen
            # Je zou product.attribute_value_ids kunnen uitlezen:
            # vb.: color, size = None, None
            # for value in product.attribute_value_ids:
            #     if value.attribute_id.name.lower() == 'color':
            #         color = value.name
            #     if value.attribute_id.name.lower() == 'size':
            #         size = value.name
            # ... en dan ook meeschrijven
        
            writer.writerow([
                product_id,
                item_group_id,
                title,
                description,
                link,
                image_link,
                availability,
                price,
                condition
                # plus je extra attributen...
            ])
        
        csv_data = output.getvalue()
        output.close()

        # 5. Response teruggeven als CSV-bestand
        return Response(
            csv_data,
            headers=[
                ('Content-Disposition', 'attachment; filename="facebook_product_feed.csv"'),
                ('Content-Type', 'text/csv; charset=utf-8')
            ],
            status=200
        )
