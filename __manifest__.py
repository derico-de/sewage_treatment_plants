# -*- coding: utf-8 -*-
{
    'name': "sewage_treatment_plants",

    'summary': """
        Modules for sewage treatment plants""",

    'description': """
        Modules for sewage treatment plants
    """,

    'author': "Maik Derstappen - Derico",
    'website': "http://derico.de",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'fieldservice', 'contract'],

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
}
