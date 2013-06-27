from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from userena.models import UserenaBaseProfile

class Profile(UserenaBaseProfile):
    ''' Default profile 
    '''
    user     = models.OneToOneField(User, unique=True,
                    verbose_name='user', related_name='profile')
    facebook = models.CharField(
                    _('facebook'), max_length=75, blank=True, null=True)
    twitter  = models.CharField(
                    _('twitter'),  max_length=20, blank=True, null=True)
    
    def __unicode__(self):
        return "%s" % (self.user)

