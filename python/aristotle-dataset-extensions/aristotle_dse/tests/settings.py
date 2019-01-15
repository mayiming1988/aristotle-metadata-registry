from aristotle_mdr.tests.settings.settings import *

INSTALLED_APPS = (
    # The good stuff
    'aristotle_dse',
) + INSTALLED_APPS

ARISTOTLE_SETTINGS['CONTENT_EXTENSIONS'] = ['aristotle_dse', 'aristotle_mdr_links']

ROOT_URLCONF = 'aristotle_dse.tests.urls'
