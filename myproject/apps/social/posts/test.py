import json
from datetime import datetime

from django.test import TestCase
from django.test.client import Client

from django.contrib.auth.models import User
from myproject.apps.social.models import PostQueue
from myproject.apps.biz.models import Business, Website, WebsiteTypes
from myproject.apps.social.forms import PostQueueForm



class SimpleTest(TestCase):
    ''' Testing the PostQueue
    '''
    def setUp(self):
        self.user = User.objects.create(username="stu")
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        PostQueue.objects.create(
            biz=1,
            message="This is a test message",
            social_sites="[u'facebook']",
            post_date=self.date,
            status="active",
            fbook_post_id="",
            task_id=""
            )
        self.client = Client()

    def testIfCorrectJsonResponse(self):
        # define test url here
        # url = urllib.urlencode('http://www.reddit.com')
        response = self.client.get("/social/1/post/json/?url=TEST").content
        expected = {'url': 'TEST'}
        self.assertEquals(response, expected)


#-----------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------
'''
expected = """[
{
    "pk": 1,
    "model": "myproject.apps.social.PostQueue",
    "fields": {
        "biz": 1,
        "message": "This is a test message",
        "social_sites": "[u'facebook']",
        "post_date": "%s",
        "status": "active",
        "facebook_post_id": "",
        "task_id": ""
    }
}]""" % (self.date, )

expected = " ".join(expected.split())

'''
