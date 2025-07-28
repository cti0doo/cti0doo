{
    'name': 'L10n_co_loans',
    'description': """
Loans upgrade
=================
loan term unit in years or months and scheduled payment up to balance <= 0
    """,
    'author': "CTI Ltda",
    'contributor': 'Juan Sebastian Castiblanco, Rafael Riveros',
    'category': 'Accounting/Accounting',
    'sequence': 32,
    'depends': ['account_loans'],
    'data': [
        'wizard/loan_compute_wizard.xml',

    ],
    'license': 'OEEL-1',
    'auto_install': False,
}
