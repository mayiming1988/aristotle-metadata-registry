"""
Base settings necessary for running an Aristotle Instance in "the cloud (tm)"
"""

import dj_database_url
from aristotle_mdr.required_settings import *

ALLOWED_HOSTS = ["*"]
DEBUG = os.environ.get('DEBUG_TOOLBAR', False)
ARISTOTLE_SETTINGS['SITE_NAME'] = 'Aristotle Development Server'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_DIR = os.path.join(BASE_DIR, 'static')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
] + MIDDLEWARE + [
    'impersonate.middleware.ImpersonateMiddleware'
]
DATABASES = {'default': dj_database_url.config()}

INSTALLED_APPS = ['impersonate']+list(INSTALLED_APPS)
ROOT_URLCONF = 'urls'


LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

# Debug toolbar
import socket
DEBUG_TOOLBAR = os.environ.get('DEBUG_TOOLBAR', False)
if DEBUG and DEBUG_TOOLBAR:
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    INSTALLED_APPS += ('debug_toolbar',)
    ip = socket.gethostbyname(socket.gethostname())
    INTERNAL_IPS = [ip[:-1] + '1']
