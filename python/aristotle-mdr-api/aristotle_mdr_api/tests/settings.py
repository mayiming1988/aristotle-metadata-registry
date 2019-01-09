
import os

ROOT_URLCONF = 'aristotle_mdr_api.tests.urls'

PACKAGE_DIR = os.path.dirname(os.path.dirname(__file__))

STATICFILES_DIRS = [
    os.path.join(PACKAGE_DIR, 'static')
]

STATIC_ROOT = '/tmp/staticfiles'
