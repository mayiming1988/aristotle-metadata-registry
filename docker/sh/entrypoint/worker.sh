set -e # Errors will cause the script to stop
pip install django-impersonate psycopg2 django-improved-user==1.0.0
pip install celery django-celery-results
pip install -e git+https://github.com/harrywhite4/pypandoc#egg=pypandoc
# tail -f /dev/null # If things go wrong use this to get the container up
django-admin check
celery worker --app=aristotle_bg_workers --without-heartbeat