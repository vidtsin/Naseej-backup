# -*- coding: utf-8 -*-
{
    'name': "naseej_inv_f2",

    'version': '1.0',
    'summary': 'Nassej Project',
    'description': """  
    """,

    'author': "Nassej",
    'category': 'Nassej Project',
    'website': 'http://www.git-eg.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock','purchase', 'sale_management','point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 10,
    'application': True,


}