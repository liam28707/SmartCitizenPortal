{
    'name': 'Smart Citizen Portal',
    'version': '1.0',
    'summary': 'AI-powered citizen request system',
    'category': 'Government',
    'author': 'ALS',
    'depends': ['base', 'mail'],
    'data': [
        'views/citizen_dashboard_views.xml',
        'views/citizen_category_views.xml',
        'views/citizen_request_views.xml',
        'views/citizen_person_views.xml',
        'views/citizen_menus.xml',
        'security/ir.model.access.csv'
    ],
    'application': True,
}