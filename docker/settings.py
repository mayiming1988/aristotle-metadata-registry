"""
Base settings necessary for running an Aristotle Instance in "the cloud (tm)"
"""

import dj_database_url
from aristotle_mdr.required_settings import *

ALLOWED_HOSTS = ["*"]
DEBUG = True
ARISTOTLE_SETTINGS['SITE_NAME'] = 'Aristotle Development Server'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_DIR = os.path.join(BASE_DIR, 'static')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
ARISTOTLE_ASYNC_SIGNALS = False
INSTALLED_APPS = list(INSTALLED_APPS)+['aristotle_mdr.contrib.links','aristotle_dse','aristotle_glossary']
ROOT_URLCONF = 'urls'
ARISTOTLE_SETTINGS['CONTENT_EXTENSIONS'] = ARISTOTLE_SETTINGS['CONTENT_EXTENSIONS']+['aristotle_mdr_links','aristotle_dse','aristotle_glossary']

MIDDLEWARE = ['whitenoise.middleware.WhiteNoiseMiddleware'] + MIDDLEWARE
DATABASES = {'default': dj_database_url.config()}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db',
        'PORT': '5432',
    }
}

CACHES= {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis/0',
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack_elasticsearch.elasticsearch5.Elasticsearch5SearchEngine',
        'URL': 'http://elasticsearch:9200',
        'INDEX_NAME': 'documents',
        'INCLUDE_SPELLING': True,
        'KWARGS': {
            'http_auth': 'elastic:changeme'
        }
    }
}

CELERY_BROKER_URL = 'redis://redis/1'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TASK_TRACK_STARTED = True

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

CKEDITOR_CONFIGS = {
    'default': {
        #'toolbar': 'full',
        'toolbar' : [
            { 'name': 'clipboard', 'items': [ 'Cut', 'Copy', 'Paste', 'PasteText', '-', 'Undo', 'Redo' ] },
            { 'name': 'basicstyles', 'items' : [ 'Bold','Italic','Subscript','Superscript','-','RemoveFormat' ] },
            { 'name': 'links', 'items' : [ 'Link','Unlink' ] },
	        { 'name': 'paragraph', 'items' : [ 'NumberedList','BulletedList','-','Blockquote' ] },
    	    { 'name': 'insert', 'items' : [ 'Image','Table','HorizontalRule','SpecialChar'] },
            { 'name': 'aristotletoolbar', 'items': [ 'Glossary' ] },
            { 'name': 'document', 'items': [ 'Maximize','Source' ] },
        ],
        'extraPlugins' : 'aristotle_glossary',
    },
}