# -*- coding: utf-8 -*-
{
    'name': "Colombian Accounting",

    'summary': """
        Ciiu
        Documnet Type & Verification Digit
        ReteIca""",

    'description': """
        Pucs, Taxes (including ICA and Retention by uvt) and fiscal position (Account & Taxes Maps based in Origin and Destiny). 
        Dian or Regularories Codes including fiscal responsibility & cities and ciiu.
        Magnetic media & Certification    
    """,

    'author': "CTI Ltda",
    'contributor': 'Carlos Martinez, Wilfredo Moreno, Rafael Riveros',
    'website': "http://www.cti.com.co",
    'category': 'Localization',
    'version': '0.1',
    'license': 'OPL-1',

    'sequence': 110,
    # any module necessary for this one to work correctly
    'depends': ['base','account','l10n_latam_base','l10n_co','account_debit_note', 'l10n_co_dian'
    ],

    # always loaded
    'data': [
#        'data/account.group.csv',
        'data/account.account.tag.csv',
#        'data/account.account-co.csv',
#        'data/account_batch_payment_data.xml',
        'data/payment.option.csv',
#        'data/res_groups.xml',
#        'data/account.fiscal.position-co.csv',
#        'views/chart_account_apply_view.xml',
#        'views/account_journal_view.xml',
#        'views/edi_resolution.xml',
#        'views/fiscal_responsibility_view.xml',
###      'views/company_view.xml',
        'views/partner_view.xml',
        'views/product_view.xml',
        'views/account_view.xml',
        'data/account_reports.xml',
        'views/res_company_view.xml',
#        'views/res_partner_view.xml'
        'wizard/retention_views.xml',
#        'report/certification_templates.xml',
        # NACIONALES
        'data/1001.xml',
        'data/1003.xml',
        'data/1004.xml',
        'data/1005.xml',
        'data/1006.xml',
        'data/1007.xml',
        'data/1008.xml',
        'data/1009.xml',
        'data/1010.xml',
        'data/1011.xml',
        'data/1012.xml',
        'data/2276.xml',
        # DISTRITALES
        'data/art_2.xml',
        'data/art_4.xml',
        'data/art_6.xml',

        'data/magnetic.media.lines.csv',
        'data/magnetic.media.lines.concepts.csv',
        # views
        'views/magnetic_media.xml',
        #        'views/account_invoice_view.xml',

        # security
        'security/ir.model.access.csv',

        # data
        'data/res.bank.csv',
#        'data/res.city.zip.csv',
        'data/res.partner.industry.csv',
        'data/account.ciiu.csv',
        # views
        'views/account_ciiu_view.xml',

    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
