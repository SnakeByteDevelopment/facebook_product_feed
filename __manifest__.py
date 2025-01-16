{
    'name': 'Facebook Product Feed',
    'version': '15.0.1.0.0',
    'category': 'Website',
    'summary': 'Genereer een productfeed per Odoo-website voor Facebook.',
    'author': 'Jouw Naam',
    'website': 'https://www.jouw-bedrijf.nl',
    'license': 'LGPL-3',
    'depends': ['website', 'sale'],  # of 'website_sale' als je de eCommerce wilt gebruiken
    'data': [
        'security/ir.model.access.csv',
        'views/feed_config_view.xml',
    ],
    'installable': True,
    'application': False,
}
