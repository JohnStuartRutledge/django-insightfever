from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from guardian.shortcuts import get_perms, assign
from myproject.apps.biz.models import Business
from myproject.models import TimeStamp

YELP_PERMISSIONS = (
    ('view_yelp',   'view Yelp info'),
)

class Yelp(TimeStamp):
    """ Model for holding Yelp info
    """
    biz          = models.ForeignKey(Business)
    stars        = models.FloatField(blank=True, null=True)
    review_count = models.IntegerField(default=0)
    scraped_on   = models.DateTimeField(null=True)
    
    class Meta:
        app_label    = 'social'
        db_table     = u'fever_social_yelp'
        verbose_name = _('Yelp')
        permissions  = YELP_PERMISSIONS
    
    def __unicode__(self):
        return self.biz.biz_name


class YelpSimilar(TimeStamp):
    '''Model for holding Yelp similar Businesses
    '''
    biz                  = models.ForeignKey(Business)
    similar_name         = models.CharField(max_length=60)
    similar_link         = models.URLField(blank=True, null=True)
    similar_stars        = models.FloatField(blank=True, null=True)
    similar_neighborhood = models.CharField(max_length=60, blank=True, null=True)
    scraped_on           = models.DateTimeField(null=True)
    
    class Meta:
        app_label    = 'social'
        db_table     = u'fever_social_yelp_similar'
        verbose_name = _('Yelp Similar Businesses')
        permissions  = YELP_PERMISSIONS
    
    def __unicode__(self):
        return "%s" % (self.similar_name)


"""
class YelpReviews(TimeStamp):
    '''Model for holding individual Yelp reviews
    '''
    biz           = models.ForeignKey(Business)
    reviewer_name = models.CharField(_('reviewer name'), max_length=60)
    date_posted   = models.DateField(_('date posted'), unique=True)
    stars         = models.FloatField(_('stars'))
    review_link   = models.URLField(_('review link'))
    friend_count  = models.IntegerField(_('friend count'))
    review_count  = models.IntegerField(_('review count'))
    photo_count   = models.IntegerField(_('photo count'))
    checkin_count = models.IntegerField(_('checkin count'))
    useful_count  = models.IntegerField(_('useful count'))
    funny_count   = models.IntegerField(_('funny count'))
    cool_count    = models.IntegerField(_('cool count'))
    message       = models.TextField(_('message'))
    
    class Meta:
        app_label    = 'social'
        db_table = u'fever_social_yelp_reviews'
        verbose_name = _('Yelp Reviews')
        permissions  = YELP_PERMISSIONS
    
    def __unicode__(self):
        return self.reviewer_name


class YelpUpdates(TimeStamp):
    '''Rather than use this class, it might be better to simply
    use the YelpReviews class above, and create some kind of
    oneToOne or ManyToMany field that is self referrential.
    AKA if the scraper detects an update in the review, then
    it will insert a new row in the YelpReviews table, but
    that row will reference its earlier incarnation via a lookup
    table. That way you can create a timeline of changes.
    NOTE - lookup a better way to do this.
    '''
    biz           = models.ForeignKey(Business)
    review        = models.ForeignKeyField(YelpReviews)
    date_posted   = models.DateField()
    stars         = models.FloatField(  blank=True, null=True)
    friend_count  = models.IntegerField(blank=True, null=True)
    review_count  = models.IntegerField(blank=True, null=True)
    photo_count   = models.IntegerField(blank=True, null=True)
    checkin_count = models.IntegerField(blank=True, null=True)
    useful_count  = models.IntegerField(blank=True, null=True)
    funny_count   = models.IntegerField(blank=True, null=True)
    cool_count    = models.IntegerField(blank=True, null=True)
    message       = models.TextField(   blank=True, null=True)
    
    class Meta:
        app_label    = 'social'
        db_table = u'fever_social_yelp_updates'
        verbose_name = _('Yelp Updates')
        permissions  = YELP_PERMISSIONS
    
    def __unicode__(self):
        return self.reply_id


"""




