{
    'name': 'Notion Journal Sync',
    'version': '1.0.0',
    'category': 'Accounting',
    'depends': ['account'],
    'author': 'Your Name',
    'summary': 'Sync journal entries from Notion to Odoo',
    'data': [
        'views/sync_notion_wizard_view.xml',
        'views/sync_notion_button.xml',
        'security/ir.model.access.csv',
        'views/timestamps_accounting.xml',
    ],
    'installable': True,
    'application': False,
}
