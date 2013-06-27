'''
from django.db.models import signals
from django.dispatch import receiver
from djcelery.models import CrontabSchedule, IntervalSchedule, PeriodicTask
#from myproject.apps.social.posts.models import PostQueue
from myproject.apps.likeriser.tasks import post_to_site

#-----------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------

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
            eta = msg.post_date
            # add msg to Celery Task Queue
            result = post_to_site.apply_async(msg, eta=eta)

        # add the task_id of the celery task to DB
        #msg.task_id = result.task_id
        #msg.save()

        if result.successful():
            print 'message was successfully sent'
        else:
            # handle errors
            print 'message not successfully sent yet'
            print 'result state = {}'.format(result.state)

    elif kwargs['create'] and msg.status == 'inactive':
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


"""
# get a task from Celery Task Queue
result = MyTask.AsyncResult(task_id)

# return the contents of that task
fbook_response = result.get()

# check fbook response for errors
if 'error' in fbook_response:
    handle_errors(fbook_response)



"""
'''
