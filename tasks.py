# from django.core.cache import cache 
from djcelery.models import PeriodicTask, IntervalSchedule, CrontabSchedule
from django.conf import settings
from celery import Celery
from celery.task import Task, PeriodicTask  
from celery.result import AsyncResult 
from celery.schedules import crontab
from celery.utils.log import get_task_logger
import celeryconfig

from datetime import datetime, timedelta

log = get_task_logger(__name__)

celery = Celery('tasks', backend='amqp', broker='amqp://')

# to use the config file uncomment the following line
# celery.config_from_object('celeryconfig')

# make sure celery is added to your PYTHONPATH (in your bash_rc)
# export PYTHONPATH=$PYTHONPATH:/path/to/celeryconfig

# run celery with:
# >>> celeryd --loglevel=INFO

#-----------------------------------------------------------------------------
# TASKS 
#-----------------------------------------------------------------------------

@celery.task(name='tasks.post_to_site')
def post_to_site(msg_id, msg_message, msg_post_date):
    ''' Task that takes a PostQueue object, extracts
    the message and posttime, and posts to Facebook/Twitter 
    EXAMPLE DATE: 2012-09-04 20:30:00
    '''
    current_task_id = post_to_site.request.id
    log.info('message_{}[{}]:{}'.format(
        msg_id, msg_post_date, msg_message))
    return msg_message


@celery.task
def post_to_facebook(msg_id, msg_message, msg_post_date):
    ''' Task that takes the variables in a PostQueue object
    and posts its content to Facebook at the scheduled time.
    '''
    pass


@celery.task
def post_to_twitter(msg_id, msg_message, msg_post_date):
    ''' Task that takes the variables in a PostQueue object
    and posts its content to Twitter at the scheduled time.
    '''
    try:
        # connect to twitter
        pass
    except:
        # except specific twitter errors
        pass
    pass


@celery.task 
def verify_task(task_id):
    result = AsyncResult(task_id)
    if result.read():
        # do_something_with(result.get())
        pass
    else:
        verify_task.retry(countdown=1)


def make_weekly_task(hour, minute, day_of_week):
    ''' Construct a task meant to execute at specific time each week 
    hour        - digit without leading zero representing the hour to post 
    minute      - digit without leading zero representing the min to post 
    day_of_week - 3 character abbreviation of the week to post on 

    EXAMPLE:
        make_weekly_task(7, 30, 'mon')
    ''' 
    @periodic_task(run_every=crontab(
        hour=hour, minute=minute, day_of_week=day_of_week))
    def every_monday_morning():
        print("This is run every Monday morning at 7:30")


#-----------------------------------------------------------------------------
# Scheduled Message/Post 
#-----------------------------------------------------------------------------


class MessageTask(Task):
    ''' Class for sending a message
    EXAMPLE USE:
        @task(base=MessageTask)
        def mytask():
            pass
    '''
    abstract = True
    def __call__(self, *args, **kwargs):
        # before running the task, check the DB to see if the
        # task is active or not, if inactive then cancel it
        if self.msg.status == 'inactive':
            return

        #if revoke_flag_set_in_db_for(self.request.id):
        #    return
        super(MessageTask, self).__call__(*args, **kwargs)
        #return self.run(*args, **kwargs)

    def on_success(self, retval, task_id, args, kwargs):
        # http://celery.readthedocs.org/en/latest/userguide/tasks.html#on_success
        pass

    def on_faliure(self, exc, task_id, args, kwargs, einfo):
        # http://celery.readthedocs.org/en/latest/userguide/tasks.html#on_failure
        pass

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        # http://celery.readthedocs.org/en/latest/userguide/tasks.html#on_retry
        pass

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        # http://celery.readthedocs.org/en/latest/userguide/tasks.html#after_return
        print('Task returned: %r' % (self.request, ))

    def send_message(self):
        ''' Send a facebook/twitter message at the exact moment
        a user scheduled it to be sent
        '''
        pass

    def cancel_message(self):
        ''' remove the scheduled message from the queue
        '''
        pass

    def update_message_status(self):
        ''' use this to update the status of the message 
        states are: sent, pending, paused, deleted, error 
        '''
        pass


