#from django.db.models import signals
#from django.dispatch import receiver
#from djcelery.models import CrontabSchedule, IntervalSchedule, PeriodicTask
#from myproject.apps.likeriser import tasks
#import tasks

from django.db import models
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from guardian.shortcuts import get_perms, assign


import time
from datetime import datetime, timedelta
import pytz
from django.utils import timezone

from myproject.apps.biz.models import Business
from myproject.models import TimeStamp
#from myproject.apps.social.forms import MultiSelectField

# get current timezone
current_tz = timezone.get_current_timezone()

# example of using djangos timezone.now() feature which generates a UTC
# friendly timezone if USE_TZ is set in the settings.py file, else it
# uses just the regular datetime.now()
# foo = timezone.now() + timedelta(minutes=1)

SOCIAL_SITE_CHOICES = (
        ('twitter',  _('Twitter')),
        ('facebook', _('Facebook')),
    )

#-----------------------------------------------------------------------------
# FIELDS
#-----------------------------------------------------------------------------


#-----------------------------------------------------------------------------
# MODELS
#-----------------------------------------------------------------------------

POSTING_PERMISSIONS = (
    ('schedule_social_post', 'Schedule a post on Facebook and Twitter'),
)

class PostQueue(TimeStamp):
    """ Model for holding Apartment Ratings related info
    """
    biz           = models.ForeignKey(Business)
    message       = models.CharField(_("Message"), blank=False, max_length=5000)
    social_sites  = models.CharField(blank=True, null=True, max_length=40)
    #social_sites  = MultiSelectField(max_length=40, blank=True, choices=SOCIAL_SITE_CHOICES)
    post_date     = models.DateTimeField(blank=True, null=True)
    status        = models.CharField(blank=True, null=True, default="active", max_length=20)
    fbook_post_id = models.CharField(blank=True, null=True, max_length=250)
    task_id       = models.CharField(blank=True, null=True, max_length=250)

    class Meta:
        app_label    = 'social'
        db_table     = u'fever_social_post_queue'
        verbose_name = _('Post Queue')
        permissions  = POSTING_PERMISSIONS

    def __unicode__(self):
        return "{0} | {1} | {2}".format(self.biz.biz_name,
            self.post_date.strftime("%y/%m/%d"), self.message)

#-----------------------------------------------------------------------------
# SIGNALS
#-----------------------------------------------------------------------------

'''
@receiver(signals.post_save, sender=PostQueue)
def make_celery_task(sender, **kwargs):
    """ Take the message being saved into the DB and
    create a Celery Task from it.
    """
    msg = kwargs['instance']

    if kwargs['created'] and msg.status == 'active':
        # if the obj is new, marked active, and was just successfully
        # inserted to the DB, then add it to the Celery queue.

        # schedule the post based on date/time or cycle
        if msg.post_date == 'tomorrow':
            eta = datetime.utcnow() + timedelta(days=1)
            # result = some_other_task
        elif msg.post_date == 'next week' or msg.post_date == 'next month':
            # handle cyclical tasks here
            if msg.post_date == 'next week':
                eta = datetime.utcnow() + timedelta(days=7)
            elif msg.post_date == 'next month':
                eta = datetime.utcnow() + timedelta(months=1)
            # result = make_cyclical_task(eta)
        else:

            # check if the date being scheduled is timezone naive
            # and if it is make it timezone aware, else leave it alone
            if timezone.is_naive(msg.post_date):
                eta = timezone.make_aware(msg.post_date, current_tz)
            else:
                eta = msg.post_date

            # NOTE - WebFaction server is set to EST (-0500)

            # add msg to Celery Task Queue
            result = tasks.post_to_site.apply_async(
                        args=[msg.id, msg.message, msg.post_date], eta=eta)


        # add the task_id of the celery task to DB
        msg.task_id = result.task_id
        msg.save()

        # result.ready() # returns true when task is finished processing
        # if the task raises an exception you can access the error traceback
        # via: result.traceback
        if result.successful():
            print 'message was successfully scheduled'
        else:
            # handle errors
            print
            print 'message not successfully scheduled'
            print 'result state = {}'.format(result.state)
            print

    elif kwargs['created'] and msg.status == 'inactive':
        # they just created a new message, but they saved it
        # as a draft, AKA they don't want it added to a task queue
        # TODO - create a 'SAVE AS DRAFT' button that automatically
        # sets msg.status to inactive. This is better than the radio
        # buttons you currently have. You should make it so that if
        # they hit the 'save draft' button that post_date no longer
        # becomes a required field. Also, you should create a drafts
        # section, and add it up there with the other sections you
        # already have (i.e, sent messages, upcoming messages, etc)
        return

    elif not kwargs['created'] and msg.status == 'inactive':
        # deactivate existing message in Celery task queue
        print "DEACTIVATING EXISTING TASK"
        if msg.task_id:
            celery.current_app.revoke(msg.task_id)
        else:
            print 'there is no task_id saved for this post'

    elif not kwargs['created'] and msg.status == 'delete':
        # delete existing task from Celery queue
        print "DELETING EXISTING TASK"
'''

