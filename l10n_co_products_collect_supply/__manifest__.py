# -*- coding: utf-8 -*-
{
    'name': "Product Collect & Supply",

    'summary': """
        Module that allows to register collect of the same product to several
        suppliers in a simple form and supplies management
    """,

    'description': """
        Module that allows to register collect of the same product to several
        suppliers in a simple form and supplies management
    """,

    'author': "CTI Ltda",
    'website': "http://www.cti.com.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Operations/Purchase/inventory/Deliver',
    'version': '0.1',
    'license': 'OPL-1',

    # any module necessary for this one to work correctly
    'depends': ['base','account', 'purchase', 'stock_landed_costs', 'stock_picking_batch','sale_stock','sale_renting'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'reports/purchase_line_pivot.xml',
        'data/sequence.xml',
        'reports/product_collect_templates.xml',
        'reports/product_collect_reports.xml',
        'views/data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
