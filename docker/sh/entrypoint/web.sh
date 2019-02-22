set -e # Errors will cause the script to stop
# tail -f /dev/null # If things go wrong use this to get the container up
# pip install django-impersonate psycopg2 django-improved-user==1.0.0 dj-database-url
gunicorn wsgi:application -b 0.0.0.0:8000 -w 2 --log-file=- --access-logfile=- --log-level debug --reload
