from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from guardian.shortcuts import get_perms, assign
from myproject.apps.biz.models import Business
from myproject.models import TimeStamp

CRAIGSLIST_PERMISSIONS = (
    ('view_craigslist', 'view Craigslist info'),
)

class Craigslist(models.Model):
    """ Model for holding Craigslist info
    """
    biz         = models.ForeignKey(Business)
    post_id     = models.IntegerField()
    post_url    = models.URLField()
    price       = models.FloatField()
    bedrooms    = models.CharField()
    description = models.TextField()
    
    class Meta:
        app_label    = 'social'
        db_table     = u'fever_craigslist'
        verbose_name = _('Craigslist Item')
        
        # django.guardian permissions
        permissions = CRAIGSLIST_PERMISSIONS
    
    def __unicode__(self):
        return self.biz.biz_name







