
# settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': '965601',
        'HOST': 'your-rds-endpoint.region.rds.amazonaws.com',
        'PORT': '5432',
    }
}

# For production settings
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com', 'your-eb-env.elasticbeanstalk.com']

# Static files configuration
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Requirements.txt
"""
Django==4.2.10
psycopg2-binary==2.9.9
gunicorn==21.2.0
django-storages==1.14
boto3==1.34.0
"""

# .ebextensions/01_django.config
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: your_project.wsgi:application
  aws:elasticbeanstalk:environment:proxy:staticfiles:
    /static: staticfiles