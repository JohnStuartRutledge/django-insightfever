from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from guardian.shortcuts import get_perms, assign
from myproject.apps.biz.models import Business
from myproject.models import TimeStamp

FACEBOOK_PERMISSIONS = (
    ('view_facebook', 'view Facebook info'),
)

class Facebook(TimeStamp):
    """ Model for holding Facebook insights info
    friends_of_fans = the total potential reachable audience
    NOTE - according to facebook all daily, weekly and monthly Insights 
           data are aggregated according to PDT (Pacific Daylight Time)
    """
    biz                      = models.ForeignKey(Business)
    date                     = models.DateTimeField(blank=True, null=True)
    lifetime_total_likes     = models.IntegerField(blank=True, null=True)
    daily_new_page_likes     = models.IntegerField(blank=True, null=True)
    daily_page_unlikes       = models.IntegerField(blank=True, null=True)
    friends_of_fans          = models.IntegerField(blank=True, null=True)
    daily_shared_stories     = models.IntegerField(blank=True, null=True)
    weekly_shared_stories    = models.IntegerField(blank=True, null=True)
    monthly_shared_stories   = models.IntegerField(blank=True, null=True)
    daily_engaged_page       = models.IntegerField(blank=True, null=True)
    daily_total_reach        = models.IntegerField(blank=True, null=True)
    weekly_total_reach       = models.IntegerField(blank=True, null=True)
    monthly_total_reach      = models.IntegerField(blank=True, null=True)
    daily_post_impressions   = models.IntegerField(blank=True, null=True)
    weekly_post_impressions  = models.IntegerField(blank=True, null=True)
    monthly_post_impressions = models.IntegerField(blank=True, null=True)
    
    class Meta:
        app_label    = 'social'
        db_table     = u'fever_social_facebook'
        verbose_name = _('facebook insights')
        permissions  = FACEBOOK_PERMISSIONS
    
    def __unicode__(self):
        return "{0}-{1}-{2}".format(self.biz.biz_name, 
            self.created_on.strftime("%y/%m"), self.date)


class FacebookDemographics(TimeStamp):
    '''Model for storing facebook insights demographic data
    '''
    biz = models.ForeignKey(Business)
    date= models.DateTimeField(blank=True, null=True)
    
    # MALES
    M13 = models.IntegerField(blank=True, null=True)
    M18 = models.IntegerField(blank=True, null=True)
    M25 = models.IntegerField(blank=True, null=True)
    M35 = models.IntegerField(blank=True, null=True)
    M45 = models.IntegerField(blank=True, null=True)
    M55 = models.IntegerField(blank=True, null=True)
    
    # FEMALES
    F13 = models.IntegerField(blank=True, null=True)
    F18 = models.IntegerField(blank=True, null=True)
    F25 = models.IntegerField(blank=True, null=True)
    F35 = models.IntegerField(blank=True, null=True)
    F45 = models.IntegerField(blank=True, null=True)
    F55 = models.IntegerField(blank=True, null=True)
    
    # UNKNOWN
    U13 = models.IntegerField(blank=True, null=True)
    U18 = models.IntegerField(blank=True, null=True)
    U25 = models.IntegerField(blank=True, null=True)
    U35 = models.IntegerField(blank=True, null=True)
    U45 = models.IntegerField(blank=True, null=True)
    U55 = models.IntegerField(blank=True, null=True)
    UU  = models.IntegerField(blank=True, null=True)
    
    class Meta:
        app_label    = 'social'
        db_table     = u'fever_social_facebook_demographics'
        verbose_name = _('facebook demographics')
        permissions  = FACEBOOK_PERMISSIONS
    
    def __unicode__(self):
        return "{0}".format(self.biz.biz_name)



class FacebookManagedPages(models.Model):
    ''' Model for saving the data from Facebook API 
    of a users managed pages
    '''
    user         = models.ForeignKey(User, editable=False)
    biz          = models.ForeignKey(Business, blank=True, null=True)
    name         = models.CharField(max_length=100)
    category     = models.CharField(blank=True, null=True, max_length=50, editable=False)
    fbook_uid    = models.CharField(max_length=255, editable=False)
    perms        = models.CharField(max_length=1000, editable=False)
    access_token = models.CharField(max_length=255, editable=False)
    ignored      = models.BooleanField(default=False)

    class Meta:
        app_label    = 'social'
        db_table     = u'fever_social_facebook_pageauth'
        verbose_name = _('Facebook managed page data')
        permissions  = FACEBOOK_PERMISSIONS

    def __uinicode__(self):
        return self.name




