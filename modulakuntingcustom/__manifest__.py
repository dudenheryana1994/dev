# -*- coding: utf-8 -*-
{
    'name': "User Management Kreasi",

    'summary': "Management User",

    'description': """
Untuk proses Pencatatan, mengolah, dan menyajikan data karyawan, serta berbagai kegiatan yang berhubungan dengan karyawan
    """,

    'author': "PT Kreasi",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'web'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/ir.model.access.csv',
        'views/user.xml',
        'views/usage.xml',
        #'views/templatess.xml',
        #'views/templates.xml',
    ],
    #'images': [ #
        #'static/description/odoo1.png'],#
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
