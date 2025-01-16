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
        products = request.env['product.template'].sudo().search([
            ('website_id', '=', website_id),  # pas aan indien nodig (vb: ('website_ids', 'in', website_id))
            ('sale_ok', '=', True)
        ])

        # 4. CSV genereren
        output = io.StringIO()
        writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        # Uitgebreide header (Facebook-velden)
        header = [
            'id', 
            'title', 
            'description', 
            'link', 
            'image_link', 
            'availability', 
            'price',
            'condition'  # Nieuw veld
        ]
        writer.writerow(header)

        for product in products:
            product_id = product.id
            title = product.name or ''
            description = product.description_sale or ''
            link = '%s/shop/product/%s' % (feed_config.website_id.domain, product_id)

            # Nieuw: we genereren zelf de afbeelding-URL
            # (zorg dat je site publiek toegankelijk is)
            image_link = ''
            if product.image_1920:
                # Eventueel kun je ook de domeinnaam erbij zetten, bijvoorbeeld:
                # image_link = '%s/web/image/product.template/%s/image_1920' % (
                #     feed_config.website_id.domain, product_id
                # )
                image_link = '/web/image/product.template/%s/image_1920' % (product_id)

            availability = 'in stock' if product.qty_available > 0 else 'out of stock'
            price = f"{product.list_price} {product.currency_id.name}"

            # Nieuw: condition-veld toevoegen (hard-coded 'new', of pas dit aan)
            condition = 'new'

            writer.writerow([
                product_id,
                title,
                description,
                link,
                image_link,
                availability,
                price,
                condition
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
