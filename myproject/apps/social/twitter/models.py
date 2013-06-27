from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from guardian.shortcuts import get_perms, assign
from myproject.apps.biz.models import Business
from myproject.models import TimeStamp

TWITTER_PERMISSIONS = (
    ('view_twitter', 'view Twitter info'),
)

class Twitter(models.Model):
    """ Model for holding Twitter info
    """
    #slug = AutoSlugField(_("slug"), max_length=50, populate_from="biz_name")
    biz       = models.ForeignKey(Business)
    tweets    = models.IntegerField()
    following = models.IntegerField()
    followers = models.IntegerField()
    listed    = models.IntegerField()
    
    class Meta:
        app_label    = 'social'
        db_table     = u'fever_twitter'
        verbose_name = _('Twitter')
        # django.guardian permissions
        permissions  = TWITTER_PERMISSIONS
    
    def __unicode__(self):
        return self.biz.biz_name


class Tweets(models.Model):
    '''Model for holding individual tweets
    '''
    biz         = models.ForeignKey(Business)
    message     = models.CharField(max_length=140)
    date_posted = models.DateField()
    
    class Meta:
        app_label    = 'social'
        db_table     = u'fever_twitter_tweets'
        verbose_name = _('Tweets')
        permissions  = TWITTER_PERMISSIONS
    
    def __unicode__(self):
        return "%s" % (self.biz.biz_name)


class Followers(models.Model):
    '''Model for holding Twitter followers
    '''
    biz           = models.ForeignKey(Business)
    follower_name = models.CharField(null=False, max_length=60)
    
    class Meta:
        app_label    = 'social'
        db_table     = u'fever_twitter_followers'
        verbose_name = _('Twitter Followers')
        permissions  = TWITTER_PERMISSIONS
    
    def __unicode__(self):
        return self.biz.biz_name



