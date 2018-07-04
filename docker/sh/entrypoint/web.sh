gunicorn -b 0.0.0.0:8001 -w 2 wsgi:application --log-file=-
# django-admin runserver 0.0.0.0:8000