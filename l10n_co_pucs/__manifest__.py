# -*- coding: utf-8 -*-
{
    'name': "Colombian Accounting PUC's",

    'summary': """
        Accounting Templates
        """,

    'description': """
        Colombian Pucs. 
        Commercial, Financial and Solidarity Accounting Plans.   
    """,
    'countries': ['co'],
    'version': '0.2',
    'category': 'Accounting/Localizations/Account Charts',
    'author': "CTI Ltda",
    'contributor': 'Carlos Martinez, Rafael Riveros',
    'website': "http://www.cti.com.co",
    'license': 'OPL-1',

    'sequence': 110,
    # any module necessary for this one to work correctly
    'depends': ['l10n_co_account'],
    'auto_install': ['account'],
    # always loaded
    'data': [
        'data/account.group-co_com.csv',
        'data/account.account.tag.csv',
        'data/account_chart_template_data.xml',
        'views/account_fiscal_position_views.xml',
        'views/tax_group.xml',
        'views/tax_view.xml',
        # security

    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
