from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.localflavor.us.models import USStateField, PhoneNumberField
from autoslug import AutoSlugField
from taggit.managers import TaggableManager
from guardian.shortcuts import get_perms, assign

from social_auth.fields import JSONField

BUSINESS_TYPES = (
    ('none', ''),
    ('property_manager', _('Property Manager')),
    ('medical',          _('Medical')),
    ('other',            _('Other'))
    )


class Business(models.Model):
    """ Model for holding information about business
    """
    # biz_type = models.CharField(_('business type'),
    #                blank=False, max_length=20, 
    #                choices=BUSINESS_TYPES, default='none',
    #                help_text=_('Select your type of business')),
    biz_name    = models.CharField(_("Name"),      blank=False, max_length=80)
    biz_info    = models.CharField(_("Info"),      blank=True,  null=True, max_length=140)
    biz_email   = models.EmailField(_("Email"),    blank=True,  null=True)
    biz_phone   = PhoneNumberField(_("Phone"),     blank=False, null=True)
    address_1   = models.CharField(_("Address 1"), blank=False, max_length=128)
    address_2   = models.CharField(_("Address 2"), blank=True,  null=True, max_length=128)
    city        = models.CharField(_("City"),      blank=True,  max_length=64)
    state       = USStateField()
    zipcode     = models.CharField(_("Zipcode"),   blank=False, max_length=5)
    members     = models.ManyToManyField(User)
    slug        = AutoSlugField(_("slug"), max_length=255, populate_from="biz_name")
    
    # add the ability to tag the model
    tags = TaggableManager()
    
    class Meta:
        db_table            = u'fever_business'
        verbose_name        = _('Business')
        verbose_name_plural = _("Businesses")
        ordering            = ("biz_name",)

        # django.guardian permissions
        permissions = (
            ('view_business', 'View business info'),
            )
    
    def __unicode__(self):
        return self.biz_name
    
    def tracked_sites(self):
        ''' Return a dict holding the list of tracked and untracked sites
        '''
        d = { 'active':[], 'inactive':[] }
        for x in self.website_set.values():
            if x['site_url']:
                d['active'].append(x['site_type_id'])
            else:
                d['inactive'].append(x['site_type_id'])
        return d


class WebsiteTypes(models.Model):
    ''' Model that holds the types of websites
    TODO
    manage this dynamically from the admin panel
    '''
    WEBSITE_TYPES = (
        ('homepg',     _('Your Home Page')),
        ('homeblog',   _('Your Blog')),
        ('facebook',   _('Facebook')),
        ('twitter',    _('Twitter')),
        ('yelp',       _('Yelp')),
        ('youtube',    _('Youtube')),
        ('aptratings', _('Apartment Ratings')),
        )
        
    site_type = models.CharField(
                    _("Website Type"), blank=False, max_length=30, unique=True)
    
    class Meta:
        db_table            = u'fever_website_types'
        verbose_name        = _('Website Type')
        verbose_name_plural = _("Website types")
    
    def __unicode__(self):
        return self.site_type


class Website(models.Model):
    ''' Model that contains url information about various websites
    '''
    business  = models.ForeignKey(Business)
    site_type = models.ForeignKey(WebsiteTypes, blank=False, null=False, 
                default='my home page')
    site_url  = models.URLField(_("website URL"), blank=False, null=False)
    
    class Meta:
        db_table            = u'fever_websites'
        verbose_name        = _('Website')
        verbose_name_plural = _("Websites")
        ordering            = ("business", "site_url",)
        permissions = (
            ('view_websites',   'View website info'),
            )
    
    def __unicode__(self):
        return '{0} - {1}'.format(str(self.business.biz_name), self.site_type)


