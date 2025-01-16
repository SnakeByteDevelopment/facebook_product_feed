import csv
import io
from odoo import http
from odoo.http import request, Response

class FacebookProductFeedController(http.Controller):

    @http.route(['/facebook_feed/<int:website_id>'], type='http', auth='public', website=True)
    def facebook_product_feed(self, website_id, **kwargs):
        """
        Voorbeeld-CSV-feed: de route is /facebook_feed/<website_id>
        Eventueel kun je nog een token check toevoegen.
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

        # 3. Producten ophalen die gekoppeld zijn aan de website
        #    Dit kan verschillen per setup. Standaard (website_sale) 
        #    is er een Many2many-relatie in de product.template: website_ids
        #    of je filtert op published='True' voor alleen gepubliceerde producten.
        products = request.env['product.template'].sudo().search([
            ('website_id', '=', website_id),  # Of ('website_ids', 'in', website_id)
            ('sale_ok', '=', True)
        ])

        # 4. CSV genereren
        output = io.StringIO()
        writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        # Facebook vraagt gewoonlijk om kolommen zoals: 
        # id,title,description,link,image_link,availability,price,brand,condition ...
        header = ['id', 'title', 'description', 'link', 'image_link', 'availability', 'price']
        writer.writerow(header)

        for product in products:
            # Een paar voorbeeldwaarden
            product_id = product.id
            title = product.name
            description = product.description_sale or ''
            link = '%s/shop/product/%s' % (feed_config.website_id.domain, product_id)
            # image_link = product.image_1920 and product.website_image_url or ''
	    image_link = ''
	    if product.image_1920:
                image_link = '/web/image/product.template/{}/image_1920/{}'.format(product.id, product.name)

            availability = 'in stock' if product.qty_available > 0 else 'out of stock'
            # Prijs in default valuta (uitgesimplificeerd)
            price = f"{product.list_price} {product.currency_id.name}"

            writer.writerow([
                product_id,
                title,
                description,
                link,
                image_link,
                availability,
                price
            ])

        # 5. Response teruggeven als CSV-bestand
        csv_data = output.getvalue()
        output.close()

        # Stel de juiste headers in
        return Response(
            csv_data,
            headers=[
                ('Content-Disposition', 'attachment; filename="facebook_product_feed.csv"'),
                ('Content-Type', 'text/csv; charset=utf-8')
            ],
            status=200
        )
