# Django settings for local machine. See the /production/settings.py
# file for the settings file used on the live website.
import os
import sys
sys.path.append('/Users/stu/Envs/dev/webapps/ifever/myproject/myproject/apps/likeriser')

# import and activate Django-Celery
import djcelery
djcelery.setup_loader()

abspath = lambda *x: os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)

WEBAPPS_DIR = '/Users/stu/Envs/dev/webapps'
USE_TZ = True
DEBUG = True
TEMPLATE_DEBUG = DEBUG
INTERNAL_IPS = ("127.0.0.1",)

if DEBUG:
    # Use the Python SMTP debugging server. You can run it with:
    # ``python -m smtpd -n -c DebuggingServer localhost:1025``.
    EMAIL_PORT = 1025

# set Django toolbar configuration options
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

CRISPY_FAIL_SILENTLY = not DEBUG

ADMINS = (
    ('Insight Fever Support', 'stu@mindwink.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default'      : {
        'ENGINE'   : 'django.db.backends.sqlite3',
        'NAME'     : '/Users/stu/Envs/dev/webapps/ifever/myproject/mwink_ifever.db3',
        'USER'     : '',
        'PASSWORD' : '',
        'HOST'     : '',
        'PORT'     : '',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
# MEDIA_ROOT = '/home/mwink/webapps/static_media/'
MEDIA_ROOT = WEBAPPS_DIR + '/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
# MEDIA_URL = 'http://insightfever.com/media/'
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
# STATIC_ROOT = '/home/mwink/webapps/ifever/static/'
STATIC_ROOT = WEBAPPS_DIR + '/static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
#ADMIN_MEDIA_PREFIX = '/admin/'

FIXTURE_DIRS = (
    abspath('fixtures'),
)

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    abspath('static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'h$(0z*6)krv9$g(d8uvmw3zfo&z#^-*ps5!5z@&6^@_sx!okaz'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    #"django_facebook.context_processors.facebook",
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    "myproject.context_processors.get_current_path",
    "social_auth.context_processors.social_auth_by_type_backends",
)

AUTHENTICATION_BACKENDS = (
    #'django_facebook.auth_backends.FacebookBackend',
    'userena.backends.UserenaAuthenticationBackend',
    'guardian.backends.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.google.GoogleOAuth2Backend',
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'myproject.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    abspath('templates'),
)

#sys.path.append(abspath('myproject/apps/likeriser'))
INSTALLED_APPS = (
    'grappelli',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.markup',

    # 3rd party apps
    'easy_thumbnails',
    'guardian',
    'userena',
    'userena.contrib.umessages',
    'crispy_forms',
    'taggit',
    'taggit_templatetags',
    'taggit_suggest',
    'autoslug',
    'knowledge',
    'social_auth',
    'mailchimp',
    'banana_py',
    'djcelery',
    #'south',

    # My apps
    'myproject.templatetags',
    'profiles',
    'biz',
    'reports',
    'social',
    'likeriser',

    # DEBUGGING
    'django_extensions',
    'debug_toolbar',
    'debug_toolbar_user_panel',
)

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar_user_panel.panels.UserPanel',
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)

#Email Server Settings
EMAIL_BACKEND       = 'django.core.mail.backends.dummy.EmailBackend'
DEFAULT_FROM_EMAIL  = ''
EMAIL_HOST          = ''
EMAIL_HOST_USER     = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT          = ''

# Userena settings
AUTH_PROFILE_MODULE         = 'profiles.Profile'
LOGIN_REDIRECT_URL          = '/accounts/%(username)s/'
LOGIN_URL                   = '/accounts/signin/'
LOGOUT_URL                  = '/accounts/signout/'
USERENA_SIGNIN_REDIRECT_URL = '/dashboard/'
USERENA_REDIRECT_ON_SIGNOUT = '/'
USERENA_DIABLE_PROFILE_LIST = True
USERENA_MUGSHOT_SIZE        = 90
USERENA_DEFAULT_PRIVACY     = 'closed'

# Guardian
ANONYMOUS_USER_ID = -1

#-----------------------------------------------------------------------------
# DJANGO-SOCIAL-AUTH SETTINGS / API KEYS
#-----------------------------------------------------------------------------

# http://django-social-auth.readthedocs.org/en/latest/pipeline.html
# pipelines handle the final process of authenticating users.
# this pipeline prevents social-auth from creating new users.
SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details'
)


# Twitter
TWITTER_CONSUMER_KEY    = ''
TWITTER_CONSUMER_SECRET = ''

# Facebook
FACEBOOK_APP_ID         = ''
FACEBOOK_API_SECRET     = ''
FACEBOOK_REDIRECT_URI   = 'http://insightfever.com:8000'
FACEBOOK_EXTENDED_PERMISSIONS = [
    'user_about_me',
    'user_birthday',
    'user_interests',
    'user_likes',
    'user_location',
    'email',
    'read_insights',
    'read_friendlists',
    'read_stream',
    'publish_stream',
    'manage_pages'
]

# https://developers.facebook.com/docs/authentication/permissions/

# Google
GOOGLE_OAUTH2_CLIENT_ID     = ''
GOOGLE_OAUTH2_CLIENT_SECRET = ''

# Mailchimp
MAILCHIMP_API_KEY           = ''
MAILCHIMP_CLIENT_ID         = ''
MAILCHIMP_CLIENT_SECRET     = ''
MAILCHIMP_WEBHOOK_KEY       = '1'
MAILCHIMP_LIST_ID           = '1' # dummy
MAILCHIMP_REDIRECT_URI      = 'http://127.0.0.1:8000/bananas/ripe/'
MAILCHIMP_COMPLETE_URI      = 'http://127.0.0.1:8000/business/accounts/route/'

# Groupon
GROUPON_API_KEY             = ''

# Youtube
YOUTUBE_DEVLOPER_KEY = ''


# Social-auth login URLs
SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = '/business/accounts/route/'
SOCIAL_AUTH_DISCONNECT_REDIRECT_URL      = '/business/accounts/route/'
SOCIAL_AUTH_BACKEND_ERROR_URL            = '/social-login-error/'
SOCIAL_AUTH_RAISE_EXCEPTIONS             = DEBUG
SOCIAL_AUTH_DEFAULT_USERNAME             = 'socialauth_user'

# Social-auth authentication and association URL names to avoid clashes
SOCIAL_AUTH_COMPLETE_URL_NAME  = 'socialauth_complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'socialauth_associate_complete'

#-----------------------------------------------------------------------------
# DJANGO-CELERY
#-----------------------------------------------------------------------------

BROKER_HOST     = "localhost"
BROKER_PORT     = 5672
BROKER_USER     = "guest"
BROKER_PASSWORD = "guest"
BROKER_VHOST    = "/"

BROKER_URL               = 'amqp://guest:guest@localhost:5672/'
BROKER_BACKEND           = 'ampq'
CELERY_RESULT_BACKEND    = 'amqp://'

CELERY_TASK_SERIALIZER   = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE          = 'America/Chicago'
CELERY_ENABLE_UTC        = True
#BROKER_BACKEND = ""
CELERYD_NODES = "w1 w2"

# where to chdir at start.
CELERYD_CHDIR = abspath(os.path.pardir)
CELERYBEAT_CHDIR = abspath(os.path.pardir)

# VIRTUALENV - python interpreter from environment
ENV_PYTHON = "$CELERYD_CHDIR/env/bin/python"

# How to call "manage.py celeryd_multi"
CELERYD_MULTI = "$CELERYD_CHDIR/manage.py celeryd_multi"

# How to call "manage.py celeryctl"
CELERYCTL  = "$CELERYD_CHDIR/manage.py celeryctl"
CELERYBEAT = "$CELERYBEAT_CHDIR/manage.py celerybeat"

# Extra arguments to celeryd
CELERYD_OPTS = "--time-limit=300 --concurrency=8"

# keep celery from disabling your django loggers
CELERYD_HIJACK_ROOT_LOGGER=False

# Name of the celery config module 
# CELERY_CONFIG_MODULE = "celeryconfig"

# %n will be replaced with the nodename.
CELERYD_LOG_FILE   = abspath('logs/celery/w1.log')
CELERYBEAT_LOGFILE = abspath('logs/celery/celeryd.log')


#CELERYD_PID_FILE = "/var/run/celery/%n.pid"

# Workers should run as an unpriviliged user.
CELERYD_USER  = "celery"
CELERYD_GROUP = "celery"

# Name of the projects settings module.
DJANGO_SETTINGS_MODULE = "myproject.settings"

#-----------------------------------------------------------------------------
# LOGGING
#-----------------------------------------------------------------------------
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format':  "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'null': {
            'level':       'DEBUG',
            'class':       'django.utils.log.NullHandler',
            },
        'log_social': {
            'level':       'DEBUG',
            'class':       'logging.handlers.RotatingFileHandler',
            'filename':    os.path.join(abspath('logs'), 'log_social'),
            'maxBytes':    50000,
            'backupCount': 2,
            'formatter':   'standard',
            },
        'console':{
            'level':       'INFO',
            'class':       'logging.StreamHandler',
            'formatter':   'standard'
            },
        'log_reports': {
            'level':       'INFO',
            'class':       'logging.handlers.RotatingFileHandler',
            'filename':    os.path.join(abspath('logs'), 'log_reports'),
            'maxBytes':    50000,
            'formatter':   'standard',
            },
        'log_biz': {
            'level':       'INFO',
            'class':       'logging.handlers.RotatingFileHandler',
            'filename':    os.path.join(abspath('logs'), 'log_biz'),
            'maxBytes':    50000,
            'formatter':   'standard',
            },
    },
    'loggers': {
        'django': {
            'handlers':  ['console'],
            'propagate': True,
            'level':     'WARN',
            },
        'django.db.backends': {
            'handlers':  ['console'],
            'level':     'DEBUG',
            'propagate': False,
            },
        'django.request': {
            'handlers':  ['console'],
            'level':     'ERROR',
            'propagate': True,
            },
        'myproject.apps.social': {
            'handlers': ['console', 'log_social'],
            'level':    'DEBUG',
            },
        'myproject.apps.reports': {
            'handlers': ['console', 'log_reports'],
            'level':    'DEBUG',
            },
        'myproject.apps.biz': {
            'handlers': ['console', 'log_biz'],
            'level':    'DEBUG',
            },
    }
}
