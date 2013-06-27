
import sys
import djcelery

sys.path.append('.')
djcelery.setup_loader()

BROKER_URL               = 'amqp://'
CELERY_RESULT_BACKEND    = 'amqp://'

CELERY_TASK_SERIALIZER   = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE          = 'America/Chicago'
CELERY_ENABLE_UTC        = True 

# list of modules to import when celery starts
CELERY_IMPORTS = ('tasks',)