from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from guardian.shortcuts import get_perms, assign
from myproject.apps.biz.models import Business
from myproject.models import TimeStamp

APTRATINGS_PERMISSIONS = (
    ('view_aptratings', 'view Apartment Ratings info'),
)

class Apt(TimeStamp):
    """ Model for holding Apartment Ratings related info
    """
    #slug = AutoSlugField(_("slug"), max_length=50, populate_from="biz_name")
    # models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    biz                  = models.ForeignKey(Business)
    recommended_by       = models.IntegerField()
    total_overall_rating = models.FloatField(blank=True, null=True)
    overall_parking      = models.FloatField(blank=True, null=True)
    overall_maintenance  = models.FloatField(blank=True, null=True)
    overall_construction = models.FloatField(blank=True, null=True)
    overall_noise        = models.FloatField(blank=True, null=True)
    overall_grounds      = models.FloatField(blank=True, null=True)
    overall_safety       = models.FloatField(blank=True, null=True)
    overall_office_staff = models.FloatField(blank=True, null=True)
    scraped_on           = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        app_label    = 'social'
        db_table     = u'fever_social_apt_totals'
        verbose_name = _('Apartment Ratings')
        permissions  = APTRATINGS_PERMISSIONS
    
    def __unicode__(self):
        return "{0}-{1}-{2}".format(self.biz.biz_name, 
            self.created_on.strftime("%y/%m"), self.total_overall_rating)


class AptComments(TimeStamp):
    '''Model for holding Apartment Ratings Comments
    '''
    biz                  = models.ForeignKey(Business)
    comment_title        = models.CharField(max_length=200, blank=True, null=True)
    comment_username     = models.CharField(max_length=60,  blank=True, null=True)
    comment_years_stayed = models.CharField(max_length=50,  blank=True, null=True)
    comment_message      = models.TextField(blank=True, null=True)
    scraped_on           = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        app_label           = 'social'
        db_table            = u'fever_social_apt_comments'
        verbose_name        = _('Apartment Ratings Comment')
        verbose_name_plural = _('Apartment Ratings Comments')
        permissions         = APTRATINGS_PERMISSIONS
    
    def __unicode__(self):
        return "{0} - {1}".format(str(self.comment_id), self.comment_title)


class AptRatings(TimeStamp):
    '''Model for holding an individual rating page
    '''
    biz            = models.ForeignKey(Business)
    comment        = models.ForeignKey(AptComments)
    overall_rating = models.FloatField(blank=True, null=True)
    parking        = models.FloatField(blank=True, null=True)
    maintenance    = models.FloatField(blank=True, null=True)
    construction   = models.FloatField(blank=True, null=True)
    noise          = models.FloatField(blank=True, null=True)
    grounds        = models.FloatField(blank=True, null=True)
    safety         = models.FloatField(blank=True, null=True)
    office_staff   = models.FloatField(blank=True, null=True)
    scraped_on     = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        app_label           = 'social'
        db_table            = u'fever_social_apt_ratings'
        verbose_name        = _('Apartment Ratings Rating')
        verbose_name_plural = _('Apartment Ratings Ratings')
        permissions         = APTRATINGS_PERMISSIONS
    
    def __unicode__(self):
        return "{0}".format(str(self.comment_id))


class AptReplies(TimeStamp):
    biz          = models.ForeignKey(Business)
    comment      = models.ForeignKey(AptComments)
    reply_number = models.IntegerField(null=False)
    reply_name   = models.CharField(max_length=120, blank=True, null=True)
    reply_date   = models.DateTimeField(blank=True, null=True)
    reply_msg    = models.TextField(blank=True, null=True)
    scraped_on   = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        app_label           = 'social'
        db_table            = u'fever_social_apt_replies'
        verbose_name        = _('Apartment Ratings Reply')
        verbose_name_plural = _('Apartment Ratings Replies')
        permissions         = APTRATINGS_PERMISSIONS
    
    def __unicode__(self):
        return "reply_id:{0}, comment_id:{1}".format(
                str(self.reply_id), str(self.comment.id))






